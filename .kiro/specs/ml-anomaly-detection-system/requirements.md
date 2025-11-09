# Requirements Document

## Introduction

Bu doküman, minibar yönetim sistemine entegre edilecek makine öğrenmesi tabanlı anomali tespit ve uyarı sisteminin gereksinimlerini tanımlar. Sistem, stok seviyeleri, tüketim miktarları, dolum süreleri ve diğer operasyonel metrikleri sürekli izleyerek anormal durumları tespit edecek ve admin panelinde proaktif uyarılar gösterecektir. Sistem, zaman içinde öğrenerek kendini geliştirecek ve daha doğru tahminler yapacaktır.

## Glossary

- **ML_System**: Makine öğrenmesi tabanlı anomali tespit ve uyarı sistemi
- **Anomaly**: Normal operasyonel davranıştan sapma gösteren durum
- **Metric**: İzlenen ölçülebilir veri noktası (stok seviyesi, dolum süresi, vb.)
- **Alert**: Admin panelinde gösterilen uyarı bildirimi
- **Training_Data**: Sistemin öğrenmesi için kullanılan geçmiş veriler
- **Threshold**: Anomali tespiti için belirlenen eşik değeri
- **Dashboard**: Admin panelinde uyarıların ve metriklerin gösterildiği arayüz
- **Learning_Model**: Verileri analiz eden ve tahmin yapan makine öğrenmesi modeli
- **Admin_User**: Sistem yöneticisi veya yetkili kullanıcı

## Requirements

### Requirement 1: Stok Seviyesi İzleme ve Anomali Tespiti

**User Story:** Admin kullanıcı olarak, stok seviyelerindeki anormal düşüşleri otomatik tespit eden bir sistem istiyorum, böylece stok tükenmeden önce proaktif aksiyon alabilirim.

#### Acceptance Criteria

1. THE ML_System SHALL sürekli olarak tüm ürünlerin stok seviyelerini izleyecektir
2. WHEN bir ürünün stok seviyesi normal tüketim patterninden %30 veya daha fazla sapma gösterdiğinde, THE ML_System SHALL bir Anomaly kaydı oluşturacaktır
3. WHEN bir Anomaly tespit edildiğinde, THE ML_System SHALL Dashboard üzerinde bir Alert gösterecektir
4. THE ML_System SHALL her ürün için geçmiş 30 günlük tüketim verilerini Training_Data olarak kullanacaktır
5. THE ML_System SHALL tespit edilen her Anomaly için önem seviyesi (düşük, orta, yüksek, kritik) belirleyecektir

### Requirement 2: Minibar Tüketim Analizi

**User Story:** Admin kullanıcı olarak, minibar tüketim miktarlarındaki anormal artış veya azalışları görmek istiyorum, böylece operasyonel sorunları veya fırsatları erkenden tespit edebilirim.

#### Acceptance Criteria

1. THE ML_System SHALL her oda için minibar tüketim miktarlarını günlük olarak analiz edecektir
2. WHEN bir odanın tüketim miktarı son 7 günlük ortalamadan %40 veya daha fazla sapma gösterdiğinde, THE ML_System SHALL bir Alert oluşturacaktır
3. THE ML_System SHALL tüketim patternlerini oda tipi, sezon ve doluluk oranına göre segmentlere ayırarak analiz edecektir
4. THE ML_System SHALL tespit edilen tüketim anomalilerini oda numarası, ürün adı ve sapma yüzdesi ile birlikte gösterecektir
5. WHILE sistem öğrenme modunu çalıştırırken, THE ML_System SHALL yanlış pozitif uyarıları azaltmak için Threshold değerlerini otomatik olarak ayarlayacaktır

### Requirement 3: Dolum Süresi Optimizasyonu

**User Story:** Admin kullanıcı olarak, minibar yeniden dolum sürelerindeki gecikmeleri otomatik tespit eden bir sistem istiyorum, böylece operasyonel verimliliği artırabilirim.

#### Acceptance Criteria

1. THE ML_System SHALL her dolum işleminin başlangıç ve bitiş zamanını kaydedecektir
2. WHEN bir dolum işlemi ortalama dolum süresinden %50 veya daha fazla uzun sürdüğünde, THE ML_System SHALL bir Alert oluşturacaktir
3. THE ML_System SHALL dolum sürelerini kat sorumlusu, kat numarası ve oda sayısına göre analiz edecektir
4. THE ML_System SHALL her kat sorumlusu için ortalama dolum süresi metriğini hesaplayacak ve Dashboard üzerinde gösterecektir
5. THE ML_System SHALL dolum süresi trendlerini haftalık ve aylık bazda raporlayacaktır

### Requirement 4: Stok Bitiş Tahmini

**User Story:** Admin kullanıcı olarak, ürünlerin ne zaman tükeneceğini önceden tahmin eden bir sistem istiyorum, böylece zamanında sipariş verebilirim.

#### Acceptance Criteria

1. THE ML_System SHALL her ürün için geçmiş tüketim verilerini kullanarak gelecekteki tüketimi tahmin edecektir
2. THE ML_System SHALL her ürün için tahmini stok bitiş tarihini hesaplayacaktır
3. WHEN bir ürünün tahmini stok bitiş tarihi 7 gün veya daha az olduğunda, THE ML_System SHALL bir Alert oluşturacaktır
4. THE ML_System SHALL tahminleri mevsimsel değişkenler, doluluk oranı ve geçmiş trendleri dikkate alarak yapacaktır
5. THE ML_System SHALL tahmin doğruluğunu gerçek verilerle karşılaştırarak Learning_Model'i sürekli güncelleyecektir

### Requirement 5: Admin Dashboard ve Uyarı Yönetimi

**User Story:** Admin kullanıcı olarak, tüm uyarıları ve metrikleri tek bir dashboard üzerinde görmek istiyorum, böylece sistemi kolayca izleyebilirim.

#### Acceptance Criteria

1. THE ML_System SHALL Dashboard üzerinde aktif Alert'leri önem seviyesine göre sıralı olarak gösterecektir
2. THE ML_System SHALL her Alert için detaylı bilgi (zaman, metrik, sapma miktarı, önerilen aksiyon) sağlayacaktır
3. WHEN Admin_User bir Alert'i görüntülediğinde, THE ML_System SHALL ilgili Alert'i "okundu" olarak işaretleyecektir
4. THE ML_System SHALL Dashboard üzerinde son 24 saat, son 7 gün ve son 30 gün için özet istatistikler gösterecektir
5. THE ML_System SHALL Admin_User'ın Alert bildirim tercihlerini (email, SMS, push notification) yapılandırmasına izin verecektir

### Requirement 6: Makine Öğrenmesi ve Sürekli İyileştirme

**User Story:** Admin kullanıcı olarak, sistemin zaman içinde daha akıllı hale gelmesini ve daha doğru tahminler yapmasını istiyorum, böylece yanlış uyarılar azalsın.

#### Acceptance Criteria

1. THE ML_System SHALL her gün gece yarısı Training_Data'yı güncelleyerek Learning_Model'i yeniden eğitecektir
2. THE ML_System SHALL tespit edilen her Anomaly için Admin_User'dan geri bildirim (doğru/yanlış pozitif) alacaktır
3. WHEN Admin_User bir Alert'i "yanlış pozitif" olarak işaretlediğinde, THE ML_System SHALL bu bilgiyi Learning_Model'e dahil edecektir
4. THE ML_System SHALL model performans metriklerini (doğruluk, hassasiyet, geri çağırma) hesaplayacak ve Dashboard üzerinde gösterecektir
5. THE ML_System SHALL en az %85 doğruluk oranına ulaşana kadar Threshold değerlerini otomatik olarak optimize edecektir

### Requirement 7: Veri Toplama ve Saklama

**User Story:** Admin kullanıcı olarak, sistemin topladığı verilerin güvenli bir şekilde saklanmasını istiyorum, böylece geçmiş analizler yapabilir ve raporlar oluşturabilirim.

#### Acceptance Criteria

1. THE ML_System SHALL tüm Metric verilerini zaman damgası ile birlikte veritabanında saklayacaktır
2. THE ML_System SHALL veri toplama işlemlerini her 15 dakikada bir gerçekleştirecektir
3. THE ML_System SHALL 90 günden eski ham verileri otomatik olarak arşivleyecektir
4. THE ML_System SHALL arşivlenen verileri sıkıştırılmış formatta saklayacaktır
5. THE ML_System SHALL veri bütünlüğünü korumak için her veri kaydında checksum kullanacaktır

### Requirement 8: Performans ve Ölçeklenebilirlik

**User Story:** Admin kullanıcı olarak, sistemin hızlı çalışmasını ve büyüdükçe performansını korumasını istiyorum, böylece kullanıcı deneyimi etkilenmesin.

#### Acceptance Criteria

1. THE ML_System SHALL Dashboard'u 2 saniye veya daha kısa sürede yükleyecektir
2. THE ML_System SHALL anomali tespit işlemlerini arka planda asenkron olarak gerçekleştirecektir
3. WHEN sistem 1000'den fazla oda verisi işlediğinde, THE ML_System SHALL performansını koruyacaktır
4. THE ML_System SHALL veritabanı sorgularını optimize etmek için önbellekleme kullanacaktır
5. THE ML_System SHALL CPU kullanımını %30'un altında tutacaktır

### Requirement 9: Güvenlik ve Yetkilendirme

**User Story:** Admin kullanıcı olarak, ML sisteminin verilerinin ve ayarlarının güvenli olmasını istiyorum, böylece yetkisiz erişim engellensin.

#### Acceptance Criteria

1. THE ML_System SHALL sadece Admin_User rolüne sahip kullanıcıların Dashboard'a erişmesine izin verecektir
2. THE ML_System SHALL tüm API isteklerini authentication token ile doğrulayacaktır
3. THE ML_System SHALL hassas verileri (model parametreleri, threshold değerleri) şifreli olarak saklayacaktır
4. THE ML_System SHALL her Alert görüntüleme ve yapılandırma değişikliğini audit log'a kaydedecektir
5. THE ML_System SHALL SQL injection ve XSS saldırılarına karşı input validasyonu yapacaktır

### Requirement 10: Raporlama ve Analitik

**User Story:** Admin kullanıcı olarak, ML sisteminin ürettiği verileri raporlar halinde görmek istiyorum, böylece stratejik kararlar alabilirim.

#### Acceptance Criteria

1. THE ML_System SHALL haftalık ve aylık anomali raporları oluşturacaktır
2. THE ML_System SHALL raporları PDF ve Excel formatlarında export edebilecektir
3. THE ML_System SHALL trend analizleri için grafikler (çizgi, bar, pasta) oluşturacaktır
4. THE ML_System SHALL en sık tespit edilen anomali tiplerini ve etkilenen ürünleri raporlayacaktır
5. THE ML_System SHALL model performans raporlarını aylık olarak otomatik oluşturacak ve Admin_User'a email ile gönderecektir
