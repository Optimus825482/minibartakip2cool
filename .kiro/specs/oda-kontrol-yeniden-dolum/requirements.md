# Requirements Document

## Introduction

Bu özellik, kat sorumlusunun oda minibar kontrolü ve yeniden dolum işlemlerini daha verimli yapmasını sağlar. Mevcut sistemde "İlk Dolum" işlemi "Oda Kontrol" menüsü içinde yer almaktadır. Bu değişiklikle İlk Dolum ayrı bir menü öğesi olacak ve Oda Kontrol sadece mevcut minibar ürünlerinin kontrolü ve yeniden dolumu için kullanılacaktır.

## Glossary

- **Kat Sorumlusu Sistemi**: Kat sorumlusunun minibar işlemlerini yönettiği web arayüzü
- **Oda Kontrol**: Mevcut minibar içeriğini görüntüleme ve yeniden dolum yapma işlemi
- **İlk Dolum**: Boş bir minibar'a ilk kez ürün ekleme işlemi
- **Yeniden Dolum**: Mevcut minibar'daki eksilen ürünleri tamamlama işlemi
- **Minibar**: Otelde odada bulunan mini buzdolabı ve içindeki ürünler
- **Kat Sorumlusu Stoğu**: Kat sorumlusunun zimmetinde olan ürün stoğu
- **QR Kod Tarama**: Oda kapısındaki QR kodu okutarak oda seçimi yapma
- **Manuel Oda Seçimi**: Dropdown listeden oda numarası seçme

## Requirements

### Requirement 1

**User Story:** Kat sorumlusu olarak, İlk Dolum ve Oda Kontrol işlemlerini ayrı menü öğeleri olarak görmek istiyorum, böylece hangi işlemi yapacağımı daha net anlayabilirim.

#### Acceptance Criteria

1. WHEN Kat Sorumlusu Sistemi ana menüsü yüklendiğinde, THE Kat Sorumlusu Sistemi SHALL "İlk Dolum" ve "Oda Kontrol" seçeneklerini ayrı menü öğeleri olarak gösterecektir
2. THE Kat Sorumlusu Sistemi SHALL "İlk Dolum" menü öğesini boş minibar'lara ilk ürün ekleme işlemi için kullanacaktır
3. THE Kat Sorumlusu Sistemi SHALL "Oda Kontrol" menü öğesini mevcut minibar içeriğini görüntüleme ve yeniden dolum için kullanacaktır
4. THE Kat Sorumlusu Sistemi SHALL her iki menü öğesini de mevcut tema stiline uygun şekilde gösterecektir

### Requirement 2

**User Story:** Kat sorumlusu olarak, Oda Kontrol'de oda seçtikten sonra o minibar'daki tüm ürünleri ve miktarlarını görmek istiyorum, böylece hangi ürünlerin eksik olduğunu hızlıca görebilirim.

#### Acceptance Criteria

1. WHEN Kat Sorumlusu Sistemi Oda Kontrol sayfasında QR kod taraması yapıldığında, THE Kat Sorumlusu Sistemi SHALL seçilen odanın minibar ürün listesini gösterecektir
2. WHEN Kat Sorumlusu Sistemi Oda Kontrol sayfasında manuel oda seçimi yapıldığında, THE Kat Sorumlusu Sistemi SHALL seçilen odanın minibar ürün listesini gösterecektir
3. THE Kat Sorumlusu Sistemi SHALL her ürün için ürün adını, mevcut miktarı ve birim bilgisini gösterecektir
4. THE Kat Sorumlusu Sistemi SHALL ürün listesini okunabilir ve tıklanabilir satırlar halinde gösterecektir
5. IF seçilen odada hiç ürün yoksa, THEN THE Kat Sorumlusu Sistemi SHALL "Bu minibar'da henüz ürün bulunmamaktadır" mesajını gösterecektir

### Requirement 3

**User Story:** Kat sorumlusu olarak, ürün listesindeki bir ürüne tıkladığımda yeniden dolum yapabilmek istiyorum, böylece eksilen ürünleri hızlıca tamamlayabilirim.

#### Acceptance Criteria

1. WHEN Kat Sorumlusu Sistemi ürün listesinde bir ürün satırına tıklandığında, THE Kat Sorumlusu Sistemi SHALL yeniden dolum modalını açacaktır
2. THE Kat Sorumlusu Sistemi SHALL modal içinde ürün adını, birimini ve mevcut miktarı gösterecektir
3. THE Kat Sorumlusu Sistemi SHALL modal içinde "Eklenecek Miktar" için sayısal input alanı sunacaktır
4. THE Kat Sorumlusu Sistemi SHALL modal içinde "İptal" ve "Dolum Yap" butonlarını gösterecektir
5. THE Kat Sorumlusu Sistemi SHALL modalı mevcut tema stiline uygun şekilde tasarlayacaktır

### Requirement 4

**User Story:** Kat sorumlusu olarak, dolum yapmadan önce işlem detaylarını görmek ve onaylamak istiyorum, böylece yanlış işlem yapmamı önleyebilirim.

#### Acceptance Criteria

1. WHEN Kat Sorumlusu Sistemi yeniden dolum modalında "Dolum Yap" butonuna tıklandığında, THE Kat Sorumlusu Sistemi SHALL girilen miktarın sıfırdan büyük olduğunu kontrol edecektir
2. IF eklenecek miktar sıfır veya negatifse, THEN THE Kat Sorumlusu Sistemi SHALL "Lütfen geçerli bir miktar giriniz" hata mesajını gösterecektir
3. IF eklenecek miktar geçerliyse, THEN THE Kat Sorumlusu Sistemi SHALL onay modalını açacaktır
4. THE Kat Sorumlusu Sistemi SHALL onay modalında şu bilgileri gösterecektir: ürün adı, mevcut miktar, eklenecek miktar, yeni toplam miktar
5. THE Kat Sorumlusu Sistemi SHALL onay modalında "Kat sorumlusu stoğunuzdan [X] adet [Ürün Adı] düşecek ve minibar'a eklenecektir" bilgi mesajını gösterecektir
6. THE Kat Sorumlusu Sistemi SHALL onay modalında "İptal" ve "Onayla" butonlarını gösterecektir

### Requirement 5

**User Story:** Kat sorumlusu olarak, dolum işlemini onayladığımda stoğumdan düşüş yapılmasını ve minibar'a ekleme yapılmasını istiyorum, böylece stok takibi doğru şekilde yapılabilir.

#### Acceptance Criteria

1. WHEN Kat Sorumlusu Sistemi onay modalında "Onayla" butonuna tıklandığında, THE Kat Sorumlusu Sistemi SHALL kat sorumlusu stoğunda yeterli ürün olduğunu kontrol edecektir
2. IF kat sorumlusu stoğunda yeterli ürün yoksa, THEN THE Kat Sorumlusu Sistemi SHALL "Stoğunuzda yeterli [Ürün Adı] bulunmamaktadır" hata mesajını gösterecektir
3. IF kat sorumlusu stoğunda yeterli ürün varsa, THEN THE Kat Sorumlusu Sistemi SHALL kat sorumlusu stoğundan belirtilen miktarı düşecektir
4. THE Kat Sorumlusu Sistemi SHALL minibar zimmet detayında ürün miktarını artıracaktır
5. THE Kat Sorumlusu Sistemi SHALL işlemi zimmet hareketleri tablosuna "Yeniden Dolum" tipi olarak kaydedecektir
6. THE Kat Sorumlusu Sistemi SHALL işlem başarılı olduğunda "Dolum işlemi başarıyla tamamlandı" başarı mesajını gösterecektir
7. THE Kat Sorumlusu Sistemi SHALL tüm modalları kapatacak ve güncel ürün listesini gösterecektir

### Requirement 6

**User Story:** Kat sorumlusu olarak, dolum işlemi sırasında hata oluşursa bilgilendirilmek istiyorum, böylece sorunu anlayıp gerekli aksiyonu alabilirim.

#### Acceptance Criteria

1. IF dolum işlemi sırasında veritabanı hatası oluşursa, THEN THE Kat Sorumlusu Sistemi SHALL "İşlem sırasında bir hata oluştu. Lütfen tekrar deneyiniz" hata mesajını gösterecektir
2. IF dolum işlemi sırasında beklenmeyen bir hata oluşursa, THEN THE Kat Sorumlusu Sistemi SHALL hatayı loglayacak ve kullanıcıya genel hata mesajı gösterecektir
3. THE Kat Sorumlusu Sistemi SHALL hata durumunda hiçbir stok değişikliği yapmayacaktır (transaction rollback)
4. THE Kat Sorumlusu Sistemi SHALL hata mesajlarını tema stiline uygun şekilde gösterecektir
