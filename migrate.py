#!/usr/bin/env python3
"""
MySQL'den PostgreSQL'e minibar_takip veritabanı taşıma scripti
Erkan için hazırlanmıştır
"""

import mysql.connector
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
from datetime import datetime, date
from decimal import Decimal

# Bağlantı bilgileri
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'minibar',
    'password': '518518Erkan',
    'database': 'minibar_takip'
}

POSTGRES_CONFIG = {
    'host': '127.0.0.1',  # localhost yerine 127.0.0.1 kullan (IPv4 zorla)
    'port': 5432,
    'user': 'postgres',
    'password': '518518Erkan',
    'database': 'minibar_takip'
}

# MySQL veri tiplerini PostgreSQL'e dönüştürme
def mysql_to_postgres_type(mysql_type):
    """MySQL veri tipini PostgreSQL karşılığına çevirir"""
    type_map = {
        'tinyint(1)': 'BOOLEAN',
        'tinyint': 'SMALLINT',
        'smallint': 'SMALLINT',
        'mediumint': 'INTEGER',
        'int': 'INTEGER',
        'bigint': 'BIGINT',
        'float': 'REAL',
        'double': 'DOUBLE PRECISION',
        'decimal': 'NUMERIC',
        'date': 'DATE',
        'datetime': 'TIMESTAMP',
        'timestamp': 'TIMESTAMP',
        'time': 'TIME',
        'year': 'INTEGER',
        'char': 'CHAR',
        'varchar': 'VARCHAR',
        'text': 'TEXT',
        'tinytext': 'TEXT',
        'mediumtext': 'TEXT',
        'longtext': 'TEXT',
        'blob': 'BYTEA',
        'tinyblob': 'BYTEA',
        'mediumblob': 'BYTEA',
        'longblob': 'BYTEA',
        'enum': 'VARCHAR',
        'set': 'VARCHAR',
        'json': 'JSONB'
    }
    
    mysql_type_lower = mysql_type.lower()
    
    for key, value in type_map.items():
        if mysql_type_lower.startswith(key):
            if key in ['char', 'varchar', 'decimal']:
                return mysql_type.upper().replace('VARCHAR', 'VARCHAR').replace('CHAR', 'CHAR')
            return value
    
    return 'TEXT'

def get_table_structure(mysql_cursor, table_name):
    """MySQL tablosunun yapısını alır"""
    mysql_cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
    create_table = mysql_cursor.fetchone()[1]
    
    mysql_cursor.execute(f"DESCRIBE `{table_name}`")
    columns = mysql_cursor.fetchall()
    
    return columns, create_table

def create_postgres_table(pg_cursor, table_name, columns):
    """PostgreSQL'de tablo oluşturur"""
    
    # Önce varsa tabloyu sil
    pg_cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
    
    # Sütun tanımlarını oluştur
    column_defs = []
    primary_keys = []
    
    for col in columns:
        col_name = col[0]
        col_type = col[1]
        is_nullable = col[2] == 'YES'
        col_key = col[3]
        col_default = col[4]
        col_extra = col[5]
        
        # PostgreSQL tipi
        pg_type = mysql_to_postgres_type(col_type)
        
        # Sütun tanımı
        col_def = f'"{col_name}" {pg_type}'
        
        # AUTO_INCREMENT -> SERIAL
        if 'auto_increment' in col_extra.lower():
            if 'bigint' in col_type.lower():
                col_def = f'"{col_name}" BIGSERIAL'
            else:
                col_def = f'"{col_name}" SERIAL'
        
        # NOT NULL
        if not is_nullable:
            col_def += ' NOT NULL'
        
        # DEFAULT değer
        if col_default is not None and 'auto_increment' not in col_extra.lower():
            if col_default.upper() == 'CURRENT_TIMESTAMP':
                col_def += ' DEFAULT CURRENT_TIMESTAMP'
            elif col_default.upper() == 'NULL':
                pass
            else:
                col_def += f" DEFAULT {col_default}"
        
        column_defs.append(col_def)
        
        # Primary key
        if col_key == 'PRI':
            primary_keys.append(col_name)
    
    # CREATE TABLE ifadesi
    create_sql = f'CREATE TABLE "{table_name}" (\n  '
    create_sql += ',\n  '.join(column_defs)
    
    # Primary key ekle
    if primary_keys:
        pk_cols = '", "'.join(primary_keys)
        create_sql += f',\n  PRIMARY KEY ("{pk_cols}")'
    
    create_sql += '\n)'
    
    print(f"\nTablo oluşturuluyor: {table_name}")
    print(f"SQL: {create_sql[:200]}...")
    
    pg_cursor.execute(create_sql)

def convert_value(value):
    """MySQL değerini PostgreSQL'e uygun formata çevirir"""
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, bytes):
        return value
    return value

def copy_table_data(mysql_cursor, pg_cursor, table_name, columns):
    """Tablo verilerini kopyalar"""
    
    # Tüm verileri al
    mysql_cursor.execute(f"SELECT * FROM `{table_name}`")
    rows = mysql_cursor.fetchall()
    
    if not rows:
        print(f"  {table_name}: Veri yok")
        return 0
    
    # Sütun isimlerini ve tiplerini al
    col_names = [col[0] for col in columns]
    col_types = [col[1].lower() for col in columns]
    
    # Boolean sütunları belirle (TINYINT(1))
    boolean_indices = [i for i, col_type in enumerate(col_types) if col_type == 'tinyint(1)']
    
    # INSERT sorgusu hazırla
    placeholders = ','.join(['%s'] * len(col_names))
    col_names_str = '", "'.join(col_names)
    insert_sql = f'INSERT INTO "{table_name}" ("{col_names_str}") VALUES ({placeholders})'
    
    # Verileri toplu ekle
    converted_rows = []
    for row in rows:
        converted_row = []
        for i, val in enumerate(row):
            # Boolean sütunlarını özel olarak işle
            if i in boolean_indices and val is not None:
                converted_row.append(bool(val))
            else:
                converted_row.append(convert_value(val))
        converted_rows.append(tuple(converted_row))
    
    # Batch insert
    batch_size = 1000
    total_inserted = 0
    
    for i in range(0, len(converted_rows), batch_size):
        batch = converted_rows[i:i+batch_size]
        pg_cursor.executemany(insert_sql, batch)
        total_inserted += len(batch)
        print(f"  {table_name}: {total_inserted}/{len(converted_rows)} kayıt aktarıldı", end='\r')
    
    print(f"  {table_name}: {total_inserted} kayıt aktarıldı ✓")
    return total_inserted

def create_indexes_and_constraints(mysql_cursor, pg_cursor, table_name):
    """Index'leri ve foreign key'leri oluşturur"""
    
    # Index'leri al
    mysql_cursor.execute(f"SHOW INDEX FROM `{table_name}`")
    indexes = mysql_cursor.fetchall()
    
    created_indexes = set()
    
    for idx in indexes:
        index_name = idx[2]
        column_name = idx[4]
        non_unique = idx[1]
        
        # PRIMARY ve AUTO_INCREMENT index'lerini atla
        if index_name == 'PRIMARY' or index_name in created_indexes:
            continue
        
        try:
            if non_unique == 0:  # UNIQUE index
                pg_cursor.execute(f'CREATE UNIQUE INDEX "{index_name}" ON "{table_name}" ("{column_name}")')
            else:  # Normal index
                pg_cursor.execute(f'CREATE INDEX "{index_name}" ON "{table_name}" ("{column_name}")')
            created_indexes.add(index_name)
            print(f"  Index oluşturuldu: {index_name}")
        except Exception as e:
            print(f"  Index oluşturulamadı ({index_name}): {e}")

def main():
    """Ana fonksiyon"""
    print("=" * 70)
    print("MySQL'den PostgreSQL'e Veritabanı Taşıma Scripti")
    print("Veritabanı: minibar_takip")
    print("=" * 70)
    
    mysql_conn = None
    pg_conn = None
    
    try:
        # MySQL bağlantısı
        print("\n[1/6] MySQL'e bağlanılıyor...")
        mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
        mysql_cursor = mysql_conn.cursor()
        print("✓ MySQL bağlantısı başarılı")
        
        # PostgreSQL bağlantısı (veritabanı olmadan)
        print("\n[2/6] PostgreSQL'e bağlanılıyor...")
        pg_config = POSTGRES_CONFIG.copy()
        db_name = pg_config.pop('database')
        
        pg_conn = psycopg2.connect(**pg_config)
        pg_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        pg_cursor = pg_conn.cursor()
        print("✓ PostgreSQL bağlantısı başarılı")
        
        # Veritabanı oluştur
        print(f"\n[3/6] PostgreSQL'de '{db_name}' veritabanı oluşturuluyor...")
        try:
            pg_cursor.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
            pg_cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✓ '{db_name}' veritabanı oluşturuldu")
        except Exception as e:
            print(f"! Veritabanı zaten var veya oluşturulamadı: {e}")
        
        # Yeni veritabanına bağlan
        pg_cursor.close()
        pg_conn.close()
        
        pg_config['database'] = db_name
        pg_conn = psycopg2.connect(**pg_config)
        pg_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        pg_cursor = pg_conn.cursor()
        
        # Tabloları al
        print("\n[4/6] MySQL tabloları listeleniyor...")
        mysql_cursor.execute("SHOW TABLES")
        tables = [table[0] for table in mysql_cursor.fetchall()]
        print(f"✓ {len(tables)} tablo bulundu: {', '.join(tables)}")
        
        # Her tablo için
        print("\n[5/6] Tablolar ve veriler aktarılıyor...")
        total_records = 0
        
        for table_name in tables:
            try:
                # Tablo yapısını al
                columns, create_table = get_table_structure(mysql_cursor, table_name)
                
                # PostgreSQL'de tablo oluştur
                create_postgres_table(pg_cursor, table_name, columns)
                pg_conn.commit()
                
                # Verileri kopyala
                records = copy_table_data(mysql_cursor, pg_cursor, table_name, columns)
                pg_conn.commit()
                total_records += records
                
            except Exception as e:
                print(f"✗ HATA ({table_name}): {e}")
                pg_conn.rollback()
                import traceback
                traceback.print_exc()
        
        # Index ve constraint'leri oluştur
        print("\n[6/6] Index'ler oluşturuluyor...")
        for table_name in tables:
            try:
                create_indexes_and_constraints(mysql_cursor, pg_cursor, table_name)
                pg_conn.commit()
            except Exception as e:
                print(f"  Index hatası ({table_name}): {e}")
        
        # Özet
        print("\n" + "=" * 70)
        print("TAŞIMA TAMAMLANDI!")
        print("=" * 70)
        print(f"Toplam tablo sayısı: {len(tables)}")
        print(f"Toplam kayıt sayısı: {total_records:,}")
        print(f"Hedef veritabanı: {db_name}")
        print("=" * 70)
        
    except mysql.connector.Error as e:
        print(f"\n✗ MySQL HATASI: {e}")
        sys.exit(1)
    except psycopg2.Error as e:
        print(f"\n✗ PostgreSQL HATASI: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ GENEL HATA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if mysql_conn:
            mysql_cursor.close()
            mysql_conn.close()
            print("\nMySQL bağlantısı kapatıldı")
        if pg_conn:
            pg_cursor.close()
            pg_conn.close()
            print("PostgreSQL bağlantısı kapatıldı")

if __name__ == "__main__":
    main()