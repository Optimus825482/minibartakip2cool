# Design Document

## Overview

Bu tasarım, mevcut Flask tabanlı minibar yönetim sistemine kapsamlı test coverage'ı eklemek ve frontend kodlarındaki hataları tespit edip düzeltmek için bir strateji sunmaktadır. Sistem şu anda pytest test framework'ü kullanmamakta ve hiç test dosyası bulunmamaktadır. Bu tasarım, sıfırdan test altyapısı kurulumunu, tüm kritik fonksiyonellikler için test yazılmasını ve frontend'deki potansiyel hataların tespit edilip düzeltilmesini kapsamaktadır.

## Architecture

### Test Altyapısı Mimarisi

```
tests/
├── conftest.py                 # Global fixtures ve konfigürasyon
├── pytest.ini                  # Pytest ayarları
├── unit/                       # Unit testler
│   ├── test_models.py         # Model testleri
│   ├── test_auth.py           # Authentication testleri
│   ├── test_utils.py          # Utility fonksiyon testleri
│   └── test_forms.py          # Form validation testleri
├── integration/                # Integration testler
│   ├── test_stok_yonetimi.py  # Stok yönetimi flow testleri
│   ├── test_zimmet.py         # Zimmet yönetimi flow testleri
│   ├── test_minibar.py        # Minibar işlemleri flow testleri
│   ├── test_qr_system.py      # QR kod sistemi testleri
│   └── test_multi_hotel.py    # Multi-hotel testleri
├── api/                        # API endpoint testleri
│   ├── test_admin_api.py      # Admin API testleri
│   ├── test_depo_api.py       # Depo API testleri
│   └── test_kat_api.py        # Kat sorumlusu API testleri
├── frontend/                   # Frontend testleri
│   ├── test_forms.py          # Form submission testleri
│   ├── test_javascript.py     # JavaScript fonksiyon testleri
│   └── test_ui.py             # UI component testleri
└── fixtures/                   # Test data fixtures
    ├── users.py               # Kullanıcı fixtures
    ├── products.py            # Ürün fixtures
    └── hotels.py              # Otel fixtures
```

### Test Stratejisi

1. **Unit Tests**: İzole fonksiyon ve metod testleri
2. **Integration Tests**: Birden fazla bileşenin birlikte çalışma testleri
3. **API Tests**: REST endpoint testleri
4. **Frontend Tests**: UI ve JavaScript testleri
5. **E2E Tests**: Kullanıcı senaryoları (opsiyonel)

## Components and Interfaces

### 1. Test Configuration (conftest.py)

**Amaç**: Global test fixtures ve konfigürasyon sağlamak

**Fixtures**:
- `app`: Flask test uygulaması
- `client`: Flask test client
- `db`: Test veritabanı
- `auth_client`: Authenticated test client
- `sample_user`: Örnek kullanıcı
- `sample_hotel`: Örnek otel
- `sample_products`: Örnek ürünler

**Konfigürasyon**:
```python
@pytest.fixture(scope='session')
def app():
    """Test Flask uygulaması oluştur"""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture(scope='function')
def db(app):
    """Her test için temiz veritabanı"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()
```

### 2. Model Tests (test_models.py)

**Test Edilen Modeller**:
- Kullanici
- Otel
- Kat
- Oda
- Urun
- UrunGrup
- StokHareket
- PersonelZimmet
- PersonelZimmetDetay
- MinibarIslem
- MinibarIslemDetay

**Test Senaryoları**:
```python
class TestKullaniciModel:
    def test_password_hashing(self, db):
        """Şifre hash'leme testi"""
        
    def test_password_verification(self, db):
        """Şifre doğrulama testi"""
        
    def test_role_assignment(self, db):
        """Rol atama testi"""
        
    def test_hotel_relationship(self, db):
        """Otel ilişkisi testi"""
```

### 3. Authentication Tests (test_auth.py)

**Test Senaryoları**:
- Login başarılı (tüm roller için)
- Login başarısız (yanlış şifre)
- Login başarısız (kullanıcı yok)
- Logout
- Session yönetimi
- CSRF token validation
- Role-based access control

**Örnek Test**:
```python
def test_login_success_admin(client, sample_admin):
    """Admin başarılı login testi"""
    response = client.post('/login', data={
        'kullanici_adi': 'admin',
        'sifre': 'test123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Dashboard' in response.data
    
def test_unauthorized_access(client):
    """Yetkisiz erişim testi"""
    response = client.get('/admin/personel-tanimla')
    assert response.status_code == 302  # Redirect to login
```

### 4. Stok Yönetimi Tests (test_stok_yonetimi.py)

**Test Senaryoları**:
- Stok girişi (giriş)
- Stok çıkışı (çıkış)
- Stok devri (devir)
- Stok sayımı (sayım)
- Negatif stok kontrolü
- Stok geçmişi
- Stok raporları

**Örnek Test**:
```python
def test_stok_giris(auth_client, sample_product):
    """Stok giriş işlemi testi"""
    response = auth_client.post('/stok-giris', data={
        'urun_id': sample_product.id,
        'hareket_tipi': 'giris',
        'miktar': 100,
        'aciklama': 'Test girişi'
    })
    
    assert response.status_code == 302
    
    # Stok kontrolü
    hareket = StokHareket.query.filter_by(
        urun_id=sample_product.id
    ).first()
    assert hareket is not None
    assert hareket.miktar == 100
```

### 5. Zimmet Yönetimi Tests (test_zimmet.py)

**Test Senaryoları**:
- Zimmet oluşturma
- Zimmet detay ekleme
- Zimmet durumu değiştirme
- Zimmet iade
- Kritik stok kontrolü
- Zimmet geçmişi

### 6. Minibar İşlemleri Tests (test_minibar.py)

**Test Senaryoları**:
- İlk dolum
- Kontrol işlemi
- Doldurma işlemi
- Ek dolum
- Tüketim hesaplama
- Minibar geçmişi

### 7. QR Kod Sistemi Tests (test_qr_system.py)

**Test Senaryoları**:
- QR kod oluşturma
- QR kod okuma
- QR kod validasyonu
- QR kod expiration
- QR kod güvenlik

### 8. Multi-Hotel Tests (test_multi_hotel.py)

**Test Senaryoları**:
- Otel oluşturma
- Veri izolasyonu
- Kullanıcı-otel ataması
- Otel bazlı raporlama
- Otel değiştirme

### 9. API Endpoint Tests

**Test Edilen Endpoint'ler**:
- `/api/admin/*` - Admin API'leri
- `/api/depo/*` - Depo API'leri
- `/api/kat-sorumlusu/*` - Kat sorumlusu API'leri
- `/api/sistem-yoneticisi/*` - Sistem yöneticisi API'leri

**Test Senaryoları**:
```python
def test_api_get_products(auth_client):
    """Ürün listesi API testi"""
    response = auth_client.get('/api/admin/urunler')
    assert response.status_code == 200
    data = response.get_json()
    assert 'success' in data
    assert data['success'] is True
    
def test_api_create_product(auth_client):
    """Ürün oluşturma API testi"""
    response = auth_client.post('/api/admin/urun-ekle', json={
        'urun_adi': 'Test Ürün',
        'grup_id': 1,
        'birim_fiyat': 10.50
    })
    assert response.status_code == 201
```

### 10. Frontend Tests

**Test Edilen Alanlar**:
- Form submission
- JavaScript validasyonlar
- AJAX çağrıları
- UI component'leri
- Responsive design

**Frontend Hata Tespiti Stratejisi**:

1. **JavaScript Console Errors**:
   - Browser console'da hata kontrolü
   - Undefined variable/function kontrolü
   - Syntax error kontrolü

2. **Form Validation Issues**:
   - Required field kontrolü
   - Data type validation
   - Client-side vs server-side tutarlılık

3. **AJAX Error Handling**:
   - Error callback kontrolü
   - Network error handling
   - Timeout handling

4. **UI/UX Issues**:
   - Broken layouts
   - Missing elements
   - Incorrect data display
   - Button states

5. **Accessibility Issues**:
   - ARIA labels
   - Keyboard navigation
   - Screen reader compatibility

**Frontend Test Araçları**:
- Selenium WebDriver (browser automation)
- Playwright (modern browser testing)
- Jest (JavaScript unit testing)
- Manual inspection

## Data Models

### Test Data Factory Pattern

```python
class UserFactory:
    @staticmethod
    def create_admin(db, **kwargs):
        """Admin kullanıcı oluştur"""
        user = Kullanici(
            kullanici_adi=kwargs.get('kullanici_adi', 'admin'),
            ad=kwargs.get('ad', 'Admin'),
            soyad=kwargs.get('soyad', 'User'),
            rol='admin',
            email=kwargs.get('email', 'admin@test.com')
        )
        user.sifre_belirle(kwargs.get('sifre', 'test123'))
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def create_kat_sorumlusu(db, **kwargs):
        """Kat sorumlusu oluştur"""
        # Similar implementation
```

### Test Database Schema

Test veritabanı production ile aynı schema'yı kullanacak ancak:
- SQLite in-memory database (hızlı testler için)
- Her test için temiz state
- Fixture'lar ile önceden tanımlı data

## Error Handling

### Test Error Handling

```python
def test_database_error_handling(client, mocker):
    """Veritabanı hatası yönetimi testi"""
    # Mock database error
    mocker.patch('models.db.session.commit', 
                 side_effect=OperationalError('DB Error', None, None))
    
    response = client.post('/stok-giris', data={...})
    assert response.status_code == 500
    assert b'Veritabanı hatası' in response.data
```

### Frontend Error Detection

**JavaScript Error Detection**:
```javascript
// Global error handler
window.addEventListener('error', function(event) {
    console.error('JavaScript Error:', event.error);
    // Log to test results
});

// Unhandled promise rejection
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled Promise Rejection:', event.reason);
});
```

**Form Validation Error Detection**:
```python
def test_form_validation_errors(client):
    """Form validation hata tespiti"""
    # Submit invalid data
    response = client.post('/personel-tanimla', data={
        'kullanici_adi': '',  # Required field empty
        'sifre': '123'  # Too short
    })
    
    # Check for validation errors
    assert b'Kullanıcı adı zorunludur' in response.data
    assert b'Şifre en az 6 karakter' in response.data
```

## Testing Strategy

### Test Coverage Goals

- **Critical Modules**: 80%+ coverage
  - models.py
  - routes/*.py
  - utils/decorators.py
  - utils/authorization.py

- **Important Modules**: 70%+ coverage
  - utils/helpers.py
  - utils/audit.py
  - forms.py

- **Other Modules**: 60%+ coverage

### Test Execution Strategy

1. **Development Phase**:
   ```bash
   # Tüm testleri çalıştır
   pytest
   
   # Belirli bir modül
   pytest tests/unit/test_models.py
   
   # Coverage ile
   pytest --cov=. --cov-report=html
   ```

2. **CI/CD Integration**:
   ```yaml
   # GitHub Actions / GitLab CI
   test:
     script:
       - pip install -r requirements.txt
       - pytest --cov=. --cov-report=xml
       - coverage report --fail-under=70
   ```

3. **Pre-commit Hooks**:
   ```bash
   # .git/hooks/pre-commit
   pytest tests/unit/
   ```

### Frontend Testing Strategy

1. **Manual Testing Checklist**:
   - [ ] Tüm formlar submit ediliyor mu?
   - [ ] JavaScript hataları var mı?
   - [ ] AJAX çağrıları çalışıyor mu?
   - [ ] Responsive design sorunsuz mu?
   - [ ] Browser compatibility (Chrome, Firefox, Safari)

2. **Automated Browser Testing**:
   ```python
   from selenium import webdriver
   
   def test_login_form_submission():
       driver = webdriver.Chrome()
       driver.get('http://localhost:5000/login')
       
       # Fill form
       driver.find_element_by_name('kullanici_adi').send_keys('admin')
       driver.find_element_by_name('sifre').send_keys('test123')
       
       # Submit
       driver.find_element_by_css_selector('button[type="submit"]').click()
       
       # Verify redirect
       assert '/dashboard' in driver.current_url
       driver.quit()
   ```

3. **JavaScript Unit Testing**:
   ```javascript
   // Jest test example
   describe('FormValidator', () => {
       test('validates required fields', () => {
           const validator = new FormValidator(form);
           validator.setRules({
               username: { required: true }
           });
           
           const result = validator.validateField('username');
           expect(result.isValid).toBe(false);
       });
   });
   ```

## Frontend Issues Detection Plan

### Common Frontend Issues to Check

1. **JavaScript Errors**:
   - Undefined variables
   - Function not found
   - Syntax errors
   - Type errors

2. **Form Issues**:
   - Form not submitting
   - Validation not working
   - CSRF token missing
   - Data not being sent

3. **AJAX Issues**:
   - Endpoints not responding
   - Error handling missing
   - Success callbacks not working
   - Data format mismatch

4. **UI Issues**:
   - Broken layouts
   - Missing CSS classes
   - Incorrect Tailwind classes
   - Dark mode issues

5. **Accessibility Issues**:
   - Missing ARIA labels
   - Keyboard navigation broken
   - Focus management issues
   - Screen reader problems

### Frontend Inspection Tools

1. **Browser DevTools**:
   - Console (JavaScript errors)
   - Network (AJAX requests)
   - Elements (DOM inspection)
   - Lighthouse (accessibility audit)

2. **Automated Tools**:
   - ESLint (JavaScript linting)
   - Stylelint (CSS linting)
   - axe DevTools (accessibility)
   - WAVE (accessibility)

3. **Manual Testing**:
   - Click through all forms
   - Test all AJAX interactions
   - Check responsive design
   - Test keyboard navigation

## Implementation Phases

### Phase 1: Test Infrastructure Setup
- Install pytest and dependencies
- Create test directory structure
- Setup conftest.py with fixtures
- Configure pytest.ini

### Phase 2: Unit Tests
- Model tests
- Utility function tests
- Form validation tests
- Decorator tests

### Phase 3: Integration Tests
- Stok yönetimi flow tests
- Zimmet yönetimi flow tests
- Minibar işlemleri flow tests
- QR kod sistemi tests

### Phase 4: API Tests
- Admin API tests
- Depo API tests
- Kat sorumlusu API tests
- Error handling tests

### Phase 5: Frontend Testing & Fixes
- Manual inspection of all pages
- JavaScript error detection
- Form validation testing
- AJAX interaction testing
- UI/UX issue detection
- Accessibility audit
- Bug fixes

### Phase 6: Coverage & Reporting
- Generate coverage reports
- Identify untested code
- Write additional tests
- Document test results

## Performance Considerations

### Test Performance

- **In-memory database**: SQLite :memory: for fast tests
- **Parallel execution**: pytest-xdist for parallel test runs
- **Selective testing**: Run only changed tests during development
- **Caching**: Cache fixtures where appropriate

### Frontend Performance Testing

- **Page load times**: Measure with Lighthouse
- **JavaScript execution**: Profile with DevTools
- **Network requests**: Optimize AJAX calls
- **Bundle size**: Check JavaScript file sizes

## Security Considerations

### Test Security

- **Sensitive data**: Never commit real credentials
- **Test isolation**: Each test should be independent
- **CSRF testing**: Verify CSRF protection works
- **SQL injection**: Test input sanitization
- **XSS testing**: Test output escaping

### Frontend Security Testing

- **XSS vulnerabilities**: Test user input handling
- **CSRF tokens**: Verify all forms have tokens
- **Secure cookies**: Check cookie flags
- **Content Security Policy**: Verify CSP headers

## Documentation

### Test Documentation

- **Docstrings**: Every test should have clear docstring
- **README**: Test directory should have README
- **Coverage reports**: HTML reports for easy viewing
- **Test results**: CI/CD should show test results

### Frontend Issue Documentation

- **Issue tracker**: Document all found issues
- **Screenshots**: Include screenshots of issues
- **Steps to reproduce**: Clear reproduction steps
- **Priority**: Categorize by severity

## Tools and Dependencies

### Python Testing Tools

```txt
# requirements-test.txt
pytest==7.4.3
pytest-flask==1.3.0
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-xdist==3.5.0
selenium==4.15.2
playwright==1.40.0
factory-boy==3.3.0
faker==20.1.0
```

### Frontend Testing Tools

```json
{
  "devDependencies": {
    "jest": "^29.7.0",
    "eslint": "^8.54.0",
    "stylelint": "^15.11.0",
    "@axe-core/cli": "^4.8.2"
  }
}
```

## Success Criteria

### Test Coverage Success Criteria

- [ ] Minimum 70% overall code coverage
- [ ] 80%+ coverage for critical modules
- [ ] All API endpoints tested
- [ ] All models tested
- [ ] All authentication flows tested

### Frontend Success Criteria

- [ ] Zero JavaScript console errors
- [ ] All forms submit successfully
- [ ] All AJAX calls work correctly
- [ ] Responsive design works on all devices
- [ ] Accessibility score 90+ (Lighthouse)
- [ ] No broken UI elements
- [ ] All validation messages display correctly

## Maintenance Plan

### Test Maintenance

- **Regular updates**: Update tests when code changes
- **Refactoring**: Keep tests DRY and maintainable
- **Documentation**: Keep test docs up to date
- **Review**: Regular test code reviews

### Frontend Maintenance

- **Regular audits**: Monthly frontend audits
- **Browser testing**: Test on new browser versions
- **Accessibility**: Regular accessibility checks
- **Performance**: Monitor frontend performance
