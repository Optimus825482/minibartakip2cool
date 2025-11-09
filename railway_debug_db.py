#!/usr/bin/env python3
"""
Railway Database Debug Script
Environment variables ve bağlantıyı debug eder
"""

import os
import sys

def main():
    print("=" * 60)
    print("🔍 RAILWAY DATABASE DEBUG")
    print("=" * 60)
    print()
    
    # Environment variables kontrol
    print("📋 Environment Variables:")
    print("-" * 60)
    
    env_vars = [
        'DATABASE_URL',
        'PGHOST',
        'PGUSER',
        'PGPASSWORD',
        'PGDATABASE',
        'PGPORT',
        'PORT',
        'SECRET_KEY',
        'FLASK_ENV'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Şifreleri gizle
            if 'PASSWORD' in var or 'SECRET' in var:
                masked = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
                print(f"✅ {var}: {masked}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: BULUNAMADI!")
    
    print()
    print("=" * 60)
    
    # DATABASE_URL parse et
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print("🔗 DATABASE_URL Analizi:")
        print("-" * 60)
        
        # postgres:// -> postgresql:// dönüşümü
        if database_url.startswith('postgres://'):
            print("⚠️  URL 'postgres://' ile başlıyor")
            print("✅ 'postgresql://' olarak değiştirilmeli")
            database_url = database_url.replace('postgres://', 'postgresql://')
        
        # URL'i parse et
        try:
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            
            print(f"Scheme: {parsed.scheme}")
            print(f"Host: {parsed.hostname}")
            print(f"Port: {parsed.port}")
            print(f"Database: {parsed.path[1:]}")
            print(f"User: {parsed.username}")
            print(f"Password: {'*' * 10}")
        except Exception as e:
            print(f"❌ URL parse hatası: {e}")
    
    print()
    print("=" * 60)

if __name__ == '__main__':
    main()
