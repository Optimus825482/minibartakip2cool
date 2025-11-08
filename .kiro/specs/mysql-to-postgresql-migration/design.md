# Design Document: MySQL to PostgreSQL Migration & Performance Optimization

## Overview

Bu tasarım, Minibar Takip Sistemi'nin MySQL'den PostgreSQL'e geçişini ve kapsamlı performans optimizasyonlarını içermektedir. Geçiş süreci zero-downtime hedeflenmekte ve tüm mevcut özellikler korunmaktadır.

### Temel Hedefler

1. **Veri Bütünlüğü**: %100 veri aktarımı garantisi
2. **Performans**: Sorgu sürelerinde minimum %40 iyileştirme
3. **Ölçeklenebilirlik**: 10x daha fazla concurrent kullanıcı desteği
4. **Güvenilirlik**: Otomatik yedekleme ve disaster recovery
5. **Geriye Dönük Uyumluluk**: Mevcut kod değişikliği minimizasyonu

### Teknoloji Stack

- **Database**: PostgreSQL 15+
- **Python Driver**: psycopg2-binary 2.9+
- **ORM**: SQLAlchemy 2.0+
- **Migration Tool**: Alembic 1.12+
- **Connection Pooling**: SQLAlchemy Engine Pool
- **Monitoring**: pg_stat_statements, custom metrics
- **Backup**: pg_dump, pg_basebackup

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Flask Application                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routes     │  │   Business   │  │   Utils      │     │
│  │   Layer      │  │   Logic      │  │   Layer      │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
├────────────────────────────┼─────────────────────────────────┤
│                   SQLAlchemy ORM                             │
├────────────────────────────┼─────────────────────────────────┤
│              Database Connection Manager                     │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Connection Pool (5-20 connections)              │       │
│  │  - Health Checks                                 │       │
│  │  - Auto Reconnect                                │       │
│  │  - Timeout Management                            │       │
│  └──────────────────────────────────────────────────┘       │
├─────────────────────────────────────────────────────────────┤
│                    PostgreSQL 15+                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Tables     │  │   Indexes    │  │   JSONB      │     │
│  │   (15)       │  │   (Optimized)│  │   Columns    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```


## Components and Interfaces

### 1. Database Connection Manager

**Sorumluluk**: PostgreSQL bağlantı havuzu yönetimi ve optimizasyonu

**Arayüz**:
```python
class DatabaseConnectionManager:
    def __init__(self, database_url: str, pool_config: PoolConfig)
    def get_connection(self) -> Connection
    def release_connection(self, conn: Connection) -> None
    def health_check(self) -> bool
    def get_pool_stats(self) -> PoolStats
    def close_all(self) -> None
```

**Konfigürasyon**:
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,              # Minimum connections
    'max_overflow': 10,           # Additional connections
    'pool_timeout': 30,           # Wait timeout (seconds)
    'pool_recycle': 3600,         # Recycle after 1 hour
    'pool_pre_ping': True,        # Health check before use
    'echo_pool': False,           # Debug logging
    'connect_args': {
        'connect_timeout': 10,
        'options': '-c timezone=utc'
    }
}
```

### 2. Migration System

**Sorumluluk**: MySQL'den PostgreSQL'e veri aktarımı

**Bileşenler**:
- **Schema Converter**: MySQL DDL → PostgreSQL DDL
- **Data Migrator**: Batch veri aktarımı
- **Validator**: Veri bütünlüğü kontrolü
- **Rollback Manager**: Hata durumunda geri alma

**Migration Pipeline**:
```
1. Pre-Migration Checks
   ├─ MySQL connection test
   ├─ PostgreSQL connection test
   ├─ Disk space check
   └─ Backup creation

2. Schema Migration
   ├─ Convert table definitions
   ├─ Convert indexes
   ├─ Convert constraints
   └─ Convert sequences

3. Data Migration (Batch Processing)
   ├─ Disable triggers/constraints
   ├─ Copy data in batches (1000 rows)
   ├─ Progress tracking
   └─ Error handling

4. Post-Migration Tasks
   ├─ Enable constraints
   ├─ Update sequences
   ├─ Rebuild indexes
   ├─ Analyze tables
   └─ Validate data

5. Validation
   ├─ Row count comparison
   ├─ Checksum validation
   ├─ Foreign key validation
   └─ Data type validation
```


### 3. Query Optimizer

**Sorumluluk**: SQL sorgu performansını optimize etme

**Optimizasyon Stratejileri**:

1. **N+1 Query Prevention**
   - Eager loading kullanımı
   - `joinedload()` ve `selectinload()` stratejileri
   - Relationship lazy loading optimizasyonu

2. **Index Optimization**
   - Composite indexes for common queries
   - Partial indexes for filtered queries
   - GIN indexes for JSONB columns
   - BRIN indexes for time-series data

3. **Query Rewriting**
   - `SELECT *` → Specific columns
   - `OFFSET` → Cursor-based pagination
   - Subquery → JOIN optimization
   - `IN` clause → `ANY` array optimization

**Örnek Optimizasyonlar**:

```python
# ÖNCE (N+1 Problem)
zimmetler = PersonelZimmet.query.all()
for zimmet in zimmetler:
    print(zimmet.personel.ad)  # Her zimmet için ayrı sorgu!

# SONRA (Eager Loading)
zimmetler = PersonelZimmet.query.options(
    joinedload(PersonelZimmet.personel)
).all()
for zimmet in zimmetler:
    print(zimmet.personel.ad)  # Tek sorgu!
```

```python
# ÖNCE (Yavaş Pagination)
page = 10
per_page = 50
offset = (page - 1) * per_page
items = Urun.query.offset(offset).limit(per_page).all()

# SONRA (Cursor-based)
last_id = request.args.get('last_id', 0)
items = Urun.query.filter(Urun.id > last_id).limit(per_page).all()
```

### 4. Index Manager

**Sorumluluk**: Veritabanı indekslerini yönetme ve optimize etme

**Index Stratejisi**:

```sql
-- Foreign Key Indexes (Otomatik)
CREATE INDEX idx_stok_hareketleri_urun_id ON stok_hareketleri(urun_id);
CREATE INDEX idx_stok_hareketleri_islem_yapan_id ON stok_hareketleri(islem_yapan_id);

-- Composite Indexes (Sık kullanılan sorgular için)
CREATE INDEX idx_minibar_islem_oda_tarih ON minibar_islemleri(oda_id, islem_tarihi DESC);
CREATE INDEX idx_stok_hareket_urun_tarih ON stok_hareketleri(urun_id, islem_tarihi DESC);

-- Partial Indexes (Filtered queries için)
CREATE INDEX idx_aktif_urunler ON urunler(urun_adi) WHERE aktif = true;
CREATE INDEX idx_aktif_zimmet ON personel_zimmet(personel_id) WHERE durum = 'aktif';

-- GIN Indexes (JSONB için)
CREATE INDEX idx_audit_logs_eski_deger ON audit_logs USING GIN (eski_deger);
CREATE INDEX idx_audit_logs_yeni_deger ON audit_logs USING GIN (yeni_deger);

-- Text Search Indexes
CREATE INDEX idx_urun_search ON urunler USING GIN (to_tsvector('turkish', urun_adi));
```

**Index Monitoring**:
```sql
-- Kullanılmayan indeksler
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexrelname NOT LIKE 'pg_toast%'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Index boyutları
SELECT indexname, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```


## Data Models

### PostgreSQL Schema Değişiklikleri

#### 1. ENUM Tipi Dönüşümleri

**MySQL ENUM → PostgreSQL ENUM**:

```sql
-- MySQL
rol ENUM('sistem_yoneticisi', 'admin', 'depo_sorumlusu', 'kat_sorumlusu')

-- PostgreSQL
CREATE TYPE kullanici_rol AS ENUM (
    'sistem_yoneticisi', 
    'admin', 
    'depo_sorumlusu', 
    'kat_sorumlusu'
);

ALTER TABLE kullanicilar 
ALTER COLUMN rol TYPE kullanici_rol 
USING rol::kullanici_rol;
```

#### 2. Timestamp Dönüşümleri

**MySQL DATETIME → PostgreSQL TIMESTAMP WITH TIME ZONE**:

```sql
-- Tüm datetime kolonları timezone-aware olacak
ALTER TABLE kullanicilar 
ALTER COLUMN olusturma_tarihi TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE stok_hareketleri 
ALTER COLUMN islem_tarihi TYPE TIMESTAMP WITH TIME ZONE;

-- Python tarafında
from datetime import datetime, timezone
now = datetime.now(timezone.utc)  # Timezone-aware
```

#### 3. JSONB Dönüşümleri

**TEXT/JSON → JSONB**:

```sql
-- Audit logs için
ALTER TABLE audit_logs 
ALTER COLUMN eski_deger TYPE JSONB USING eski_deger::jsonb;

ALTER TABLE audit_logs 
ALTER COLUMN yeni_deger TYPE JSONB USING yeni_deger::jsonb;

-- Sistem logs için
ALTER TABLE sistem_loglari 
ALTER COLUMN islem_detay TYPE JSONB USING islem_detay::jsonb;

-- GIN index ekle
CREATE INDEX idx_audit_eski_deger_gin ON audit_logs USING GIN (eski_deger);
CREATE INDEX idx_audit_yeni_deger_gin ON audit_logs USING GIN (yeni_deger);
```

#### 4. AUTO_INCREMENT → SERIAL/IDENTITY

```sql
-- MySQL
id INT AUTO_INCREMENT PRIMARY KEY

-- PostgreSQL (Modern yaklaşım)
id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY

-- Veya (Eski yaklaşım)
id SERIAL PRIMARY KEY
```

### Yeni Performans Tabloları

#### Query Performance Log

```sql
CREATE TABLE query_performance_log (
    id SERIAL PRIMARY KEY,
    query_hash VARCHAR(64) NOT NULL,
    query_text TEXT NOT NULL,
    execution_time_ms NUMERIC(10, 2) NOT NULL,
    row_count INTEGER,
    endpoint VARCHAR(200),
    kullanici_id INTEGER REFERENCES kullanicilar(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    query_plan JSONB
);

CREATE INDEX idx_qpl_hash_time ON query_performance_log(query_hash, execution_time_ms DESC);
CREATE INDEX idx_qpl_created ON query_performance_log(created_at DESC);
```

#### Database Metrics

```sql
CREATE TABLE database_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC(15, 2) NOT NULL,
    metric_unit VARCHAR(20),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

CREATE INDEX idx_metrics_name_time ON database_metrics(metric_name, recorded_at DESC);
```


## Error Handling

### Transaction Management

**Stratejiler**:

1. **Automatic Rollback**
```python
from sqlalchemy.exc import SQLAlchemyError

def safe_transaction(func):
    """Decorator for safe transaction handling"""
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            db.session.commit()
            return result
        except SQLAlchemyError as e:
            db.session.rollback()
            log_hata(e, modul=func.__name__)
            raise
        except Exception as e:
            db.session.rollback()
            log_hata(e, modul=func.__name__)
            raise
    return wrapper
```

2. **Optimistic Locking**
```python
class Urun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer, default=1, nullable=False)
    
    def update(self, **kwargs):
        current_version = self.version
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.version += 1
        
        # Version check
        result = db.session.execute(
            update(Urun)
            .where(Urun.id == self.id)
            .where(Urun.version == current_version)
            .values(**kwargs, version=self.version)
        )
        
        if result.rowcount == 0:
            raise ConcurrentUpdateError("Record was modified by another user")
```

3. **Connection Retry Logic**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def execute_with_retry(query):
    """Execute query with automatic retry on connection errors"""
    try:
        return db.session.execute(query)
    except OperationalError as e:
        if "connection" in str(e).lower():
            db.session.rollback()
            raise  # Retry
        raise  # Don't retry for other errors
```

### Migration Error Handling

**Rollback Strategy**:

```python
class MigrationManager:
    def __init__(self):
        self.checkpoint_file = 'migration_checkpoint.json'
        self.checkpoints = []
    
    def create_checkpoint(self, table_name, rows_migrated):
        """Save migration progress"""
        checkpoint = {
            'table': table_name,
            'rows': rows_migrated,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self.checkpoints.append(checkpoint)
        self._save_checkpoints()
    
    def rollback_to_checkpoint(self, checkpoint_index):
        """Rollback to specific checkpoint"""
        checkpoint = self.checkpoints[checkpoint_index]
        # Delete data after this checkpoint
        # Restore from backup if needed
    
    def handle_migration_error(self, error, context):
        """Handle migration errors with detailed logging"""
        error_log = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'last_checkpoint': self.checkpoints[-1] if self.checkpoints else None
        }
        
        # Log to file
        with open('migration_errors.log', 'a') as f:
            f.write(json.dumps(error_log) + '\n')
        
        # Notify admin
        send_admin_notification(error_log)
        
        # Attempt rollback
        if self.checkpoints:
            self.rollback_to_checkpoint(-1)
```


## Testing Strategy

### 1. Unit Tests

**Database Layer Tests**:
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_engine('postgresql://test:test@localhost/test_minibar')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_connection_pool(test_db):
    """Test connection pool behavior"""
    manager = DatabaseConnectionManager(test_db.bind.url)
    
    # Test pool size
    assert manager.get_pool_stats().size == 10
    
    # Test connection acquisition
    conn = manager.get_connection()
    assert conn is not None
    
    # Test connection release
    manager.release_connection(conn)
    assert manager.get_pool_stats().checked_out == 0

def test_transaction_rollback(test_db):
    """Test automatic rollback on error"""
    urun = Urun(urun_adi="Test", grup_id=1)
    test_db.add(urun)
    
    try:
        # Force error
        test_db.execute("INVALID SQL")
    except:
        test_db.rollback()
    
    # Verify rollback
    assert test_db.query(Urun).filter_by(urun_adi="Test").first() is None
```

### 2. Integration Tests

**Migration Tests**:
```python
def test_full_migration():
    """Test complete migration process"""
    # Setup MySQL test data
    mysql_conn = create_mysql_connection()
    create_test_data(mysql_conn)
    
    # Run migration
    migrator = MigrationManager(mysql_conn, postgres_conn)
    result = migrator.migrate_all()
    
    # Verify results
    assert result.success == True
    assert result.tables_migrated == 15
    assert result.rows_migrated > 0
    assert result.errors == []
    
    # Validate data
    validator = DataValidator(mysql_conn, postgres_conn)
    validation_result = validator.validate_all()
    assert validation_result.is_valid == True

def test_migration_rollback():
    """Test migration rollback on error"""
    migrator = MigrationManager(mysql_conn, postgres_conn)
    
    # Inject error
    with patch('migrator.migrate_table', side_effect=Exception("Test error")):
        result = migrator.migrate_all()
    
    # Verify rollback
    assert result.success == False
    assert postgres_conn.table_count() == 0
```

### 3. Performance Tests

**Query Performance Tests**:
```python
import time

def test_query_performance():
    """Test query execution times"""
    # Test N+1 prevention
    start = time.time()
    zimmetler = PersonelZimmet.query.options(
        joinedload(PersonelZimmet.personel),
        joinedload(PersonelZimmet.detaylar)
    ).limit(100).all()
    duration = time.time() - start
    
    assert duration < 0.5  # Should complete in < 500ms
    
    # Test pagination
    start = time.time()
    page = Urun.query.filter(Urun.id > 1000).limit(50).all()
    duration = time.time() - start
    
    assert duration < 0.1  # Should complete in < 100ms

def test_concurrent_transactions():
    """Test concurrent transaction handling"""
    from concurrent.futures import ThreadPoolExecutor
    
    def update_stok(urun_id):
        urun = Urun.query.get(urun_id)
        # Simulate update
        time.sleep(0.1)
        db.session.commit()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(update_stok, i) for i in range(1, 11)]
        results = [f.result() for f in futures]
    
    # Verify no deadlocks or errors
    assert all(r is None for r in results)
```

### 4. Load Tests

**Stress Testing**:
```python
from locust import HttpUser, task, between

class MinibarUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_stok(self):
        self.client.get("/admin/stok-yonetimi")
    
    @task(2)
    def view_zimmet(self):
        self.client.get("/depo-sorumlusu/personel-zimmet")
    
    @task(1)
    def create_stok_hareket(self):
        self.client.post("/api/stok-giris", json={
            "urun_id": 1,
            "miktar": 10,
            "aciklama": "Test"
        })

# Run: locust -f load_test.py --users 100 --spawn-rate 10
```


## Performance Optimization Details

### 1. Connection Pooling Configuration

**Optimal Settings**:
```python
# config.py
class Config:
    # PostgreSQL Connection
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://'
    )
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        # Pool Configuration
        'pool_size': 10,                    # Base connections
        'max_overflow': 10,                 # Extra connections
        'pool_timeout': 30,                 # Wait timeout
        'pool_recycle': 3600,               # Recycle after 1h
        'pool_pre_ping': True,              # Health check
        
        # Connection Configuration
        'connect_args': {
            'connect_timeout': 10,
            'options': '-c timezone=utc',
            'application_name': 'minibar_takip',
            
            # Performance tuning
            'keepalives': 1,
            'keepalives_idle': 30,
            'keepalives_interval': 10,
            'keepalives_count': 5,
        },
        
        # Execution Options
        'execution_options': {
            'isolation_level': 'READ COMMITTED'
        }
    }
```

### 2. Query Optimization Patterns

**Eager Loading Strategy**:
```python
# utils/query_helpers.py

def get_zimmetler_optimized(personel_id=None, durum=None):
    """Optimized zimmet query with eager loading"""
    query = PersonelZimmet.query.options(
        # Load related personel
        joinedload(PersonelZimmet.personel),
        
        # Load detaylar with their urun
        selectinload(PersonelZimmet.detaylar).joinedload(
            PersonelZimmetDetay.urun
        ).joinedload(Urun.grup)
    )
    
    if personel_id:
        query = query.filter_by(personel_id=personel_id)
    if durum:
        query = query.filter_by(durum=durum)
    
    return query.all()

def get_minibar_islemler_optimized(oda_id, limit=10):
    """Optimized minibar query"""
    return MinibarIslem.query.options(
        joinedload(MinibarIslem.oda).joinedload(Oda.kat),
        joinedload(MinibarIslem.personel),
        selectinload(MinibarIslem.detaylar).joinedload(
            MinibarIslemDetay.urun
        )
    ).filter_by(oda_id=oda_id)\
     .order_by(MinibarIslem.islem_tarihi.desc())\
     .limit(limit)\
     .all()
```

**Pagination Optimization**:
```python
def paginate_cursor_based(model, cursor_field, cursor_value, limit=50):
    """Cursor-based pagination (faster than OFFSET)"""
    query = model.query
    
    if cursor_value:
        query = query.filter(cursor_field > cursor_value)
    
    items = query.order_by(cursor_field).limit(limit + 1).all()
    
    has_next = len(items) > limit
    if has_next:
        items = items[:limit]
    
    next_cursor = getattr(items[-1], cursor_field.key) if items else None
    
    return {
        'items': items,
        'next_cursor': next_cursor,
        'has_next': has_next
    }

# Usage
result = paginate_cursor_based(
    Urun, 
    Urun.id, 
    cursor_value=request.args.get('cursor', type=int),
    limit=50
)
```

### 3. Caching Strategy

**Query Result Caching**:
```python
from functools import lru_cache
from datetime import datetime, timedelta

class QueryCache:
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return value
            del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, datetime.now())
    
    def invalidate(self, pattern=None):
        if pattern:
            keys_to_delete = [k for k in self.cache if pattern in k]
            for key in keys_to_delete:
                del self.cache[key]
        else:
            self.cache.clear()

# Global cache instance
query_cache = QueryCache(ttl_seconds=300)

@lru_cache(maxsize=128)
def get_aktif_urun_gruplari():
    """Cache active product groups"""
    return UrunGrup.query.filter_by(aktif=True).all()

def get_stok_toplamlari_cached(urun_ids):
    """Cache stock totals"""
    cache_key = f"stok_toplam_{','.join(map(str, sorted(urun_ids)))}"
    
    result = query_cache.get(cache_key)
    if result:
        return result
    
    result = get_stok_toplamlari(urun_ids)
    query_cache.set(cache_key, result)
    return result
```

### 4. Batch Operations

**Bulk Insert/Update**:
```python
def bulk_insert_stok_hareketleri(hareketler_data):
    """Bulk insert for better performance"""
    hareketler = [
        StokHareket(**data) for data in hareketler_data
    ]
    
    db.session.bulk_save_objects(hareketler)
    db.session.commit()
    
    return len(hareketler)

def bulk_update_zimmet_detay(updates):
    """Bulk update using CASE statement"""
    from sqlalchemy import case
    
    # Build CASE statement
    when_clauses = {
        update['id']: update['kalan_miktar'] 
        for update in updates
    }
    
    stmt = update(PersonelZimmetDetay).where(
        PersonelZimmetDetay.id.in_(when_clauses.keys())
    ).values(
        kalan_miktar=case(when_clauses, value=PersonelZimmetDetay.id)
    )
    
    db.session.execute(stmt)
    db.session.commit()
```


## Monitoring and Observability

### 1. Performance Monitoring

**Query Performance Tracker**:
```python
# utils/performance.py
import time
from functools import wraps

class PerformanceMonitor:
    def __init__(self):
        self.slow_query_threshold = 1.0  # seconds
    
    def track_query(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log slow queries
                if execution_time > self.slow_query_threshold:
                    self._log_slow_query(
                        func.__name__,
                        execution_time,
                        args,
                        kwargs
                    )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                self._log_failed_query(
                    func.__name__,
                    execution_time,
                    str(e)
                )
                raise
        
        return wrapper
    
    def _log_slow_query(self, func_name, execution_time, args, kwargs):
        log_entry = {
            'type': 'slow_query',
            'function': func_name,
            'execution_time': execution_time,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Save to database
        perf_log = QueryPerformanceLog(
            query_hash=hashlib.md5(func_name.encode()).hexdigest(),
            query_text=func_name,
            execution_time_ms=execution_time * 1000,
            endpoint=request.endpoint if request else None
        )
        db.session.add(perf_log)
        db.session.commit()

# Usage
monitor = PerformanceMonitor()

@monitor.track_query
def get_complex_report():
    # Complex query
    pass
```

### 2. Database Metrics Collection

**Metrics Collector**:
```python
# utils/metrics.py
from sqlalchemy import text

class DatabaseMetrics:
    def collect_all_metrics(self):
        """Collect all database metrics"""
        return {
            'connection_stats': self.get_connection_stats(),
            'table_sizes': self.get_table_sizes(),
            'index_usage': self.get_index_usage(),
            'slow_queries': self.get_slow_queries(),
            'cache_hit_ratio': self.get_cache_hit_ratio()
        }
    
    def get_connection_stats(self):
        """Get connection pool statistics"""
        query = text("""
            SELECT 
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active,
                count(*) FILTER (WHERE state = 'idle') as idle,
                count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
            FROM pg_stat_activity
            WHERE datname = current_database()
        """)
        
        result = db.session.execute(query).fetchone()
        return dict(result)
    
    def get_table_sizes(self):
        """Get table sizes"""
        query = text("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """)
        
        return [dict(row) for row in db.session.execute(query)]
    
    def get_index_usage(self):
        """Get index usage statistics"""
        query = text("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch,
                pg_size_pretty(pg_relation_size(indexrelid)) as size
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC
        """)
        
        return [dict(row) for row in db.session.execute(query)]
    
    def get_cache_hit_ratio(self):
        """Get cache hit ratio"""
        query = text("""
            SELECT 
                sum(heap_blks_read) as heap_read,
                sum(heap_blks_hit) as heap_hit,
                sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
            FROM pg_statio_user_tables
        """)
        
        result = db.session.execute(query).fetchone()
        return dict(result)
    
    def get_slow_queries(self, limit=10):
        """Get slowest queries from pg_stat_statements"""
        query = text("""
            SELECT 
                query,
                calls,
                total_exec_time,
                mean_exec_time,
                max_exec_time,
                rows
            FROM pg_stat_statements
            WHERE query NOT LIKE '%pg_stat_statements%'
            ORDER BY mean_exec_time DESC
            LIMIT :limit
        """)
        
        return [dict(row) for row in db.session.execute(query, {'limit': limit})]

# Scheduled metrics collection
from apscheduler.schedulers.background import BackgroundScheduler

def collect_metrics_job():
    """Background job to collect metrics"""
    metrics = DatabaseMetrics()
    data = metrics.collect_all_metrics()
    
    # Save to database
    for metric_name, metric_value in data.items():
        if isinstance(metric_value, (int, float)):
            db_metric = DatabaseMetric(
                metric_name=metric_name,
                metric_value=metric_value,
                metadata={}
            )
            db.session.add(db_metric)
    
    db.session.commit()

# Start scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(collect_metrics_job, 'interval', minutes=5)
scheduler.start()
```

### 3. Health Check Endpoint

```python
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Database check
        db.session.execute(text('SELECT 1'))
        db_status = 'healthy'
        
        # Connection pool check
        pool_stats = db.engine.pool.status()
        
        # Metrics
        metrics = DatabaseMetrics()
        cache_ratio = metrics.get_cache_hit_ratio()
        
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'pool': {
                'size': db.engine.pool.size(),
                'checked_out': db.engine.pool.checkedout(),
                'overflow': db.engine.pool.overflow()
            },
            'cache_hit_ratio': cache_ratio['ratio'],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 503
```


## Backup and Recovery

### 1. Automated Backup Strategy

**Backup Configuration**:
```python
# utils/backup.py
import subprocess
import os
from datetime import datetime, timedelta

class BackupManager:
    def __init__(self):
        self.backup_dir = os.getenv('BACKUP_DIR', '/backups')
        self.retention_days = 7
        self.db_url = os.getenv('DATABASE_URL')
    
    def create_backup(self):
        """Create PostgreSQL backup using pg_dump"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{self.backup_dir}/minibar_backup_{timestamp}.sql.gz"
        
        # Parse database URL
        db_config = self._parse_db_url(self.db_url)
        
        # Run pg_dump
        cmd = [
            'pg_dump',
            '-h', db_config['host'],
            '-U', db_config['user'],
            '-d', db_config['database'],
            '-F', 'c',  # Custom format
            '-Z', '9',  # Max compression
            '-f', backup_file
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['password']
        
        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True)
            
            # Verify backup
            if os.path.exists(backup_file):
                size = os.path.getsize(backup_file)
                
                # Log backup
                log_islem(
                    islem_tipi='backup',
                    modul='database',
                    detay={
                        'file': backup_file,
                        'size_mb': size / (1024 * 1024),
                        'timestamp': timestamp
                    }
                )
                
                return {
                    'success': True,
                    'file': backup_file,
                    'size': size
                }
        except subprocess.CalledProcessError as e:
            log_hata(e, modul='backup', extra_info={'stderr': e.stderr})
            return {'success': False, 'error': str(e)}
    
    def restore_backup(self, backup_file):
        """Restore from backup"""
        db_config = self._parse_db_url(self.db_url)
        
        cmd = [
            'pg_restore',
            '-h', db_config['host'],
            '-U', db_config['user'],
            '-d', db_config['database'],
            '-c',  # Clean before restore
            '-F', 'c',
            backup_file
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['password']
        
        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True)
            return {'success': True}
        except subprocess.CalledProcessError as e:
            return {'success': False, 'error': str(e)}
    
    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('minibar_backup_'):
                filepath = os.path.join(self.backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_date:
                    os.remove(filepath)
                    print(f"Deleted old backup: {filename}")

# Scheduled backup job
from apscheduler.schedulers.background import BackgroundScheduler

def daily_backup_job():
    """Daily backup job"""
    backup_manager = BackupManager()
    result = backup_manager.create_backup()
    
    if result['success']:
        backup_manager.cleanup_old_backups()
        print(f"Backup created: {result['file']}")
    else:
        # Send alert
        send_admin_notification({
            'type': 'backup_failed',
            'error': result['error']
        })

scheduler = BackgroundScheduler()
scheduler.add_job(daily_backup_job, 'cron', hour=2, minute=0)  # 02:00 daily
scheduler.start()
```

### 2. Point-in-Time Recovery

**WAL Archiving Configuration**:
```sql
-- postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /archive/%f'
max_wal_senders = 3
```

## Deployment Strategy

### Phase 1: Preparation (Week 1)

1. **Environment Setup**
   - PostgreSQL 15 kurulumu
   - Connection pooling test
   - Backup stratejisi test

2. **Code Updates**
   - requirements.txt güncelleme
   - config.py PostgreSQL desteği
   - Migration script'leri hazırlama

3. **Testing**
   - Unit test'ler
   - Integration test'ler
   - Performance baseline ölçümü

### Phase 2: Migration (Week 2)

1. **Pre-Migration**
   - MySQL full backup
   - Downtime planı
   - Rollback prosedürü hazırlama

2. **Migration Execution**
   - Schema migration
   - Data migration (batch)
   - Index creation
   - Constraint activation

3. **Validation**
   - Data integrity check
   - Row count verification
   - Foreign key validation

### Phase 3: Optimization (Week 3)

1. **Performance Tuning**
   - Index optimization
   - Query optimization
   - Connection pool tuning

2. **Monitoring Setup**
   - Metrics collection
   - Alert configuration
   - Dashboard setup

3. **Documentation**
   - Migration report
   - Performance comparison
   - Operational runbook

### Phase 4: Production (Week 4)

1. **Cutover**
   - Final sync
   - DNS/Config update
   - Application restart

2. **Monitoring**
   - 24/7 monitoring
   - Performance tracking
   - Error tracking

3. **Optimization**
   - Fine-tuning based on real traffic
   - Index adjustments
   - Query optimization

## Rollback Plan

### Rollback Triggers

1. Data integrity issues
2. Performance degradation > 50%
3. Critical bugs
4. Unrecoverable errors

### Rollback Procedure

```bash
# 1. Stop application
systemctl stop minibar-app

# 2. Restore MySQL backup
mysql -u root -p minibar_takip < backup_pre_migration.sql

# 3. Update config to MySQL
export DATABASE_URL="mysql://..."

# 4. Restart application
systemctl start minibar-app

# 5. Verify functionality
curl http://localhost:5000/health
```

## Success Metrics

### Performance Targets

- **Query Response Time**: < 100ms (p95)
- **Page Load Time**: < 500ms
- **Concurrent Users**: 100+
- **Database CPU**: < 60%
- **Connection Pool Usage**: < 80%

### Migration Success Criteria

- ✅ 100% data migrated
- ✅ 0 data loss
- ✅ All tests passing
- ✅ Performance improved by 40%+
- ✅ Zero critical bugs in first week

## Risk Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Data loss during migration | High | Low | Full backup, validation checks |
| Performance degradation | High | Medium | Load testing, rollback plan |
| Downtime > 4 hours | Medium | Low | Staged migration, practice runs |
| Compatibility issues | Medium | Medium | Extensive testing, gradual rollout |
| Team knowledge gap | Low | Medium | Training, documentation |

## Conclusion

Bu tasarım, MySQL'den PostgreSQL'e güvenli ve performanslı bir geçiş sağlar. Kapsamlı test stratejisi, monitoring ve rollback planı ile risk minimize edilmiştir. Beklenen performans iyileştirmeleri:

- **40-60%** daha hızlı sorgu süreleri
- **3x** daha fazla concurrent connection desteği
- **50%** daha az CPU kullanımı
- **Gelişmiş** JSONB ve full-text search özellikleri
