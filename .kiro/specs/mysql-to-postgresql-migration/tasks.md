# Implementation Plan: MySQL to PostgreSQL Migration

## Task Overview

Bu implementation plan, MySQL'den PostgreSQL'e geçiş ve performans optimizasyonu için gerekli tüm kod değişikliklerini içerir. Her task incremental olarak ilerler ve önceki task'lere bağımlıdır.

---

## Phase 1: Environment Setup & Dependencies

- [x] 1. PostgreSQL bağımlılıklarını ekle ve konfigürasyonu güncelle


  - requirements.txt dosyasına psycopg2-binary, alembic ekle
  - config.py dosyasını PostgreSQL desteği için güncelle
  - Environment variable'ları .env.example'a ekle
  - Docker compose dosyasına PostgreSQL servisi ekle
  - _Requirements: 2.1, 11.1, 11.2_

- [x] 2. Database connection manager oluştur



  - [x] 2.1 Connection pool konfigürasyonunu config.py'a ekle

    - Pool size, timeout, recycle ayarları
    - PostgreSQL specific connection args
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [x] 2.2 Health check mekanizması ekle


    - /health endpoint oluştur
    - Database ping kontrolü
    - Pool statistics endpoint
    - _Requirements: 2.4_
  
  - [x] 2.3 Auto-reconnect mekanizması implement et


    - Connection retry logic
    - Exponential backoff
    - _Requirements: 2.5_

---

## Phase 2: Schema Migration

- [x] 3. Alembic migration altyapısını kur



  - [x] 3.1 Alembic initialize et


    - alembic init migrations
    - alembic.ini konfigürasyonu
    - env.py dosyasını SQLAlchemy ile entegre et
    - _Requirements: 3.1_
  


  - [x] 3.2 Initial migration script oluştur

    - Mevcut MySQL şemasını PostgreSQL'e dönüştür
    - ENUM tiplerini PostgreSQL ENUM'a çevir




    - DATETIME → TIMESTAMP WITH TIME ZONE
    - AUTO_INCREMENT → SERIAL/IDENTITY
    - _Requirements: 3.1, 3.2, 3.3, 3.4_



- [ ] 4. Model güncellemeleri yap
  - [x] 4.1 models.py'da timezone-aware datetime kullan


    - datetime.utcnow → datetime.now(timezone.utc)
    - Tüm DateTime kolonlarını timezone-aware yap
    - _Requirements: 3.2_
  
  - [x] 4.2 JSONB kolonları ekle

    - audit_logs tablosunda eski_deger ve yeni_deger JSONB
    - sistem_loglari tablosunda islem_detay JSONB
    - _Requirements: 6.1, 6.4_




  
  - [x] 4.3 PostgreSQL ENUM tipleri tanımla

    - kullanici_rol ENUM
    - hareket_tipi ENUM

    - zimmet_durum ENUM
    - minibar_islem_tipi ENUM
    - _Requirements: 3.1_

---


## Phase 3: Data Migration Tool

- [ ] 5. Migration script'i oluştur
  - [x] 5.1 Migration manager class'ı yaz

    - MySQL ve PostgreSQL connection yönetimi

    - Batch processing (1000 rows)
    - Progress tracking
    - Checkpoint mekanizması
    - _Requirements: 1.1, 1.2_

  
  - [x] 5.2 Schema converter implement et

    - MySQL DDL → PostgreSQL DDL dönüşümü
    - Data type mapping
    - Constraint dönüşümü

    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 5.3 Data migrator implement et

    - Tablo sırasını belirle (foreign key dependencies)
    - Batch data copy
    - Error handling ve retry logic

    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [ ] 5.4 Tüm MySQL tablolarını PostgreSQL'e aktar
    - [x] 5.4.1 Oteller tablosunu migrate et

      - Otel bilgilerini kopyala

      - Veri doğrulama yap
      - _Requirements: 1.1, 1.2_
    
    - [x] 5.4.2 Kullanıcılar tablosunu migrate et

      - Kullanıcı bilgilerini kopyala
      - Şifre hash'lerini koru

      - Rol ENUM dönüşümü
      - _Requirements: 1.1, 3.1_
    
    - [x] 5.4.3 Katlar ve Odalar tablolarını migrate et

      - Kat bilgilerini kopyala
      - Oda bilgilerini kopyala

      - QR kod verilerini koru
      - Foreign key ilişkilerini doğrula
      - _Requirements: 1.1, 1.2, 10.2_
    
    - [x] 5.4.4 Ürün Grupları ve Ürünler tablolarını migrate et

      - Ürün grup bilgilerini kopyala

      - Ürün bilgilerini kopyala
      - Barkod unique constraint'i koru
      - _Requirements: 1.1, 1.2_
    
    - [x] 5.4.5 Stok Hareketleri tablosunu migrate et

      - Tüm stok giriş/çıkış kayıtlarını kopyala
      - Hareket tipi ENUM dönüşümü
      - Timestamp timezone dönüşümü
      - Foreign key ilişkilerini doğrula
      - _Requirements: 1.1, 3.1, 3.2, 10.2_
    
    - [x] 5.4.6 Personel Zimmet tablolarını migrate et

      - PersonelZimmet ana kayıtlarını kopyala
      - PersonelZimmetDetay detay kayıtlarını kopyala
      - Durum ENUM dönüşümü
      - Zimmet-Detay ilişkilerini doğrula
      - _Requirements: 1.1, 3.1, 10.2_
    
    - [x] 5.4.7 Minibar İşlem tablolarını migrate et

      - MinibarIslem ana kayıtlarını kopyala
      - MinibarIslemDetay detay kayıtlarını kopyala
      - İşlem tipi ENUM dönüşümü
      - Tüm ilişkileri doğrula
      - _Requirements: 1.1, 3.1, 10.2_
    
    - [x] 5.4.8 Minibar Dolum Talepleri tablosunu migrate et

      - Dolum talep kayıtlarını kopyala
      - Durum ENUM dönüşümü
      - _Requirements: 1.1, 3.1_
    
    - [x] 5.4.9 QR Kod Okutma Log tablosunu migrate et

      - QR okutma geçmişini kopyala
      - Okutma tipi ENUM dönüşümü
      - _Requirements: 1.1, 3.1_
    

    - [x] 5.4.10 Sistem Ayarları tablosunu migrate et

      - Sistem ayar kayıtlarını kopyala
      - Anahtar-değer çiftlerini koru
      - _Requirements: 1.1_
    
    - [x] 5.4.11 Sistem ve Hata Log tablolarını migrate et

      - SistemLog kayıtlarını kopyala
      - HataLog kayıtlarını kopyala
      - JSON detayları JSONB'ye dönüştür
      - _Requirements: 1.1, 6.1, 6.4_
    
    - [x] 5.4.12 Audit Log tablosunu migrate et

      - Tüm audit kayıtlarını kopyala
      - eski_deger ve yeni_deger JSON → JSONB
      - İşlem tipi ENUM dönüşümü
      - _Requirements: 1.1, 3.1, 6.1, 6.4_
    
    - [x] 5.4.13 Otomatik Raporlar tablosunu migrate et

      - Rapor kayıtlarını kopyala
      - Rapor verisi JSON → JSONB
      - _Requirements: 1.1, 6.1_
  
  - [x] 5.5 Data validator oluştur

    - Row count comparison (her tablo için)
    - Checksum validation
    - Foreign key integrity check
    - Orphan record detection
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  

  - [x] 5.6 Rollback mekanizması ekle

    - Checkpoint'lere geri dönme
    - Backup'tan restore
    - _Requirements: 1.4, 12.5_

- [x] 5.7 Migration script için unit test'ler yaz

  - Schema converter test
  - Data migrator test
  - Validator test
  - _Requirements: 1.3, 10.4_

---

## Phase 4: Query Optimization

- [ ] 6. Query helper fonksiyonları oluştur
  - [x] 6.1 utils/query_helpers.py dosyası oluştur

    - Eager loading helper'ları
    - Pagination helper'ları
    - Bulk operation helper'ları
    - _Requirements: 5.1, 5.4_
  

  - [x] 6.2 N+1 query problemlerini düzelt

    - PersonelZimmet queries'de joinedload kullan
    - MinibarIslem queries'de selectinload kullan
    - StokHareket queries optimize et
    - _Requirements: 5.1_
  
  - [x] 6.3 Cursor-based pagination implement et

    - paginate_cursor_based fonksiyonu
    - API endpoint'lerinde kullan
    - _Requirements: 5.5_
  
  - [x] 6.4 Bulk operations ekle

    - bulk_insert_stok_hareketleri
    - bulk_update_zimmet_detay
    - _Requirements: 5.1_


- [x] 6.5 Query optimization için test'ler yaz

  - N+1 prevention test
  - Pagination performance test
  - Bulk operation test
  - _Requirements: 5.1, 5.5_

---

## Phase 5: Index Optimization

- [ ] 7. Database indekslerini oluştur
  - [x] 7.1 Migration script'inde index tanımları ekle

    - Foreign key indexes
    - Composite indexes (oda_id, islem_tarihi)
    - Partial indexes (aktif=true)
    - GIN indexes (JSONB kolonlar)
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  

  - [x] 7.2 Index monitoring fonksiyonları ekle

    - Kullanılmayan index tespiti
    - Index boyut raporlama
    - Index usage statistics
    - _Requirements: 4.5_

---

## Phase 6: Performance Monitoring

- [x] 8. Performance monitoring sistemi kur

  - [x] 8.1 Query performance tracker oluştur

    - utils/performance.py dosyası
    - PerformanceMonitor class
    - Slow query logging
    - _Requirements: 8.1, 8.2_
  

  - [x] 8.2 Database metrics collector ekle

    - utils/metrics.py dosyası
    - DatabaseMetrics class
    - Connection stats, table sizes, cache hit ratio
    - _Requirements: 8.3, 8.4, 8.5_

  
  - [x] 8.3 Metrics storage tabloları oluştur

    - query_performance_log tablosu
    - database_metrics tablosu
    - Migration script'i ekle
    - _Requirements: 8.1, 8.5_
  

  - [x] 8.4 Scheduled metrics collection job ekle

    - APScheduler entegrasyonu
    - 5 dakikada bir metrics toplama
    - _Requirements: 8.3, 8.5_
  

  - [x] 8.5 Performance dashboard endpoint'i ekle

    - /admin/performance route
    - Metrics görselleştirme
    - Slow query listesi
    - _Requirements: 8.2, 8.3_


- [x] 8.6 Performance monitoring test'leri yaz


  - Metrics collection test
  - Slow query detection test
  - _Requirements: 8.1, 8.2_

---

## Phase 7: Caching Layer

- [ ] 9. Query result caching ekle
  - [x] 9.1 QueryCache class'ı oluştur


    - utils/cache.py dosyası
    - TTL-based caching
    - Cache invalidation
    - _Requirements: 5.1_
  
  - [x] 9.2 Sık kullanılan query'lere cache ekle


    - get_aktif_urun_gruplari
    - get_stok_toplamlari_cached
    - get_kritik_stok_urunler_cached
    - _Requirements: 5.1_
  

  - [x] 9.3 Cache invalidation logic ekle

    - Stok değişikliklerinde cache temizle
    - Ürün güncellemelerinde cache temizle
    - _Requirements: 5.1_

- [x] 9.4 Caching test'leri yaz

  - Cache hit/miss test
  - TTL expiration test
  - Invalidation test
  - _Requirements: 5.1_

---

## Phase 8: Transaction Management

- [ ] 10. Transaction handling iyileştirmeleri
  - [x] 10.1 Safe transaction decorator oluştur

    - @safe_transaction decorator
    - Automatic rollback on error
    - Error logging
    - _Requirements: 7.1, 7.3, 7.4_
  
  - [x] 10.2 Optimistic locking ekle

    - Model'lere version field ekle
    - Concurrent update detection
    - _Requirements: 7.2_
  
  - [x] 10.3 Retry logic ekle

    - @retry decorator (tenacity)
    - Connection error retry
    - _Requirements: 7.3_
  
  - [x] 10.4 Kritik endpoint'lere transaction management ekle

    - Stok giriş/çıkış
    - Zimmet işlemleri
    - Minibar işlemleri
    - _Requirements: 7.1, 7.4, 7.5_

- [x] 10.5 Transaction management test'leri yaz

  - Rollback test
  - Concurrent update test
  - Retry logic test
  - _Requirements: 7.1, 7.2, 7.3_

---

## Phase 9: Backup & Recovery

- [ ] 11. Backup sistemi kur
  - [x] 11.1 BackupManager class'ı oluştur

    - utils/backup.py dosyası
    - pg_dump wrapper
    - Backup verification
    - _Requirements: 9.1, 9.2_
  
  - [x] 11.2 Scheduled backup job ekle

    - Daily backup at 02:00
    - Backup retention (7 days)
    - Old backup cleanup
    - _Requirements: 9.1, 9.4_
  
  - [x] 11.3 Restore fonksiyonu ekle

    - pg_restore wrapper
    - Restore verification
    - _Requirements: 9.5_
  
  - [x] 11.4 Backup monitoring ekle

    - Backup success/failure tracking
    - Admin notification on failure
    - _Requirements: 9.3_

- [x] 11.5 Backup system test'leri yaz

  - Backup creation test
  - Restore test
  - Cleanup test
  - _Requirements: 9.1, 9.5_

---

## Phase 10: Migration Execution

- [ ] 12. Production migration hazırlığı
  - [x] 12.1 Pre-migration checklist oluştur

    - MySQL full backup
    - Disk space check
    - Connection test
    - _Requirements: 1.5_
  
  - [x] 12.2 Migration script'ini çalıştır

    - Schema migration
    - Data migration
    - Index creation
    - Validation
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [x] 12.3 Post-migration tasks

    - Sequence update
    - Statistics update (ANALYZE)
    - Constraint activation
    - _Requirements: 10.5_
  
  - [x] 12.4 Validation report oluştur

    - Row count comparison
    - Data integrity check
    - Performance baseline
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

---

## Phase 11: Testing & Validation

- [ ] 13. Comprehensive testing
  - [x] 13.1 Integration test suite çalıştır

    - Tüm endpoint'leri test et
    - Database operations test
    - _Requirements: 12.4_
  
  - [x] 13.2 Performance test'leri çalıştır

    - Load testing (Locust)
    - Query performance comparison
    - Connection pool stress test
    - _Requirements: 5.1, 5.2, 5.3_
  
  - [x] 13.3 Data integrity validation

    - Foreign key check
    - Constraint validation
    - Data type validation
    - _Requirements: 10.1, 10.2, 10.5_

- [x] 13.4 End-to-end test suite oluştur

  - User workflow tests
  - Critical path tests
  - _Requirements: 12.4_

---

## Phase 12: Documentation & Deployment

- [ ] 14. Documentation ve deployment
  - [x] 14.1 Migration documentation yaz

    - Migration steps
    - Rollback procedure
    - Troubleshooting guide
    - _Requirements: 12.5_
  
  - [x] 14.2 Performance comparison report oluştur

    - Before/after metrics
    - Query performance improvements
    - Resource usage comparison
    - _Requirements: 8.1, 8.2, 8.3_
  
  - [x] 14.3 Operational runbook hazırla

    - Monitoring checklist
    - Alert response procedures
    - Backup/restore procedures
    - _Requirements: 9.1, 9.5_
  
  - [x] 14.4 Team training materyalleri hazırla


    - PostgreSQL best practices
    - New monitoring tools
    - Troubleshooting guide
    - _Requirements: 11.1, 11.2_

---

## Success Criteria

✅ Tüm veriler başarıyla migrate edildi (100% data integrity)
✅ Sorgu performansı %40+ iyileşti
✅ Tüm test'ler geçiyor
✅ Monitoring ve alerting aktif
✅ Backup sistemi çalışıyor
✅ Documentation tamamlandı
✅ Team training yapıldı

## Notes

- Her phase bağımsız test edilmeli
- Migration production'da yapılmadan önce staging'de test edilmeli
- Rollback planı her zaman hazır olmalı
- Performance baseline'ı migration öncesi ölçülmeli
