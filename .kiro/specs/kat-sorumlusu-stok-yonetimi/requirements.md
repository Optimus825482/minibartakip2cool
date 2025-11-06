# Requirements Document

## Introduction

Bu özellik, Kat Sorumlusu panelini geliştirerek Depo Sorumlusu panelindeki gibi gelişmiş stok yönetimi özellikleri ekler. Kat sorumluları kendilerine aktarılan stoklarını görebilecek, kritik stok seviyelerini belirleyebilecek, azalan ürünleri takip edebilecek ve otomatik sipariş hazırlayabilecekler. Ayrıca stokout olacak veya olabilecek ürünleri proaktif olarak takip edebilecekler.

## Glossary

- **Sistem**: Minibar Takip Sistemi
- **Kat Sorumlusu**: Otelde belirli bir kattan sorumlu olan ve minibar işlemlerini yöneten personel
- **Zimmet**: Kat sorumlusuna depo tarafından teslim edilen ürün stoğu
- **Kritik Stok Seviyesi**: Bir ürünün minimum bulunması gereken miktarı, bu seviyenin altına düşünce uyarı verilir
- **Stokout**: Bir ürünün stokta hiç kalmaması durumu
- **Otomatik Sipariş**: Kritik stok seviyesine düşen ürünler için sistem tarafından önerilen sipariş listesi
- **Aktif Zimmet**: Henüz tamamlanmamış, kullanımda olan zimmet kaydı
- **Kalan Miktar**: Zimmetten henüz kullanılmamış ürün miktarı

## Requirements

### Requirement 1: Aktarılan Stokları Görüntüleme

**User Story:** Kat sorumlusu olarak, kendime aktarılan tüm zimmet stoklarını detaylı bir şekilde görmek istiyorum, böylece elimdeki ürünleri takip edebilirim.

#### Acceptance Criteria

1. WHEN Kat Sorumlusu "Zimmet Stoklarım" sayfasını açtığında, THE Sistem SHALL tüm aktif zimmet kayıtlarını listeler
2. WHILE Kat Sorumlusu zimmet listesini görüntülerken, THE Sistem SHALL her zimmet için teslim tarihi, teslim eden kişi, toplam ürün sayısı ve durum bilgilerini gösterir
3. WHEN Kat Sorumlusu bir zimmet kaydına tıkladığında, THE Sistem SHALL o zimmetteki tüm ürünlerin detaylarını (ürün adı, teslim edilen miktar, kullanılan miktar, kalan miktar) gösterir
4. WHERE Kat Sorumlusunun birden fazla aktif zimmeti varsa, THE Sistem SHALL zimmetleri tarihe göre sıralı şekilde gösterir
5. WHEN Kat Sorumlusu zimmet detaylarını görüntülediğinde, THE Sistem SHALL her ürün için kullanım yüzdesini görsel olarak (progress bar) gösterir

### Requirement 2: Kritik Stok Seviyesi Belirleme

**User Story:** Kat sorumlusu olarak, zimmetimdeki her ürün için kritik stok seviyesi belirlemek istiyorum, böylece hangi ürünlerin azaldığını otomatik olarak görebilirim.

#### Acceptance Criteria

1. WHEN Kat Sorumlusu zimmet detay sayfasında bir ürünün yanındaki "Kritik Seviye Belirle" butonuna tıkladığında, THE Sistem SHALL kritik stok seviyesi girişi için bir modal pencere açar
2. WHEN Kat Sorumlusu kritik stok seviyesini girip kaydettiğinde, THE Sistem SHALL bu değeri veritabanına kaydeder ve başarı mesajı gösterir
3. WHILE Kat Sorumlusu kritik seviye belirlerken, THE Sistem SHALL girilen değerin pozitif bir tam sayı olmasını zorunlu kılar
4. WHEN Kat Sorumlusu daha önce belirlenmiş kritik seviyeyi değiştirmek istediğinde, THE Sistem SHALL mevcut değeri gösterir ve güncelleme yapılmasına izin verir
5. IF Kat Sorumlusu geçersiz bir değer girerse, THEN THE Sistem SHALL hata mesajı gösterir ve kaydetmez

### Requirement 3: Azalan Ürünleri Görüntüleme

**User Story:** Kat sorumlusu olarak, kritik stok seviyesinin altına düşen veya düşmek üzere olan ürünleri görmek istiyorum, böylece zamanında sipariş verebilirim.

#### Acceptance Criteria

1. WHEN Kat Sorumlusu dashboard'a girdiğinde, THE Sistem SHALL kritik seviyenin altındaki ürünleri kırmızı renkle vurgular
2. WHEN Kat Sorumlusu "Kritik Stoklar" sayfasını açtığında, THE Sistem SHALL kritik seviyenin altındaki tüm ürünleri listeler
3. WHILE Kat Sorumlusu kritik stok listesini görüntülerken, THE Sistem SHALL her ürün için kalan miktar, kritik seviye ve eksik miktar bilgilerini gösterir
4. WHERE bir ürün kritik seviyenin %20 üzerindeyse, THE Sistem SHALL o ürünü sarı renkle (uyarı) gösterir
5. WHEN bir ürünün stoğu sıfıra düştüğünde, THE Sistem SHALL o ürünü "Stokout" olarak işaretler ve en üstte gösterir

### Requirement 4: Otomatik Sipariş Hazırlama

**User Story:** Kat sorumlusu olarak, kritik seviyedeki ürünler için otomatik sipariş listesi oluşturmak istiyorum, böylece depodan hızlıca talep edebilirim.

#### Acceptance Criteria

1. WHEN Kat Sorumlusu "Sipariş Hazırla" butonuna tıkladığında, THE Sistem SHALL kritik seviyedeki tüm ürünler için otomatik sipariş listesi oluşturur
2. WHILE Sistem sipariş listesi oluştururken, THE Sistem SHALL her ürün için önerilen sipariş miktarını (kritik seviye - kalan miktar + güvenlik marjı) hesaplar
3. WHEN Kat Sorumlusu sipariş listesini görüntülediğinde, THE Sistem SHALL her ürün için mevcut stok, kritik seviye ve önerilen sipariş miktarını gösterir
4. WHERE Kat Sorumlusu sipariş miktarlarını düzenlemek isterse, THE Sistem SHALL manuel düzenleme yapılmasına izin verir
5. WHEN Kat Sorumlusu siparişi onayladığında, THE Sistem SHALL sipariş talebini kaydeder ve depo sorumlusuna bildirim gönderir

### Requirement 5: Stokout Takibi ve Uyarılar

**User Story:** Kat sorumlusu olarak, stokout olan veya olabilecek ürünleri proaktif olarak takip etmek istiyorum, böylece misafir memnuniyetsizliği yaşanmaz.

#### Acceptance Criteria

1. WHEN bir ürünün stoğu sıfıra düştüğünde, THE Sistem SHALL Kat Sorumlusuna anında bildirim gösterir
2. WHEN Kat Sorumlusu dashboard'a girdiğinde, THE Sistem SHALL stokout ürün sayısını belirgin bir şekilde gösterir
3. WHILE Kat Sorumlusu "Stokout Ürünler" sayfasını görüntülerken, THE Sistem SHALL stokout olan tüm ürünleri ve son kullanım tarihlerini listeler
4. WHERE bir ürün kritik seviyenin %50'sinin altına düştüğünde, THE Sistem SHALL o ürünü "Stokout Riski" olarak işaretler
5. WHEN Kat Sorumlusu bir stokout ürün için acil sipariş verdiğinde, THE Sistem SHALL siparişi "Acil" önceliğiyle işaretler ve kaydeder

### Requirement 6: Stok Hareketleri Geçmişi

**User Story:** Kat sorumlusu olarak, zimmetimdeki ürünlerin kullanım geçmişini görmek istiyorum, böylece tüketim trendlerini analiz edebilirim.

#### Acceptance Criteria

1. WHEN Kat Sorumlusu bir ürünün detay sayfasını açtığında, THE Sistem SHALL o ürünün son 30 günlük kullanım geçmişini gösterir
2. WHILE Kat Sorumlusu geçmiş hareketleri görüntülerken, THE Sistem SHALL her hareket için tarih, işlem tipi, miktar ve oda bilgilerini gösterir
3. WHERE Kat Sorumlusu tarih filtresi uygulamak isterse, THE Sistem SHALL belirtilen tarih aralığındaki hareketleri gösterir
4. WHEN Kat Sorumlusu "Grafik Görünümü" seçeneğini seçtiğinde, THE Sistem SHALL günlük tüketim grafiğini gösterir
5. WHEN Kat Sorumlusu geçmiş verileri Excel'e aktarmak istediğinde, THE Sistem SHALL verileri Excel formatında indirir

### Requirement 7: Dashboard İyileştirmeleri

**User Story:** Kat sorumlusu olarak, dashboard'da stok durumumu özetleyen kartlar ve grafikler görmek istiyorum, böylece hızlıca genel durumu anlayabilirim.

#### Acceptance Criteria

1. WHEN Kat Sorumlusu dashboard'a girdiğinde, THE Sistem SHALL toplam zimmet ürün sayısı, kritik stok sayısı, stokout ürün sayısı ve bugünkü kullanım kartlarını gösterir
2. WHILE Kat Sorumlusu dashboard'u görüntülerken, THE Sistem SHALL en çok kullanılan 5 ürünü grafik olarak gösterir
3. WHERE kritik stok veya stokout ürün varsa, THE Sistem SHALL bu kartları kırmızı renkle vurgular
4. WHEN Kat Sorumlusu bir karta tıkladığında, THE Sistem SHALL ilgili detay sayfasına yönlendirir
5. WHEN Kat Sorumlusu "Yenile" butonuna tıkladığında, THE Sistem SHALL tüm dashboard verilerini gerçek zamanlı olarak günceller
