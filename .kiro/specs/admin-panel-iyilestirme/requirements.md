# Admin Panel İyileştirme - Gereksinimler Dokümanı

## Giriş

Bu doküman, Minibar Takip Sistemi'ndeki Admin rolüne sahip kullanıcıların sistem genelinde tam erişim yetkisine sahip olması ve sidebar menü yapısının profesyonel ve işlevsel hale getirilmesi için hazırlanmıştır. Admin kullanıcıları, Railway Sync ve geliştirici işlemleri hariç, sistemdeki tüm modüllere erişebilecek ve tüm CRUD operasyonlarını gerçekleştirebilecektir.

## Sözlük

- **Admin**: Sistem yöneticisi yetkilerine sahip ancak Railway Sync işlemlerine erişimi olmayan kullanıcı rolü
- **Sistem Yöneticisi**: Tüm yetkilere sahip en üst düzey kullanıcı rolü
- **CRUD**: Create (Oluşturma), Read (Okuma), Update (Güncelleme), Delete (Silme) işlemleri
- **Sidebar**: Uygulamanın sol tarafında yer alan navigasyon menüsü
- **Depo Stokları**: Depodaki ürün stok durumları
- **Minibar Stokları**: Odalardaki minibar ürün stok durumları
- **Minibar İşlemleri**: Minibar kontrol, doldurma ve tüketim kayıtları
- **Personel Zimmet**: Kat sorumlularına verilen ürün zimmet kayıtları
- **Stok Hareketleri**: Depoya giriş ve çıkış yapan ürün hareketleri
- **Audit Trail**: Sistem denetim kayıtları
- **Railway Sync**: Uzak sunucu ile veritabanı senkronizasyon işlemleri

## Gereksinimler

### Gereksinim 1: Admin Sidebar Menü Yapısı

**Kullanıcı Hikayesi:** Admin rolüne sahip bir kullanıcı olarak, sistemdeki tüm modüllere kolayca erişebilmek için profesyonel ve organize edilmiş bir sidebar menüsüne ihtiyacım var.

#### Kabul Kriterleri

1. WHEN Admin kullanıcı sisteme giriş yaptığında, THE Sidebar MUST kullanıcıya tüm erişilebilir modülleri kategorize edilmiş şekilde gösterir
2. THE Sidebar MUST aşağıdaki kategori başlıklarını içerir: "Panel", "Sistem Yönetimi", "Ürün Yönetimi", "Kullanıcı Yönetimi", "Depo Yönetimi", "Minibar Yönetimi", "Raporlar", "Güvenlik & Denetim"
3. THE Sidebar MUST her menü öğesi için uygun ve anlaşılır ikonlar gösterir
4. THE Sidebar MUST aktif sayfayı görsel olarak vurgular
5. THE Sidebar MUST mobil cihazlarda responsive olarak çalışır

### Gereksinim 2: Depo Yönetimi Erişimi

**Kullanıcı Hikayesi:** Admin kullanıcı olarak, depo stok durumlarını görüntüleyebilmek, stok girişi yapabilmek ve stok hareketlerini takip edebilmek istiyorum.

#### Kabul Kriterleri

1. WHEN Admin kullanıcı "Depo Stokları" menüsüne tıkladığında, THE Sistem MUST tüm ürünlerin güncel stok durumlarını listeler
2. WHEN Admin kullanıcı "Stok Girişi" sayfasına eriştiğinde, THE Sistem MUST yeni stok girişi yapma formunu gösterir
3. WHEN Admin kullanıcı "Stok Hareketleri" sayfasına eriştiğinde, THE Sistem MUST tüm giriş ve çıkış hareketlerini tarih, ürün ve miktar bilgileriyle listeler
4. THE Sistem MUST Admin kullanıcının stok hareketlerini filtreleyebilmesine izin verir
5. THE Sistem MUST Admin kullanıcının stok raporlarını Excel formatında dışa aktarabilmesine izin verir

### Gereksinim 3: Minibar Yönetimi Tam Erişimi

**Kullanıcı Hikayesi:** Admin kullanıcı olarak, tüm odaların minibar durumlarını görüntüleyebilmek, minibar işlemlerini takip edebilmek ve gerektiğinde müdahale edebilmek istiyorum.

#### Kabul Kriterleri

1. WHEN Admin kullanıcı "Oda Minibar Stokları" sayfasına eriştiğinde, THE Sistem MUST tüm odaların güncel minibar stok durumlarını listeler
2. WHEN Admin kullanıcı "Minibar İşlemleri" sayfasına eriştiğinde, THE Sistem MUST tüm minibar kontrol, doldurma ve tüketim kayıtlarını listeler
3. WHEN Admin kullanıcı bir minibar işlem kaydına tıkladığında, THE Sistem MUST işlem detaylarını (tarih, personel, oda, ürünler, miktarlar) gösterir
4. THE Sistem MUST Admin kullanıcının minibar işlemlerini düzenleyebilmesine izin verir
5. THE Sistem MUST Admin kullanıcının hatalı minibar işlemlerini silebilmesine izin verir
6. WHEN Admin kullanıcı bir minibar işlemini sildiğinde, THE Sistem MUST ilgili stok hareketlerini geri alır ve audit log kaydı oluşturur

### Gereksinim 4: Personel Zimmet Yönetimi

**Kullanıcı Hikayesi:** Admin kullanıcı olarak, tüm personel zimmet kayıtlarını görüntüleyebilmek, zimmet durumlarını takip edebilmek ve gerektiğinde zimmet kayıtlarını düzenleyebilmek istiyorum.

#### Kabul Kriterleri

1. WHEN Admin kullanıcı "Personel Zimmetleri" sayfasına eriştiğinde, THE Sistem MUST tüm aktif ve tamamlanmış zimmet kayıtlarını listeler
2. WHEN Admin kullanıcı bir zimmet kaydına tıkladığında, THE Sistem MUST zimmet detaylarını (personel, tarih, ürünler, miktarlar, kullanım, iade) gösterir
3. THE Sistem MUST Admin kullanıcının zimmet kayıtlarını düzenleyebilmesine izin verir
4. THE Sistem MUST Admin kullanıcının zimmet iade işlemlerini yapabilmesine izin verir
5. WHEN Admin kullanıcı bir zimmet kaydını iptal ettiğinde, THE Sistem MUST ilgili stok hareketlerini geri alır ve audit log kaydı oluşturur

### Gereksinim 5: Raporlama ve Analiz Erişimi

**Kullanıcı Hikayesi:** Admin kullanıcı olarak, sistem genelindeki tüm raporlara erişebilmek ve detaylı analizler yapabilmek istiyorum.

#### Kabul Kriterleri

1. WHEN Admin kullanıcı "Raporlar" menüsüne eriştiğinde, THE Sistem MUST tüm rapor türlerini kategorize edilmiş şekilde listeler
2. THE Sistem MUST Admin kullanıcının "Depo Stok Raporu", "Minibar Tüketim Raporu", "Kat Bazlı Rapor", "Personel Zimmet Raporu" ve "Stok Hareket Raporu" oluşturabilmesine izin verir
3. WHEN Admin kullanıcı bir rapor oluşturduğunda, THE Sistem MUST tarih aralığı, ürün grubu, kat ve personel filtrelerini sunmalıdır
4. THE Sistem MUST raporları Excel ve PDF formatlarında dışa aktarma seçeneği sunmalıdır
5. THE Sistem MUST rapor oluşturma işlemlerini audit log'a kaydetmelidir

### Gereksinim 6: İşlem Kayıtları Yönetimi

**Kullanıcı Hikayesi:** Admin kullanıcı olarak, sistemdeki tüm işlem kayıtlarını görüntüleyebilmek, detaylarını inceleyebilmek ve gerektiğinde düzeltme yapabilmek istiyorum.

#### Kabul Kriterleri

1. WHEN Admin kullanıcı "Stok Hareketleri" sayfasına eriştiğinde, THE Sistem MUST tüm stok giriş ve çıkış kayıtlarını listeler
2. WHEN Admin kullanıcı "Minibar İşlem Geçmişi" sayfasına eriştiğinde, THE Sistem MUST tüm minibar işlem kayıtlarını listeler
3. THE Sistem MUST Admin kullanıcının işlem kayıtlarını tarih, personel, ürün ve işlem tipi kriterlerine göre filtreleyebilmesine izin verir
4. WHEN Admin kullanıcı bir işlem kaydını düzenlediğinde, THE Sistem MUST değişiklik öncesi ve sonrası durumu audit log'a kaydetmelidir
5. THE Sistem MUST Admin kullanıcının hatalı işlem kayıtlarını silebilmesine izin verir ve silme işlemini audit log'a kaydetmelidir

### Gereksinim 7: Güvenlik ve Denetim

**Kullanıcı Hikayesi:** Admin kullanıcı olarak, sistem güvenliğini sağlamak ve tüm işlemleri denetleyebilmek için audit trail kayıtlarına erişebilmek istiyorum.

#### Kabul Kriterleri

1. WHEN Admin kullanıcı "Audit Trail" sayfasına eriştiğinde, THE Sistem MUST tüm kullanıcı işlemlerini kronolojik sırada listeler
2. THE Sistem MUST her audit kaydı için kullanıcı, işlem tipi, tablo, kayıt ID, eski değer, yeni değer, tarih ve IP adresi bilgilerini gösterir
3. THE Sistem MUST Admin kullanıcının audit kayıtlarını kullanıcı, işlem tipi, tablo ve tarih kriterlerine göre filtreleyebilmesine izin verir
4. THE Sistem MUST Admin kullanıcının audit kayıtlarını Excel formatında dışa aktarabilmesine izin verir
5. THE Sistem MUST Admin kullanıcının sistem log kayıtlarını görüntüleyebilmesine izin verir

### Gereksinim 8: Railway Sync Kısıtlaması

**Kullanıcı Hikayesi:** Sistem geliştirici olarak, Railway Sync işlemlerinin sadece sistem yöneticisi tarafından kullanılabilmesini ve Admin kullanıcılarının bu işlemlere erişememesini istiyorum.

#### Kabul Kriterleri

1. THE Sistem MUST Admin kullanıcıların sidebar menüsünde "Railway Sync" öğesini göstermez
2. WHEN Admin kullanıcı Railway Sync URL'ine doğrudan erişmeye çalıştığında, THE Sistem MUST "Yetkisiz Erişim" hatası gösterir ve kullanıcıyı dashboard'a yönlendirir
3. THE Sistem MUST Railway Sync yetkisiz erişim denemelerini audit log'a kaydetmelidir
4. THE Sistem MUST sadece "sistem_yoneticisi" rolüne sahip kullanıcıların Railway Sync işlemlerine erişmesine izin verir

### Gereksinim 9: Sidebar Menü Organizasyonu

**Kullanıcı Hikayesi:** Admin kullanıcı olarak, sidebar menüsünün mantıksal ve kullanıcı dostu bir şekilde organize edilmesini istiyorum.

#### Kabul Kriterleri

1. THE Sidebar MUST menü öğelerini aşağıdaki sırayla gruplandırır: "Panel", "Sistem Yönetimi", "Ürün Yönetimi", "Kullanıcı Yönetimi", "Depo Yönetimi", "Minibar Yönetimi", "Raporlar", "Güvenlik & Denetim"
2. THE Sidebar MUST her kategori başlığını görsel olarak ayırt edilebilir şekilde gösterir
3. THE Sidebar MUST her menü öğesi için tutarlı ikon seti kullanır
4. THE Sidebar MUST aktif sayfayı farklı renk veya arka plan ile vurgular
5. THE Sidebar MUST mobil cihazlarda hamburger menü ile açılıp kapanabilir olmalıdır

### Gereksinim 10: Performans ve Kullanılabilirlik

**Kullanıcı Hikayesi:** Admin kullanıcı olarak, sistemin hızlı ve akıcı çalışmasını ve kullanıcı dostu bir arayüze sahip olmasını istiyorum.

#### Kabul Kriterleri

1. WHEN Admin kullanıcı bir sayfaya eriştiğinde, THE Sistem MUST sayfa içeriğini 2 saniye içinde yüklemelidir
2. WHEN Admin kullanıcı bir liste sayfasında arama yaptığında, THE Sistem MUST sonuçları 1 saniye içinde göstermelidir
3. THE Sistem MUST tüm liste sayfalarında sayfalama (pagination) özelliği sunmalıdır
4. THE Sistem MUST kullanıcı işlemlerinde başarı ve hata mesajlarını görsel olarak net bir şekilde göstermelidir
5. THE Sistem MUST kritik işlemler (silme, sıfırlama) için onay dialogları göstermelidir
