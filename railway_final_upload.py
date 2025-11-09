#!/usr/bin/env python3
"""
Railway'e Final Upload - Temiz SQL dosyalarıyla
"""

import psycopg2
import re
from datetime import datetime

class C:
    G = '\033[92m'; Y = '\033[93m'; R = '\033[91m'; B = '\033[94m'; E = '\033[0m'

def log(msg, c=C.B):
    print(f"{c}[{datetime.now().strftime('%H:%M:%S')}] {msg}{C.E}")

def clean_sql(sql_content):
    """SQL içeriğini temizle - sadece geçerli SQL komutlarını al"""
    # Yorumları kaldır
    lines = []
    for line in sql_content.split('\n'):
        # \restrict gibi psql özel komutlarını atla
        if line.strip().startswith('\\'):
            continue
        # -- yorumlarını koru ama boş satırları atla
        if line.strip() and not line.strip().startswith('--'):
            lines.append(line)
        elif line.strip().startswith('--'):
            lines.append(line)
    
    return '\n'.join(lines)

def main():
    log("🚀 Railway Final Upload Başlıyor...", C.G)
    
    railway_url = "postgresql://postgres:kJQQiRoGKGgWRPWGsRrSdKRoMogEVAGy@shinkansen.proxy.rlwy.net:27699/railway"
    
    try:
        # Bağlan
        log("1️⃣ Railway'e bağlanılıyor...", C.Y)
        conn = psycopg2.connect(railway_url)
        conn.autocommit = True
        cursor = conn.cursor()
        log("✓ Bağlantı başarılı", C.G)
        
        # Temizle
        log("2️⃣ Database temizleniyor...", C.Y)
        cursor.execute("DROP SCHEMA IF EXISTS public CASCADE")
        cursor.execute("CREATE SCHEMA public")
        cursor.execute("GRANT ALL ON SCHEMA public TO postgres")
        cursor.execute("GRANT ALL ON SCHEMA public TO public")
        log("✓ Database temizlendi", C.G)
        
        # Schema yükle
        log("3️⃣ Schema yükleniyor...", C.Y)
        with open('railway_schema_final.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        schema_sql = clean_sql(schema_sql)
        
        try:
            cursor.execute(schema_sql)
            log("✓ Schema yüklendi", C.G)
        except Exception as e:
            log(f"⚠️  Schema yükleme hatası: {str(e)[:100]}", C.Y)
            # Devam et, bazı hatalar normal olabilir
        
        # Data yükle
        log("4️⃣ Data yükleniyor...", C.Y)
        with open('railway_data_final.sql', 'r', encoding='utf-8') as f:
            data_sql = f.read()
        
        data_sql = clean_sql(data_sql)
        
        # INSERT'leri ayır
        inserts = []
        current = []
        
        for line in data_sql.split('\n'):
            if line.strip():
                current.append(line)
                if line.strip().endswith(';'):
                    inserts.append('\n'.join(current))
                    current = []
        
        total = len(inserts)
        success = 0
        errors = 0
        
        log(f"  Toplam {total} INSERT komutu bulundu", C.B)
        
        for i, insert in enumerate(inserts, 1):
            if i % 100 == 0:
                log(f"  İşleniyor: {i}/{total} ({success} başarılı, {errors} hata)", C.B)
            
            try:
                cursor.execute(insert)
                success += 1
            except Exception as e:
                errors += 1
                error_msg = str(e).lower()
                if 'duplicate' not in error_msg and 'already exists' not in error_msg:
                    if errors <= 5:  # İlk 5 hatayı göster
                        log(f"  ⚠️  Hata {errors}: {str(e)[:80]}", C.Y)
        
        log(f"✓ Data yüklendi: {success} başarılı, {errors} hata", C.G)
        
        # Doğrulama
        log("5️⃣ Doğrulama...", C.Y)
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [t[0] for t in cursor.fetchall()]
        
        log(f"✓ {len(tables)} tablo oluşturuldu:", C.G)
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                log(f"  • {table}: {count} kayıt", C.B)
            except:
                log(f"  • {table}: Sayım yapılamadı", C.Y)
        
        cursor.close()
        conn.close()
        
        log("", C.G)
        log("🎉 Transfer tamamlandı!", C.G)
        log("🌐 https://minibar.erkanerdem.net", C.B)
        
        return True
        
    except Exception as e:
        log(f"❌ Hata: {e}", C.R)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
