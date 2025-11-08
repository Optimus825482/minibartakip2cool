#!/usr/bin/env python3
"""
Quick Database Connection Test
Local'de test etmek için
"""

import os
import sys
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Config'i import et
from config import Config

print("=" * 60)
print("🔍 Database Connection Test")
print("=" * 60)
print()

# Config bilgilerini göster
print("📋 Configuration:")
print(f"  ENV: {Config.ENV}")
print(f"  IS_DEVELOPMENT: {Config.IS_DEVELOPMENT}")
print(f"  DB_TYPE: {Config.DB_TYPE}")
print()

# Database URI'yi göster (password'ü gizle)
db_uri = Config.SQLALCHEMY_DATABASE_URI
if db_uri:
    # Password'ü gizle
    if '@' in db_uri:
        parts = db_uri.split('@')
        user_part = parts[0].split('://')[1].split(':')[0]
        masked_uri = db_uri.replace(parts[0].split(':')[-1], '***')
        print(f"  Database URI: {masked_uri}")
    else:
        print(f"  Database URI: {db_uri}")
else:
    print("  ❌ Database URI bulunamadı!")
    sys.exit(1)

print()

# Engine options'ı göster
print("⚙️  Engine Options:")
for key, value in Config.SQLALCHEMY_ENGINE_OPTIONS.items():
    if key == 'connect_args':
        print(f"  {key}:")
        for k, v in value.items():
            print(f"    {k}: {v}")
    else:
        print(f"  {key}: {value}")

print()
print("=" * 60)
print("✅ Configuration OK!")
print("=" * 60)
