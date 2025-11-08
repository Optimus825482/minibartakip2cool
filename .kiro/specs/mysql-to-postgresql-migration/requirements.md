# Requirements Document

## Introduction

Bu özellik, mevcut Minibar Takip Sistemi'nin veritabanını MySQL'den PostgreSQL'e geçirmeyi ve sistemin genel performansını optimize etmeyi amaçlamaktadır. PostgreSQL'in gelişmiş özellikleri (JSONB, daha iyi indeksleme, concurrent işlemler) kullanılarak sistem performansı artırılacak ve ölçeklenebilirlik sağlanacaktır.

## Glossary

- **Migration System**: MySQL'den PostgreSQL'e veri aktarım ve dönüşüm sistemi
- **Database Connection Manager**: Veritabanı bağlantı havuzu ve yönetim sistemi
- **Query Optimizer**: SQL sorgularını optimize eden ve performans iyileştirmeleri yapan sistem
- **Index Manager**: Veritabanı indekslerini yöneten ve optimize eden sistem
- **Performance Monitor**: Veritabanı performansını izleyen ve raporlayan sistem
- **Backup System**: Veritabanı yedekleme ve geri yükleme sistemi
- **Data Validator**: Migrasyon sonrası veri bütünlüğünü kontrol eden sistem
- **PostgreSQL Driver**: Python PostgreSQL bağlantı kütüphanesi (psycopg2)
- **SQLAlchemy ORM**: Python ORM framework'ü
- **Connection Pool**: Veritabanı bağlantı havuzu
- **JSONB**: PostgreSQL'in binary JSON veri tipi
- **Audit Log**: Sistem değişiklik kayıtları
- **Transaction**: Veritabanı işlem birimi

## Requirements

### Requirement 1: Veritabanı Geçiş Altyapısı

**User Story:** Sistem yöneticisi olarak, mevcut MySQL veritabanındaki tüm verilerin PostgreSQL'e güvenli ve eksiksiz şekilde aktarılmasını istiyorum, böylece veri kaybı olmadan yeni veritabanına geçiş yapabilirim.

#### Acceptance Criteria

1. WHEN sistem yöneticisi migration script'ini çalıştırdığında, THE Migration System SHALL tüm MySQL tablolarını PostgreSQL uyumlu şemaya dönüştürmeli
2. WHEN veri aktarımı başladığında, THE Migration System SHALL her tablo için kayıt sayısını ve ilerleme durumunu raporlamalı
3. WHEN migration tamamlandığında, THE Migration System SHALL kaynak ve hedef veritabanlarındaki kayıt sayılarını karşılaştırmalı
4. WHEN migration sırasında hata oluştuğunda, THE Migration System SHALL hata detaylarını loglamalı ve işlemi güvenli şekilde durdurmalı
5. WHERE migration öncesi yedekleme seçeneği aktifse, THE Migration System SHALL mevcut MySQL veritabanının tam yedeğini almalı

### Requirement 2: PostgreSQL Bağlantı Yönetimi

**User Story:** Geliştirici olarak, PostgreSQL veritabanına optimize edilmiş bağlantı yönetimi istiyorum, böylece sistem performansı ve kaynak kullanımı iyileştirilmiş olsun.

#### Acceptance Criteria

1. THE Database Connection Manager SHALL connection pooling kullanarak minimum 5, maksimum 20 eşzamanlı bağlantı yönetmeli
2. WHEN bir bağlantı 30 saniyeden uzun süre boşta kaldığında, THE Database Connection Manager SHALL bağlantıyı otomatik olarak kapatmalı
3. WHEN bağlantı havuzu dolduğunda, THE Database Connection Manager SHALL yeni istekleri 10 saniye bekletmeli
4. THE Database Connection Manager SHALL her bağlantı için health check yapmalı ve bozuk bağlantıları yeniden oluşturmalı
5. WHEN veritabanı bağlantısı kesildiğinde, THE Database Connection Manager SHALL otomatik yeniden bağlanma mekanizması çalıştırmalı

### Requirement 3: Veri Tipi Dönüşümleri

**User Story:** Geliştirici olarak, MySQL'e özgü veri tiplerinin PostgreSQL karşılıklarına doğru şekilde dönüştürülmesini istiyorum, böylece veri bütünlüğü korunmuş olsun.

#### Acceptance Criteria

1. THE Migration System SHALL MySQL ENUM tiplerini PostgreSQL CHECK constraint veya ENUM tipine dönüştürmeli
2. THE Migration System SHALL MySQL DATETIME tiplerini PostgreSQL TIMESTAMP WITH TIME ZONE tipine dönüştürmeli
3. THE Migration System SHALL MySQL TEXT tiplerini PostgreSQL TEXT veya JSONB tipine (uygun yerlerde) dönüştürmeli
4. THE Migration System SHALL MySQL AUTO_INCREMENT alanlarını PostgreSQL SERIAL veya IDENTITY tipine dönüştürmeli
5. THE Migration System SHALL tüm karakter setlerini UTF-8 olarak korumalı

### Requirement 4: İndeks Optimizasyonu

**User Story:** Sistem yöneticisi olarak, sık kullanılan sorguların performansını artırmak için optimize edilmiş indeksler istiyorum, böylece sistem yanıt süreleri azaltılmış olsun.

#### Acceptance Criteria

1. THE Index Manager SHALL foreign key kolonları için otomatik indeks oluşturmalı
2. THE Index Manager SHALL tarih bazlı sorgular için timestamp kolonlarına indeks eklemelidir
3. WHERE arama işlemleri yapılan text kolonlar varsa, THE Index Manager SHALL GIN veya GiST indeksleri oluşturmalı
4. THE Index Manager SHALL composite indeksler için kullanım istatistiklerini analiz etmeli
5. THE Index Manager SHALL kullanılmayan indeksleri tespit edip raporlamalı

### Requirement 5: Sorgu Performans Optimizasyonu

**User Story:** Geliştirici olarak, mevcut SQL sorgularının PostgreSQL için optimize edilmesini istiyorum, böylece sorgu çalışma süreleri minimize edilmiş olsun.

#### Acceptance Criteria

1. THE Query Optimizer SHALL N+1 sorgu problemlerini tespit etmeli ve eager loading önerileri sunmalı
2. WHEN bir sorgu 1 saniyeden uzun sürdüğünde, THE Performance Monitor SHALL sorguyu loglamalı ve EXPLAIN ANALYZE çıktısı üretmeli
3. THE Query Optimizer SHALL JOIN işlemlerini analiz etmeli ve gereksiz JOIN'leri raporlamalı
4. THE Query Optimizer SHALL SELECT * kullanımlarını tespit etmeli ve sadece gerekli kolonların seçilmesini önermelidir
5. WHERE pagination kullanılan sorgular varsa, THE Query Optimizer SHALL OFFSET yerine cursor-based pagination önermelidir

### Requirement 6: JSONB Kullanımı

**User Story:** Geliştirici olarak, esnek veri yapıları için PostgreSQL JSONB tipini kullanmak istiyorum, böylece şema değişiklikleri olmadan yeni alanlar ekleyebilirim.

#### Acceptance Criteria

1. WHERE log kayıtları JSON formatında saklanıyorsa, THE Migration System SHALL TEXT kolonları JSONB tipine dönüştürmeli
2. THE Database Connection Manager SHALL JSONB kolonları için GIN indeksleri oluşturmalı
3. THE Query Optimizer SHALL JSONB sorgularında jsonb_path_query operatörlerini kullanmalı
4. THE Migration System SHALL mevcut JSON string'lerini valid JSONB formatına dönüştürmeli
5. WHERE JSONB kolonları kullanılıyorsa, THE Query Optimizer SHALL JSONB operatörlerini (->>, ->, @>, ?) kullanarak sorgu performansını artırmalı

### Requirement 7: Transaction Yönetimi

**User Story:** Geliştirici olarak, veri tutarlılığını garanti altına almak için gelişmiş transaction yönetimi istiyorum, böylece concurrent işlemler güvenli şekilde yönetilmiş olsun.

#### Acceptance Criteria

1. THE Database Connection Manager SHALL her kritik işlem için ACID özelliklerini garanti etmeli
2. WHEN concurrent update işlemleri olduğunda, THE Database Connection Manager SHALL optimistic locking veya pessimistic locking stratejisi uygulamalı
3. WHEN transaction başarısız olduğunda, THE Database Connection Manager SHALL otomatik rollback yapmalı ve hatayı loglamalı
4. THE Database Connection Manager SHALL transaction isolation level'ını READ COMMITTED olarak ayarlamalı
5. WHERE long-running transaction'lar tespit edildiğinde, THE Performance Monitor SHALL uyarı üretmeli

### Requirement 8: Performans İzleme ve Raporlama

**User Story:** Sistem yöneticisi olarak, veritabanı performansını sürekli izlemek ve raporlamak istiyorum, böylece performans sorunlarını proaktif olarak tespit edebilirim.

#### Acceptance Criteria

1. THE Performance Monitor SHALL her sorgu için execution time, row count ve plan bilgilerini kaydetmeli
2. WHEN ortalama sorgu süresi baseline'ın %50 üzerine çıktığında, THE Performance Monitor SHALL alarm üretmeli
3. THE Performance Monitor SHALL günlük performans raporu oluşturmalı ve en yavaş 10 sorguyu listelemelidir
4. THE Performance Monitor SHALL connection pool kullanım oranını izlemeli ve %80'i geçtiğinde uyarı vermeli
5. THE Performance Monitor SHALL database size, table size ve index size metriklerini günlük olarak kaydetmeli

### Requirement 9: Yedekleme ve Geri Yükleme

**User Story:** Sistem yöneticisi olarak, PostgreSQL veritabanının otomatik yedeklenmesini ve gerektiğinde geri yüklenebilmesini istiyorum, böylece veri güvenliği sağlanmış olsun.

#### Acceptance Criteria

1. THE Backup System SHALL her gün otomatik olarak full backup almalı
2. THE Backup System SHALL backup dosyalarını sıkıştırmalı ve şifrelemeli
3. WHEN backup başarısız olduğunda, THE Backup System SHALL sistem yöneticisine bildirim göndermeli
4. THE Backup System SHALL son 7 günlük backup'ları saklamalı ve eski backup'ları otomatik silmeli
5. THE Backup System SHALL backup'tan geri yükleme işlemi için test mekanizması sağlamalı

### Requirement 10: Veri Doğrulama ve Bütünlük Kontrolü

**User Story:** Sistem yöneticisi olarak, migration sonrası veri bütünlüğünün doğrulanmasını istiyorum, böylece tüm verilerin eksiksiz ve doğru şekilde aktarıldığından emin olabilirim.

#### Acceptance Criteria

1. THE Data Validator SHALL her tablo için kayıt sayısı karşılaştırması yapmalı
2. THE Data Validator SHALL foreign key ilişkilerini kontrol etmeli ve orphan kayıtları raporlamalı
3. THE Data Validator SHALL kritik kolonlar için checksum hesaplamalı ve karşılaştırmalı
4. WHEN veri tutarsızlığı tespit edildiğinde, THE Data Validator SHALL detaylı rapor oluşturmalı
5. THE Data Validator SHALL migration sonrası tüm constraint'lerin aktif olduğunu doğrulamalı

### Requirement 11: Konfigürasyon Yönetimi

**User Story:** Geliştirici olarak, farklı ortamlar için (development, staging, production) esnek konfigürasyon yönetimi istiyorum, böylece her ortama özel ayarlar yapılabilsin.

#### Acceptance Criteria

1. THE Database Connection Manager SHALL environment variable'lardan PostgreSQL bağlantı bilgilerini okumalı
2. THE Database Connection Manager SHALL Railway, Heroku gibi PaaS platformlarının DATABASE_URL formatını desteklemeli
3. WHERE SSL bağlantı gerekiyorsa, THE Database Connection Manager SHALL SSL sertifikalarını doğrulamalı
4. THE Database Connection Manager SHALL connection timeout, pool size gibi parametreleri environment'a göre ayarlamalı
5. THE Database Connection Manager SHALL local development için PostgreSQL Docker container desteği sağlamalı

### Requirement 12: Geriye Dönük Uyumluluk

**User Story:** Geliştirici olarak, migration sırasında mevcut kodun çalışmaya devam etmesini istiyorum, böylece aşamalı geçiş yapılabilsin.

#### Acceptance Criteria

1. THE Migration System SHALL SQLAlchemy ORM kullanarak database-agnostic kod yazılmasını sağlamalı
2. THE Migration System SHALL MySQL'e özgü SQL syntax'ını PostgreSQL'e çevirmeli
3. WHERE custom SQL sorguları varsa, THE Migration System SHALL bunları tespit edip uyarı vermeli
4. THE Migration System SHALL migration öncesi ve sonrası için test suite çalıştırmalı
5. THE Migration System SHALL rollback planı ve prosedürü sağlamalı
