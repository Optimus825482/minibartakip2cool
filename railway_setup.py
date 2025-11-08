#!/usr/bin/env python3
"""
Railway Environment Variables Setup Script
"""

import subprocess
import sys

# Environment variables
ENV_VARS = {
    'DATABASE_URL': 'postgresql://postgres:NEOcbkYOOSzROELtJEuVZxdPphGLIXnx@shinkansen.proxy.rlwy.net:36747/railway',
    'SECRET_KEY': '8f3a9b2c7d1e6f4a5b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a',
    'FLASK_ENV': 'production',
    'ENV': 'production',
    'DB_TYPE': 'postgresql'
}

def check_railway_cli():
    """Railway CLI kurulu mu kontrol et"""
    try:
        # Windows'ta railway.cmd veya railway.exe olabilir
        result = subprocess.run(['railway', '--version'], 
                              capture_output=True, 
                              text=True,
                              shell=True)  # Windows için shell=True
        return result.returncode == 0
    except Exception:
        return False

def set_variable(key, value):
    """Railway'de environment variable ayarla"""
    try:
        cmd = f'railway variables --set "{key}={value}"'
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True,
                              shell=True,  # Windows için shell=True
                              check=True)
        print(f"✅ {key} ayarlandı")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {key} ayarlanamadı: {e.stderr}")
        return False

def main():
    print("=" * 60)
    print("RAILWAY ENVIRONMENT VARIABLES SETUP")
    print("=" * 60)
    print()
    
    # Railway CLI kontrolü
    if not check_railway_cli():
        print("❌ Railway CLI bulunamadı!")
        print()
        print("Kurulum için:")
        print("  npm install -g @railway/cli")
        print()
        sys.exit(1)
    
    print("✅ Railway CLI bulundu")
    print()
    
    # Login kontrolü
    print("🔐 Railway'e giriş yapılıyor...")
    try:
        subprocess.run('railway login', shell=True, check=True)
        print("✅ Giriş başarılı")
    except subprocess.CalledProcessError:
        print("❌ Giriş başarısız")
        sys.exit(1)
    
    print()
    print("📝 Environment variables ayarlanıyor...")
    print()
    
    # Variables'ları ayarla
    success_count = 0
    for i, (key, value) in enumerate(ENV_VARS.items(), 1):
        print(f"[{i}/{len(ENV_VARS)}] {key}...", end=" ")
        if set_variable(key, value):
            success_count += 1
    
    print()
    print("=" * 60)
    if success_count == len(ENV_VARS):
        print("🎉 TÜM VARIABLES BAŞARIYLA AYARLANDI!")
    else:
        print(f"⚠️  {success_count}/{len(ENV_VARS)} variable ayarlandı")
    print("=" * 60)
    print()
    
    # Kontrol
    print("📊 Mevcut variables:")
    try:
        subprocess.run('railway variables', shell=True, check=True)
    except subprocess.CalledProcessError:
        pass
    
    print()
    print("🚀 Deploy için:")
    print("  railway up")
    print()

if __name__ == '__main__':
    main()
