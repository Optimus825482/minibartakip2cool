"""
Test Configuration
Testler için izole konfigürasyon - Production'a hiç dokunmaz!
"""
import os
import tempfile


class TestConfig:
    """Test konfigürasyonu"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key-do-not-use-in-production'
    
    # SQLite in-memory database - Production'a hiç dokunmaz!
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Test için DB type
    DB_TYPE = 'mysql'  # SQLite için MySQL mode
    
    # Server name for URL generation
    SERVER_NAME = 'localhost.localdomain'
    
    # Disable rate limiting in tests
    RATELIMIT_ENABLED = False
    
    # Logging
    LOG_LEVEL = 'ERROR'
