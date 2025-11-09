# Otel Doluluk Yönetimi - Gereksinimler Dökümanı

## Giriş

Bu özellik, otel odalarının doluluk durumlarını Excel dosyaları üzerinden sisteme yükleyerek, kat sorumluları ve diğer yetkili kullanıcıların misafir giriş-çıkış bilgilerini takip etmelerini ve minibar kontrollerini daha verimli planlamalarını sağlar. Sistem, IN HOUSE (mevcut misafirler) ve ARRIVALS (gelecek misafirler) listelerini işleyerek oda doluluk durumlarını otomatik olarak günceller.

## Sözlük

- **Sistem**: Otel minibar yönetim sistemi
- **Depo Sorumlusu**: Excel dosyalarını yükleme yetkisine sahip kullanıcı rolü
- **Kat Sorumlusu**: Oda doluluk bilgilerini görüntüleyebilen ve minibar kontrolü yapan kullanıcı rolü
- **Sistem Yöneticisi**: Tüm verilere erişim yetkisine sahip yönetici rolü
- **IN HOUSE Listesi**: Otelde hali hazırda konaklayan misafirlerin listesi
- **ARRIVALS Listesi**: Otele giriş yapacak misafirlerin listesi
- **Excel Dosyası**: Misafir bilgilerini içeren .xlsx formatındaki dosya
- **İşlem Kodu**: Her yükleme işlemi için oluşturulan benzersiz tanımlayıcı kod
- **Oda Doluluk Durumu**: Bir odanın belirli bir tarih aralığında dolu veya boş olma durumu
- **Misafir Kayıt**: Bir odaya ait misafir giriş-çıkış bilgilerini içeren veri kaydı

## Gereksinimler

### Gereksinim 1: Excel Dosyası Yükleme

**Kullanıcı Hikayesi:** Depo sorumlusu olarak, otel doluluk bilgilerini sisteme aktarmak için Excel dosyalarını yükleyebilmeliyim ki oda durumları güncel tutulabilsin.

#### Kabul Kriterleri

1. THE Sistem SHALL depo sorumlusu panelinde sidebar menüsünde "Doluluk Yönetimi" adında yeni bir menü öğesi göstermelidir
2. WHEN depo sorumlusu "Doluluk Yönetimi" sayfasına eriştiğinde, THE Sistem SHALL iki ayrı dosya yükleme alanı sunmalıdır (IN HOUSE ve ARRIVALS için)
3. WHEN depo sorumlusu bir Excel dosyası seçtiğinde, THE Sistem SHALL dosya formatını (.xlsx) doğrulamalıdır
4. WHEN depo sorumlusu geçerli bir Excel dosyası yüklediğinde, THE Sistem SHALL dosyayı sunucuya yüklemeli ve benzersiz bir işlem kodu oluşturmalıdır
5. IF yüklenen dosya geçersiz format içeriyorsa, THEN THE Sistem SHALL kullanıcıya hata mesajı göstermeli ve yükleme işlemini iptal etmelidir

### Gereksinim 2: Excel Verilerini İşleme

**Kullanıcı Hikayesi:** Sistem olarak, yüklenen Excel dosyalarındaki verileri okuyup veritabanına kaydedebilmeliyim ki oda doluluk bilgileri güncellenebilsin.

#### Kabul Kriterleri

1. WHEN IN HOUSE dosyası yüklendiğinde, THE Sistem SHALL "Name", "Room no", "R.Type", "Arrival", "Departure", "Adult" sütunlarını okumalıdır
2. WHEN ARRIVALS dosyası yüklendiğinde, THE Sistem SHALL "Name", "Room no", "R.Type", "Hsk.St.", "Arr.Time", "Arrival", "Departure", "Adult" sütunlarını okumalıdır
3. THE Sistem SHALL "Room no" değerini oda numarası olarak, "Arrival" değerini giriş tarihi olarak, "Departure" değerini çıkış tarihi olarak, "Adult" değerini misafir sayısı olarak işlemelidir
4. WHEN Excel verisi işlenirken, THE Sistem SHALL her satır için benzersiz bir misafir kaydı oluşturmalıdır
5. THE Sistem SHALL her misafir kaydına yükleme işlem kodunu atamalıdır
6. IF Excel dosyasında geçersiz oda numarası bulunursa, THEN THE Sistem SHALL o satırı atlayarak hata loguna kaydetmelidir
7. IF Excel dosyasında geçersiz tarih formatı bulunursa, THEN THE Sistem SHALL o satırı atlayarak hata loguna kaydetmelidir

### Gereksinim 3: Oda Doluluk Durumu Güncelleme

**Kullanıcı Hikayesi:** Sistem olarak, misafir kayıtlarına göre oda doluluk durumlarını otomatik olarak güncelleyebilmeliyim ki kullanıcılar güncel bilgilere erişebilsin.

#### Kabul Kriterleri

1. WHEN yeni misafir kaydı oluşturulduğunda, THE Sistem SHALL ilgili odanın doluluk durumunu giriş ve çıkış tarihleri arasında "dolu" olarak işaretlemelidir
2. WHEN misafir çıkış tarihi geçtiğinde, THE Sistem SHALL odanın doluluk durumunu "boş" olarak güncellemelidir
3. THE Sistem SHALL her oda için mevcut ve gelecek misafir bilgilerini ayrı ayrı saklayabilmelidir
4. THE Sistem SHALL aynı odaya ait ardışık rezervasyonları doğru şekilde yönetebilmelidir
5. THE Sistem SHALL oda doluluk durumunu gerçek zamanlı olarak hesaplayabilmelidir

### Gereksinim 4: Kat Sorumlusu Oda Detay Görüntüleme

**Kullanıcı Hikayesi:** Kat sorumlusu olarak, bir odanın detaylı doluluk bilgilerini görüntüleyebilmeliyim ki minibar kontrollerimi daha iyi planlayabileyim.

#### Kabul Kriterleri

1. WHEN kat sorumlusu bir oda seçtiğinde, THE Sistem SHALL o odanın mevcut misafir bilgilerini göstermelidir (giriş tarihi, çıkış tarihi, kalan gün sayısı, misafir sayısı)
2. WHEN kat sorumlusu bir oda seçtiğinde, THE Sistem SHALL o odanın gelecek rezervasyon bilgilerini göstermelidir (giriş tarihi, çıkış tarihi, kalış süresi, misafir sayısı)
3. THE Sistem SHALL oda detay sayfasında misafir giriş tarihini, çıkış tarihini ve kalan gün sayısını hesaplayarak göstermelidir
4. THE Sistem SHALL oda detay sayfasında gelecek misafirlerin giriş tarihini ve kalış süresini göstermelidir
5. WHEN kat sorumlusu belirli bir tarih seçtiğinde, THE Sistem SHALL o tarihte kaç odanın dolu olacağını göstermelidir

### Gereksinim 5: Günlük Doluluk Raporu

**Kullanıcı Hikayesi:** Kat sorumlusu olarak, belirli bir tarihteki otel doluluk durumunu görüntüleyebilmeliyim ki o günkü iş yükümü planlayabileyim.

#### Kabul Kriterleri

1. WHEN kat sorumlusu bir tarih seçtiğinde, THE Sistem SHALL o tarihte kaç misafirin giriş yapacağını göstermelidir
2. WHEN kat sorumlusu bir tarih seçtiğinde, THE Sistem SHALL o tarihte kaç misafirin çıkış yapacağını göstermelidir
3. WHEN kat sorumlusu bir tarih seçtiğinde, THE Sistem SHALL o tarihte kaç odanın dolu olacağını göstermelidir
4. THE Sistem SHALL günlük doluluk raporunda kat bazında dolu oda listesini göstermelidir
5. THE Sistem SHALL günlük doluluk raporunda oda numaralarını ve misafir sayılarını göstermelidir

### Gereksinim 6: Yetki Yönetimi

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, tüm doluluk verilerine erişebilmeliyim ve depo sorumlusu ile kat sorumlusunun da uygun yetkilere sahip olduğundan emin olabilmeliyim.

#### Kabul Kriterleri

1. THE Sistem SHALL depo sorumlusuna Excel dosyası yükleme yetkisi vermelidir
2. THE Sistem SHALL kat sorumlusuna oda doluluk bilgilerini görüntüleme yetkisi vermelidir
3. THE Sistem SHALL sistem yöneticisine tüm doluluk verilerine erişim yetkisi vermelidir
4. THE Sistem SHALL depo sorumlusuna oda doluluk bilgilerini görüntüleme yetkisi vermelidir
5. IF yetkisiz bir kullanıcı doluluk yönetimi sayfasına erişmeye çalışırsa, THEN THE Sistem SHALL erişimi engellemeli ve hata mesajı göstermelidir

### Gereksinim 7: Hatalı Yükleme Geri Alma

**Kullanıcı Hikayesi:** Depo sorumlusu olarak, yanlışlıkla yüklediğim verileri işlem kodu ile toplu olarak silebilmeliyim ki hatalı veriler sistemde kalmasın.

#### Kabul Kriterleri

1. THE Sistem SHALL her yükleme işlemi için benzersiz bir işlem kodu oluşturmalıdır
2. THE Sistem SHALL depo sorumlusuna yükleme geçmişini ve işlem kodlarını göstermelidir
3. WHEN depo sorumlusu bir işlem kodunu seçip silme işlemi başlattığında, THE Sistem SHALL o işlem koduna ait tüm misafir kayıtlarını silmelidir
4. WHEN hatalı yükleme silindiğinde, THE Sistem SHALL ilgili oda doluluk durumlarını yeniden hesaplamalıdır
5. THE Sistem SHALL silme işlemini audit log'a kaydetmelidir

### Gereksinim 8: Otomatik Dosya Temizleme

**Kullanıcı Hikayesi:** Sistem olarak, yüklenen Excel dosyalarını belirli bir süre sonra otomatik olarak silebilmeliyim ki sunucu alanı verimli kullanılabilsin.

#### Kabul Kriterleri

1. THE Sistem SHALL yüklenen Excel dosyalarını sunucuda dört gün boyunca saklamalıdır
2. WHEN bir Excel dosyası beşinci güne ulaştığında, THE Sistem SHALL dosyayı otomatik olarak silmelidir
3. THE Sistem SHALL dosya silme işlemini günlük olarak kontrol etmelidir
4. THE Sistem SHALL silinen dosyaların kayıtlarını sistem loguna yazmalıdır
5. THE Sistem SHALL dosya silme işlemi sırasında veritabanındaki misafir kayıtlarını korumalıdır

### Gereksinim 9: Veri Doğrulama ve Hata Yönetimi

**Kullanıcı Hikayesi:** Sistem olarak, yüklenen verileri doğrulayabilmeli ve hataları kullanıcıya bildirebilmeliyim ki veri bütünlüğü korunabilsin.

#### Kabul Kriterleri

1. THE Sistem SHALL Excel dosyasındaki her satırı işlemeden önce gerekli sütunların varlığını kontrol etmelidir
2. IF gerekli bir sütun eksikse, THEN THE Sistem SHALL yükleme işlemini iptal etmeli ve kullanıcıya hata mesajı göstermelidir
3. THE Sistem SHALL oda numarasının sistemde kayıtlı olup olmadığını kontrol etmelidir
4. THE Sistem SHALL tarih formatlarının geçerli olup olmadığını kontrol etmelidir
5. THE Sistem SHALL misafir sayısının pozitif bir tam sayı olup olmadığını kontrol etmelidir
6. WHEN veri doğrulama hatası oluştuğunda, THE Sistem SHALL hata detaylarını içeren bir rapor oluşturmalıdır
7. THE Sistem SHALL başarıyla işlenen ve hata veren satır sayılarını kullanıcıya göstermelidir

### Gereksinim 10: Performans ve Ölçeklenebilirlik

**Kullanıcı Hikayesi:** Sistem olarak, büyük Excel dosyalarını verimli bir şekilde işleyebilmeliyim ki kullanıcı deneyimi olumsuz etkilenmesin.

#### Kabul Kriterleri

1. THE Sistem SHALL beş yüz satıra kadar olan Excel dosyalarını otuz saniye içinde işleyebilmelidir
2. THE Sistem SHALL dosya yükleme işlemini arka planda (asenkron) gerçekleştirmelidir
3. WHILE dosya işlenirken, THE Sistem SHALL kullanıcıya ilerleme durumunu göstermelidir
4. THE Sistem SHALL işlem tamamlandığında kullanıcıya bildirim göstermelidir
5. THE Sistem SHALL veritabanı işlemlerini toplu (batch) olarak gerçekleştirmelidir
