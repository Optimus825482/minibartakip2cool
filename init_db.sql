-- Minibar Takip Sistemi - Initial Database Setup
-- Bu dosya Docker container ilk başlatıldığında otomatik çalışır

-- Database charset ayarları
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Timezone ayarı
SET time_zone = '+00:00';

-- Foreign key kontrollerini geçici olarak kapat
SET FOREIGN_KEY_CHECKS = 0;

-- Not: Tablolar init_db.py tarafından oluşturulacak
-- Bu dosya sadece initial setup için gerekli ayarları içerir

-- Foreign key kontrollerini tekrar aç
SET FOREIGN_KEY_CHECKS = 1;

-- Database hazır mesajı
SELECT 'Database initialized successfully!' as Status;
