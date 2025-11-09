# Design Document

## Overview

Bu tasarım, base.html template'indeki header yapısını yeniden düzenleyerek daha kullanıcı dostu, kompakt ve anlamlı bir navigasyon deneyimi sağlamayı amaçlamaktadır. Mevcut header yapısı gereksiz yer kaplıyor ve her sayfada "Panel" yazısı gösteriliyor. Yeni tasarımda:

- Her sayfa kendi başlığını header'da gösterecek
- Otel logosu daha büyük ve görünür olacak
- Sayfa açıklamaları header'a taşınacak
- İşlem butonları sayfa içeriğine indirilecek
- Header daha kompakt ve responsive olacak

## Architecture

### Component Hierarchy

```
base.html
├── Header (Yeniden tasarlanacak)
│   ├── Hamburger Menu Button (Mevcut - değişmeyecek)
│   ├── Logo & Title Section (YENİ)
│   │   ├── Hotel Logo (Büyütülecek)
│   │   ├── Page Title (Dinamik)
│   │   └── Page Description (YENİ - opsiyonel)
│   └── Actions Section (Mevcut)
│       ├── Theme Toggle
│       └── Logout Button
├── Sidebar (Değişmeyecek)
└── Main Content
    ├── Page Actions Bar (YENİ - butonlar için)
    └── Page Content
```

### Template Block Yapısı

Yeni block yapısı:

```jinja2
{% block page_title %}Sayfa Başlığı{% endblock %}
{% block page_description %}Sayfa açıklaması (opsiyonel){% endblock %}
{% block page_actions %}İşlem butonları (opsiyonel){% endblock %}
```

## Components and Interfaces

### 1. Header Component (base.html)

**Mevcut Durum:**
```html
<header>
  <div class="flex items-center justify-between px-3 sm:px-4 py-3">
    <div class="w-12 md:hidden"></div>
    <div class="flex items-center gap-3">
      <!-- Küçük logo -->
      <!-- "Panel" yazısı (statik) -->
    </div>
    <div class="flex items-center space-x-2">
      <!-- Theme toggle, Logout -->
    </div>
  </div>
</header>
```

**Yeni Tasarım:**
```html
<header class="bg-white dark:bg-slate-800 shadow-sm border-b sticky top-0 z-20">
  <div class="flex items-center justify-between px-4 py-2.5 gap-4">
    <!-- Sol: Logo + Başlık -->
    <div class="flex items-center gap-3 flex-1 min-w-0">
      {% if kullanici_otel and kullanici_otel.logo %}
      <img src="data:image/png;base64,{{ kullanici_otel.logo }}" 
           alt="{{ kullanici_otel.ad }}"
           class="h-10 sm:h-12 w-auto object-contain flex-shrink-0">
      {% endif %}
      
      <div class="flex flex-col min-w-0 flex-1">
        <h1 class="text-lg sm:text-xl font-bold text-slate-900 dark:text-slate-100 truncate">
          {% block page_title %}Panel{% endblock %}
        </h1>
        {% block page_description %}{% endblock %}
      </div>
    </div>
    
    <!-- Sağ: Actions -->
    <div class="flex items-center gap-2">
      <button id="theme-toggle" class="p-2 rounded-lg">...</button>
      <a href="{{ url_for('logout') }}" class="p-2 rounded-lg">...</a>
    </div>
  </div>
</header>
```

### 2. Page Actions Bar Component (Yeni)

Her sayfada, content'in hemen başında opsiyonel olarak gösterilecek:

```html
{% block content %}
<div class="space-y-6">
  <!-- Page Actions Bar (Opsiyonel) -->
  {% block page_actions %}
  <!-- Örnek: -->
  <div class="flex justify-end gap-3">
    <a href="..." class="btn-primary">
      <svg>...</svg>
      Yeni Ekle
    </a>
  </div>
  {% endblock %}
  
  <!-- Sayfa içeriği -->
  ...
</div>
{% endblock %}
```

### 3. Page Description Component (Yeni)

Header içinde, başlığın altında gösterilecek opsiyonel açıklama:

```html
{% block page_description %}
<p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 truncate hidden sm:block">
  Açıklama metni buraya gelecek
</p>
{% endblock %}
```

## Data Models

### Context Variables

**Mevcut:**
- `current_user`: Giriş yapmış kullanıcı
- `kullanici_otel`: Kullanıcının bağlı olduğu otel bilgisi

**Yeni (Eklenmeyecek):**
Mevcut context değişkenleri yeterli. Sadece template block'ları kullanılacak.

## Implementation Details

### 1. base.html Değişiklikleri

**Header Section (Satır ~1110-1150):**

```html
<!-- Top Navigation - Responsive -->
<header class="bg-white dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700 sticky top-0 z-20">
  <div class="flex items-center justify-between px-4 py-2.5 gap-4">
    <!-- Spacer for mobile menu button -->
    <div class="w-12 md:hidden"></div>

    <!-- Logo & Page Title Section -->
    <div class="flex items-center gap-3 flex-1 min-w-0">
      {% if kullanici_otel %}
        {% if kullanici_otel.logo %}
        <img src="data:image/png;base64,{{ kullanici_otel.logo }}" 
             alt="{{ kullanici_otel.ad }}" 
             class="h-10 sm:h-12 w-auto object-contain flex-shrink-0">
        {% endif %}
        
        <div class="flex flex-col min-w-0 flex-1">
          <h1 class="text-lg sm:text-xl font-bold text-slate-900 dark:text-slate-100 truncate">
            {% block page_title %}Panel{% endblock %}
          </h1>
          {% block page_description %}{% endblock %}
        </div>
      {% else %}
        <h1 class="text-lg sm:text-xl font-bold text-slate-900 dark:text-slate-100 truncate flex-1">
          {% block page_title_fallback %}Panel{% endblock %}
        </h1>
      {% endif %}
    </div>

    <!-- Right side actions -->
    <div class="flex items-center gap-2">
      <!-- Theme Toggle -->
      <button id="theme-toggle" class="p-2 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
        <svg id="theme-toggle-dark-icon" class="hidden w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path>
        </svg>
        <svg id="theme-toggle-light-icon" class="hidden w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"></path>
        </svg>
      </button>

      <!-- Logout -->
      {% if current_user %}
      <a href="{{ url_for('logout') }}" 
         class="p-2 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
         title="Çıkış Yap">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
        </svg>
      </a>
      {% endif %}
    </div>
  </div>
</header>
```

### 2. Sayfa Template'lerinde Değişiklikler

**Örnek: kritik_stoklar.html**

**Mevcut:**
```html
{% block page_title %}Kritik Stoklar{% endblock %}

{% block content %}
<div class="space-y-6">
  <div class="flex justify-between items-center">
    <div>
      <h2 class="text-2xl font-bold text-slate-900">Kritik Stoklar</h2>
      <p class="mt-1 text-sm text-slate-500">Azalan ve stokout ürünleri takip edin</p>
    </div>
    <div class="flex gap-3">
      <a href="..." class="btn">Sipariş Hazırla</a>
      <a href="..." class="btn">Dashboard'a Dön</a>
    </div>
  </div>
  ...
</div>
{% endblock %}
```

**Yeni:**
```html
{% block page_title %}Kritik Stoklar{% endblock %}

{% block page_description %}
<p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 truncate hidden sm:block">
  Azalan ve stokout ürünleri takip edin
</p>
{% endblock %}

{% block content %}
<div class="space-y-6">
  <!-- Page Actions -->
  <div class="flex justify-end gap-3">
    <a href="{{ url_for('kat_sorumlusu_siparis_hazirla') }}" 
       class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700">
      <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
      </svg>
      Sipariş Hazırla
    </a>
    <a href="{{ url_for('kat_sorumlusu_dashboard') }}" 
       class="inline-flex items-center px-4 py-2 border border-slate-300 rounded-md shadow-sm text-sm font-medium text-slate-700 bg-white hover:bg-slate-50">
      Dashboard'a Dön
    </a>
  </div>

  <!-- İstatistik Kartları -->
  <div class="grid grid-cols-1 gap-5 sm:grid-cols-4">
    ...
  </div>
  ...
</div>
{% endblock %}
```

### 3. CSS Değişiklikleri

Header yüksekliğini azaltmak için:

```css
/* Header height optimization */
header {
    min-height: 56px; /* Mobile */
}

@media (min-width: 640px) {
    header {
        min-height: 64px; /* Desktop */
    }
}

/* Logo sizing */
header img {
    max-height: 40px; /* Mobile */
}

@media (min-width: 640px) {
    header img {
        max-height: 48px; /* Desktop */
    }
}
```

## Responsive Design Strategy

### Mobile (< 640px)
- Logo: 40px yükseklik
- Başlık: text-lg (18px)
- Açıklama: Gizli
- Header yükseklik: 56px
- Butonlar: Tam genişlik, stack

### Tablet (640px - 1024px)
- Logo: 48px yükseklik
- Başlık: text-xl (20px)
- Açıklama: Görünür
- Header yükseklik: 64px
- Butonlar: Yan yana

### Desktop (> 1024px)
- Logo: 48px yükseklik
- Başlık: text-xl (20px)
- Açıklama: Görünür
- Header yükseklik: 64px
- Butonlar: Yan yana

## Migration Strategy

### Aşama 1: Base Template Güncelleme
1. base.html header section'ını yeniden yaz
2. Yeni block'ları ekle (page_description)
3. CSS değişikliklerini uygula

### Aşama 2: Sayfa Template'lerini Güncelleme
Öncelik sırasına göre:
1. Dashboard sayfaları (sistem_yoneticisi, kat_sorumlusu)
2. Liste sayfaları (otel_listesi, kat_tanimla, oda_tanimla)
3. Form sayfaları (otel_tanimla, kat_duzenle)
4. Rapor sayfaları
5. Diğer sayfalar

Her sayfa için:
1. `page_title` block'unu kontrol et
2. `page_description` block'u ekle
3. Sayfa içindeki h2 başlığını kaldır
4. İşlem butonlarını content'in başına taşı

### Aşama 3: Test ve Doğrulama
1. Her sayfa tipinde responsive test
2. Dark mode uyumluluğu
3. Logo olan/olmayan otel senaryoları
4. Uzun başlık/açıklama senaryoları

## Error Handling

### Logo Yükleme Hataları
```python
# Backend'de zaten var, değişiklik yok
if kullanici_otel and kullanici_otel.logo:
    # Logo göster
else:
    # Sadece başlık göster
```

### Uzun Başlıklar
```html
<!-- truncate class ile otomatik kesme -->
<h1 class="... truncate">
  {% block page_title %}...{% endblock %}
</h1>
```

### Eksik Block'lar
```html
<!-- Default değerler ile fallback -->
{% block page_title %}Panel{% endblock %}
{% block page_description %}{% endblock %} <!-- Boş bırakılabilir -->
```

## Testing Strategy

### Unit Tests
Gerekli değil - sadece template değişiklikleri

### Integration Tests
1. Her sayfa tipinde görsel test
2. Responsive breakpoint testleri
3. Dark mode testleri

### Manual Testing Checklist
- [ ] Dashboard sayfaları doğru başlık gösteriyor
- [ ] Logo doğru boyutta görünüyor
- [ ] Açıklamalar mobile'da gizli
- [ ] Butonlar sayfa içinde doğru konumda
- [ ] Header yüksekliği optimize
- [ ] Dark mode çalışıyor
- [ ] Truncate uzun başlıklarda çalışıyor
- [ ] Logo olmayan otellerde düzgün görünüm

## Performance Considerations

### Optimizasyonlar
1. Logo base64 olarak zaten cache'leniyor
2. CSS değişiklikleri minimal
3. JavaScript değişikliği yok
4. Sayfa yükleme hızı etkilenmeyecek

### Potansiyel Sorunlar
- Yok - sadece HTML/CSS değişiklikleri

## Security Considerations

### XSS Koruması
```html
<!-- Jinja2 otomatik escape ediyor -->
<h1>{{ page_title }}</h1> <!-- Güvenli -->
```

### CSRF
Değişiklik yok - sadece görsel düzenlemeler

## Accessibility

### WCAG 2.1 Uyumluluğu
1. **Semantic HTML**: `<header>`, `<h1>` kullanımı
2. **Contrast Ratios**: Mevcut renk paletini koruyoruz
3. **Focus States**: Mevcut focus stilleri korunuyor
4. **Screen Readers**: Logo için alt text mevcut

### Keyboard Navigation
Değişiklik yok - mevcut navigasyon korunuyor

## Documentation Updates

### Gerekli Dokümantasyon
1. Template kullanım kılavuzu (yeni block'lar için)
2. Sayfa oluşturma şablonu (örnek template)

### Örnek Template
```html
{% extends "base.html" %}

{% block title %}Sayfa Başlığı - Minibar Takip Sistemi{% endblock %}

{% block page_title %}Sayfa Başlığı{% endblock %}

{% block page_description %}
<p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 truncate hidden sm:block">
  Sayfa açıklaması buraya gelecek
</p>
{% endblock %}

{% block content %}
<div class="space-y-6">
  <!-- Opsiyonel: İşlem Butonları -->
  <div class="flex justify-end gap-3">
    <a href="..." class="btn-primary">Yeni Ekle</a>
  </div>

  <!-- Sayfa İçeriği -->
  ...
</div>
{% endblock %}
```
