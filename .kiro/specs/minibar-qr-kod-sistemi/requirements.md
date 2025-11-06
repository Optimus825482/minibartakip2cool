# Requirements Document

## Introduction

Bu doküman, otel minibar yönetim sistemine QR kod tabanlı oda tanıma ve işlem başlatma özelliğinin eklenmesini tanımlar. Sistem, kat sorumlusunun iş yükünü azaltacak, misafirlere self-servis dolum talebi imkanı sunacak ve minibar işlemlerinin zaman damgalı takibini sağlayacaktır.

## Glossary

- **Sistem**: Otel minibar yönetim web uygulaması
- **QR Kod**: Her odaya özgü, oda ve kat bilgilerini içeren Quick Response kodu
- **Admin Paneli**: Sistem yöneticisinin oda tanımları ve ayarları yaptığı arayüz
- **Kat Sorumlusu Paneli**: Kat sorumlusunun minibar işlemlerini gerçekleştirdiği arayüz
- **Minibar İşlemi**: Oda minibarına ürün ekleme, çıkarma veya sayım yapma işlemi
- **Dolum Talebi**: Misafirin minibar doldurulması için yaptığı talep
- **Oda Tanımı**: Sistemde kayıtlı oda bilgileri (kat, oda numarası, durum)
- **QR Okuyucu**: Mobil cihazın kamera özelliğini kullanarak QR kod okuma fonksiyonu
- **Toplu QR Oluşturma**: Birden fazla oda için aynı anda QR kod üretme işlemi
- **Misafir Mesajı**: QR kod okutulduğunda misafire gösterilen dolum talebi açıklama metni

## Requirements

### Requirement 1

**User Story:** Admin olarak, yeni oda tanımlarken otomatik QR kod oluşturulmasını istiyorum, böylece her oda için benzersiz bir QR kod hazır olsun.

#### Acceptance Criteria

1. WHEN admin panelinde yeni bir oda kaydedildiğinde, THE Sistem SHALL o oda için benzersiz bir QR kod oluşturur
2. THE Sistem SHALL QR kod URL'ini oluştururken çalıştığı domain adresini otomatik olarak algılar
3. THE QR Kod SHALL oda ID'si, kat numarası ve oda numarasını içeren parametrelerle URL encode eder
4. THE Sistem SHALL oluşturulan QR kod görselini veritabanında saklar
5. THE Sistem SHALL QR kod oluşturma işleminin başarısız olması durumunda admin kullanıcıya hata mesajı gösterir

### Requirement 2

**User Story:** Admin olarak, mevcut tüm odalar için toplu QR kod oluşturabilmek istiyorum, böylece sistemdeki eski kayıtlar için de QR kodları hazırlayabileyim.

#### Acceptance Criteria

1. THE Admin Paneli SHALL oda tanımları sayfasında "Tüm Odalar İçin QR Oluştur" butonu gösterir
2. WHEN admin "Tüm Odalar İçin QR Oluştur" butonuna tıkladığında, THE Sistem SHALL sistemdeki tüm odalar için QR kod oluşturur
3. THE Sistem SHALL QR kodu olmayan odalar için "QR Kodu Olmayan Odalar İçin QR Oluştur" butonu gösterir
4. WHEN admin "QR Kodu Olmayan Odalar İçin QR Oluştur" butonuna tıkladığında, THE Sistem SHALL sadece QR kodu olmayan odalar için QR kod oluşturur
5. THE Sistem SHALL toplu QR oluşturma işlemi sırasında ilerleme durumunu kullanıcıya gösterir
6. THE Sistem SHALL toplu işlem tamamlandığında kaç adet QR kod oluşturulduğunu bildirir

### Requirement 3

**User Story:** Admin olarak, her oda için misafire gösterilecek minibar dolum talebi mesajını özelleştirebilmek istiyorum, böylece oda tipine göre farklı mesajlar verebileyim.

#### Acceptance Criteria

1. THE Admin Paneli SHALL oda tanımları listesinde her oda için "Misafir Mesajını Düzenle" seçeneği gösterir
2. WHEN admin bir odanın misafir mesajını düzenlediğinde, THE Sistem SHALL girilen metni o oda kaydına kaydeder
3. THE Sistem SHALL misafir mesajı alanının maksimum 500 karakter uzunluğunda olmasını sağlar
4. WHERE misafir mesajı tanımlanmamışsa, THE Sistem SHALL varsayılan bir mesaj gösterir
5. THE Sistem SHALL misafir mesajında HTML injection saldırılarına karşı input validasyonu yapar

### Requirement 4

**User Story:** Kat sorumlusu olarak, odadaki QR kodu okutarak minibar işlemlerine başlamak istiyorum, böylece kat ve oda numarasını manuel seçmek zorunda kalmayayım.

#### Acceptance Criteria

1. THE Kat Sorumlusu Paneli SHALL minibar işlemleri sayfasında "QR Kod ile Başla" butonu gösterir
2. WHEN kat sorumlusu "QR Kod ile Başla" butonuna tıkladığında, THE Sistem SHALL mobil cihazın kamerasını QR okuyucu olarak açar
3. WHEN kat sorumlusu kat sorumlusu paneli içinden geçerli bir oda QR kodu okuttuğunda, THE Sistem SHALL QR koddan oda ve kat bilgilerini parse eder
4. THE Sistem SHALL parse edilen oda bilgilerini minibar işlem formunda otomatik olarak doldurur
5. THE Sistem SHALL QR kod okutma işleminin zaman damgasını kaydeder
6. IF geçersiz veya tanınmayan bir QR kod okutulursa, THEN THE Sistem SHALL kat sorumlusuna hata mesajı gösterir
7. THE Sistem SHALL QR kod okuma işlemi sırasında ağ bağlantısı kesilirse kullanıcıya bilgi mesajı gösterir

### Requirement 5

**User Story:** Kat sorumlusu olarak, QR kod okutarak başlattığım işlemlerin kaydının tutulmasını istiyorum, böylece hangi odaya ne zaman gittiğim takip edilebilsin.

#### Acceptance Criteria

1. WHEN kat sorumlusu QR kod okutarak minibar işlemi başlattığında, THE Sistem SHALL işlem kaydına "QR Kod ile Başlatıldı" bilgisini ekler
2. THE Sistem SHALL QR kod okutma zamanını işlem kaydında saklar
3. THE Sistem SHALL hangi kat sorumlusunun hangi odaya ne zaman gittiğini raporlayabilir
4. THE Sistem SHALL QR kod ile başlatılan işlemleri manuel başlatılan işlemlerden ayırt edebilir
5. THE Sistem SHALL QR kod okutma geçmişini en az 90 gün boyunca saklar

### Requirement 6

**User Story:** Misafir olarak, odamdaki minibar QR kodunu okutarak dolum talebi yapabilmek istiyorum, böylece resepsiyonu aramadan talepte bulunabileyim.

#### Acceptance Criteria

1. WHEN QR kod kat sorumlusu paneli dışında bir yerden (normal tarayıcı, başka uygulama, başka cihaz) okutulduğunda, THE Sistem SHALL otomatik olarak misafir dolum talebi sayfasına yönlendirir
2. THE Sistem SHALL misafir dolum talebi sayfasında o oda için tanımlanan özel mesajı gösterir
3. THE Sistem SHALL misafir dolum talebi sayfasında "Dolum Talebi Gönder" butonu gösterir
4. WHEN misafir dolum talebi gönderdiğinde, THE Sistem SHALL talebi oda numarası ve zaman damgası ile kaydeder
5. THE Sistem SHALL dolum talebini kat sorumlusu panelinde bildirim olarak gösterir
6. THE Sistem SHALL misafir dolum talebinin başarıyla gönderildiğini onay mesajı ile bildirir
7. THE Sistem SHALL QR kod URL'inden oda bilgilerini otomatik olarak parse ederek dolum talebine ekler

### Requirement 7

**User Story:** Admin olarak, oluşturulan QR kodları görüntüleyebilmek ve indirebilmek istiyorum, böylece bunları yazdırıp odalara yerleştirebileyim.

#### Acceptance Criteria

1. THE Admin Paneli SHALL oda listesinde her oda için "QR Kodu Görüntüle" seçeneği gösterir
2. WHEN admin bir odanın QR kodunu görüntülediğinde, THE Sistem SHALL QR kod görselini modal pencerede gösterir
3. THE Sistem SHALL QR kod görselini PNG formatında indirme seçeneği sunar
4. THE Sistem SHALL QR kod görselini yazdırma seçeneği sunar
5. THE Sistem SHALL QR kod görselinde oda numarası ve kat bilgisini metin olarak da gösterir
6. THE Sistem SHALL toplu QR kod indirme seçeneği sunar (ZIP dosyası olarak)

### Requirement 8

**User Story:** Sistem yöneticisi olarak, QR kod sisteminin güvenli olmasını istiyorum, böylece yetkisiz kişiler sahte QR kodlarla sisteme erişemesin.

#### Acceptance Criteria

1. THE Sistem SHALL QR kod URL'lerinde güvenlik token'ı kullanır
2. THE Sistem SHALL her QR kod için benzersiz ve tahmin edilemez bir token oluşturur
3. WHEN QR kod okutulduğunda, THE Sistem SHALL token'ın geçerliliğini doğrular
4. IF geçersiz veya manipüle edilmiş bir token algılanırsa, THEN THE Sistem SHALL erişimi reddeder ve güvenlik loguna kaydeder
5. THE Sistem SHALL QR kod token'larının süresi dolmaz ancak oda silindiğinde geçersiz hale gelir
6. THE Sistem SHALL QR kod erişim denemelerini rate limiting ile sınırlar (dakikada maksimum 10 deneme)
