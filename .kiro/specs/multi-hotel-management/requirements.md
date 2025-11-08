# Çoklu Otel Yönetim Sistemi - Gereksinimler Dokümanı

## Giriş

Bu doküman, mevcut tek otel üzerinden çalışan minibar ve stok yönetim sisteminin, çoklu otel desteğine dönüştürülmesi için gerekli gereksinimleri tanımlar. Sistem, birden fazla otelin yönetilmesini, her otelin kendi kat ve oda yapısına sahip olmasını, depo ve kat sorumlularının birden fazla otele atanabilmesini sağlayacaktır.

## Sözlük (Glossary)

- **Sistem**: Minibar ve Stok Yönetim Uygulaması
- **Otel**: Yönetilen konaklama tesisi (örn: Merit Royal Diamond)
- **Kat**: Bir otele ait fiziksel kat yapısı
- **Oda**: Bir kata ait misafir odası
- **Depo Sorumlusu**: Stok giriş/çıkış ve zimmet işlemlerini yöneten kullanıcı rolü
- **Kat Sorumlusu**: Oda minibar kontrollerini yapan kullanıcı rolü
- **Zimmet**: Depo sorumlusunun kat sorumlusuna teslim ettiği ürün kayıtları
- **Sidebar**: Uygulamanın sol tarafındaki navigasyon menüsü
- **Sistem Yönetimi**: Sidebar'daki yönetim işlemlerinin bulunduğu bölüm

## Gereksinimler

### Gereksinim 1: Otel Yönetimi

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, birden fazla oteli sisteme ekleyip yönetebilmek istiyorum, böylece her otelin bağımsız operasyonlarını takip edebilirim.

#### Kabul Kriterleri

1. THE Sistem SHALL Sidebar'da "Sistem Yönetimi" bölümünde "Otel Yönetimi" menü öğesini görüntüler
2. WHEN kullanıcı "Otel Yönetimi" sayfasını açtığında, THE Sistem SHALL mevcut otellerin listesini tablo formatında gösterir
3. THE Sistem SHALL "Yeni Otel Ekle" butonu ile otel ekleme formunu sunar
4. WHEN kullanıcı otel ekleme formunu doldurduğunda, THE Sistem SHALL otel adı, adres, telefon, email ve vergi no bilgilerini kaydeder
5. THE Sistem SHALL her otel için düzenleme ve aktif/pasif yapma işlemlerini sağlar

### Gereksinim 2: Kat Yönetiminde Otel Seçimi

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, kat eklerken önce hangi otele ait olduğunu seçebilmek istiyorum, böylece katları doğru otele atayabilirim.

#### Kabul Kriterleri

1. WHEN kullanıcı "Kat Ekle" sayfasını açtığında, THE Sistem SHALL otel seçimi için dropdown listesi gösterir
2. THE Sistem SHALL dropdown listesinde aktif otelleri alfabetik sırada listeler
3. WHEN kullanıcı bir otel seçtiğinde, THE Sistem SHALL seçilen otele ait kat ekleme işlemini gerçekleştirir
4. THE Sistem SHALL kat listesi sayfasında her katın hangi otele ait olduğunu gösterir
5. WHEN kullanıcı kat düzenleme sayfasını açtığında, THE Sistem SHALL mevcut otel seçimini gösterir ve değiştirme imkanı sunar

### Gereksinim 3: Oda Yönetiminde Hiyerarşik Seçim

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, oda eklerken önce otel sonra kat seçebilmek istiyorum, böylece odaları doğru hiyerarşiye yerleştirebilirim.

#### Kabul Kriterleri

1. WHEN kullanıcı "Oda Ekle" sayfasını açtığında, THE Sistem SHALL önce otel seçimi için dropdown gösterir
2. WHEN kullanıcı bir otel seçtiğinde, THE Sistem SHALL seçilen otele ait katları ikinci dropdown'da listeler
3. WHEN kullanıcı bir kat seçtiğinde, THE Sistem SHALL oda bilgilerini girme formunu aktif eder
4. THE Sistem SHALL oda listesi sayfasında her odanın otel ve kat bilgilerini gösterir
5. WHEN kullanıcı oda düzenleme sayfasını açtığında, THE Sistem SHALL mevcut otel ve kat seçimlerini gösterir

### Gereksinim 4: Mevcut Verilere Otel Ataması

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, mevcut kat ve odaların "Merit Royal Diamond" oteline otomatik atanmasını istiyorum, böylece veri bütünlüğü korunur.

#### Kabul Kriterleri

1. WHEN sistem ilk kez çoklu otel desteğine geçtiğinde, THE Sistem SHALL "Merit Royal Diamond" adında varsayılan otel kaydı oluşturur
2. THE Sistem SHALL mevcut tüm kat kayıtlarını "Merit Royal Diamond" oteline atar
3. THE Sistem SHALL mevcut tüm oda kayıtlarının kat ilişkileri üzerinden otel bağlantısını sağlar
4. THE Sistem SHALL veri migrasyonu sırasında hiçbir kat veya oda kaydını kaybetmez
5. THE Sistem SHALL migrasyon işleminin başarılı tamamlandığını log kaydına yazar

### Gereksinim 5: Depo Sorumlusu Atamalarında Otel Seçimi

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, depo sorumlusu atarken hangi otelde çalışacağını belirleyebilmek istiyorum, böylece sorumluluk alanlarını net tanımlayabilirim.

#### Kabul Kriterleri

1. WHEN kullanıcı "Depo Sorumlusu Ekle" sayfasını açtığında, THE Sistem SHALL otel seçimi için çoklu seçim (multi-select) alanı gösterir
2. THE Sistem SHALL bir depo sorumlusunun birden fazla otele atanmasına izin verir
3. WHEN kullanıcı depo sorumlusu düzenleme sayfasını açtığında, THE Sistem SHALL mevcut otel atamalarını gösterir
4. THE Sistem SHALL depo sorumlusu listesinde her sorumluya atanan otelleri gösterir
5. THE Sistem SHALL mevcut depo sorumlularına "Merit Royal Diamond" otel atamasını otomatik ekler

### Gereksinim 6: Kat Sorumlusu Atamalarında Otel Seçimi

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, kat sorumlusu atarken hangi otelde çalışacağını belirleyebilmek istiyorum, böylece sorumluluk alanlarını net tanımlayabilirim.

#### Kabul Kriterleri

1. WHEN kullanıcı "Kat Sorumlusu Ekle" sayfasını açtığında, THE Sistem SHALL otel seçimi için tekli seçim (dropdown) alanı gösterir
2. THE Sistem SHALL bir kat sorumlusunun sadece tek bir otele atanmasına izin verir
3. WHEN kullanıcı kat sorumlusu düzenleme sayfasını açtığında, THE Sistem SHALL mevcut otel atamasını gösterir
4. THE Sistem SHALL kat sorumlusu listesinde her sorumluya atanan oteli gösterir
5. THE Sistem SHALL mevcut kat sorumlularına "Merit Royal Diamond" otel atamasını otomatik ekler

### Gereksinim 7: Çoklu Otel Depo Sorumlusu Yetkilendirmesi

**Kullanıcı Hikayesi:** Depo sorumlusu olarak, atandığım tüm otellerin stok ve zimmet işlemlerini görebilmek istiyorum, böylece birden fazla oteli yönetebilirim.

#### Kabul Kriterleri

1. WHEN depo sorumlusu sisteme giriş yaptığında, THE Sistem SHALL atandığı tüm otellerin verilerine erişim sağlar
2. THE Sistem SHALL stok hareketleri sayfasında otel filtreleme seçeneği sunar
3. THE Sistem SHALL zimmet işlemlerinde hangi otele ait olduğunu gösterir
4. WHEN depo sorumlusu zimmet verdiğinde, THE Sistem SHALL hangi otel için zimmet verildiğini kaydeder
5. THE Sistem SHALL depo sorumlusunun sadece atandığı otellerin verilerini gösterir

### Gereksinim 8: Tekli Otel Kat Sorumlusu Yetkilendirmesi

**Kullanıcı Hikayesi:** Kat sorumlusu olarak, atandığım otelin oda ve minibar işlemlerini görebilmek istiyorum, böylece sorumlu olduğum oteli yönetebilirim.

#### Kabul Kriterleri

1. WHEN kat sorumlusu sisteme giriş yaptığında, THE Sistem SHALL sadece atandığı otelin verilerine erişim sağlar
2. THE Sistem SHALL minibar işlemleri sayfasında sadece atandığı otelin odalarını gösterir
3. THE Sistem SHALL oda listesinde sadece atandığı otele ait odaları listeler
4. WHEN kat sorumlusu minibar kontrolü yaptığında, THE Sistem SHALL hangi otel için işlem yapıldığını kaydeder
5. THE Sistem SHALL kat sorumlusunun başka otellerin verilerine erişimini engeller

### Gereksinim 9: Veri Bütünlüğü ve İlişkiler

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, otel silme veya değiştirme işlemlerinde veri bütünlüğünün korunmasını istiyorum, böylece sistem tutarlı çalışır.

#### Kabul Kriterleri

1. WHEN kullanıcı bir oteli silmeye çalıştığında, THE Sistem SHALL otele ait kat veya oda varsa uyarı gösterir
2. THE Sistem SHALL otel silme işleminde cascade delete yerine aktif/pasif yapma önerir
3. WHEN bir kat başka otele taşındığında, THE Sistem SHALL kata ait tüm odaların da yeni otele bağlı kalmasını sağlar
4. THE Sistem SHALL her stok hareketi ve zimmet kaydında otel bilgisini tutar
5. THE Sistem SHALL raporlarda otel bazlı filtreleme ve gruplama sağlar

### Gereksinim 10: Kullanıcı Arayüzü ve Navigasyon

**Kullanıcı Hikayesi:** Kullanıcı olarak, otel seçimlerinin ve bilgilerinin net ve anlaşılır şekilde gösterilmesini istiyorum, böylece hata yapmadan işlem yapabilirim.

#### Kabul Kriterleri

1. THE Sistem SHALL tüm dropdown ve select listelerinde otel adlarını alfabetik sırada gösterir
2. THE Sistem SHALL otel seçimi yapılmadan kat veya oda ekleme formlarını submit etmeye izin vermez
3. THE Sistem SHALL form validasyonlarında otel seçimi zorunluluğunu kontrol eder
4. THE Sistem SHALL hata mesajlarında hangi alanın eksik olduğunu Türkçe açıklar
5. THE Sistem SHALL başarılı işlemlerde kullanıcıya bilgilendirme mesajı gösterir
