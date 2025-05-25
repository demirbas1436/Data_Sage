# DATA SAGE

DATA SAGE, Flask ile geliştirilmiş bir web uygulamasıdır. Kullanıcının doğal dilde yazdığı sorgu önce OpenAI GPT-3.5-Turbo API’si ile SQL sorgusuna dönüştürülür. Elde edilen SQL sorgusu Python’un sqlite3 modülü ile `sakila.db` veritabanında çalıştırılarak sonuçlar elde edilir. Sonuçlar, basit bir HTML/CSS arayüzünde tablo halinde gösterilir. Arayüz tamamen sade tasarlanmıştır; Bootstrap veya benzeri ek bir kütüphane kullanılmamıştır. Proje ile birlikte veritabanı dosyası (`sakila.db`) sağlanmamaktadır; bu dosyayı kendiniz temin etmeli ve proje kök dizinine yerleştirmelisiniz.

## Özellikler

- Kullanıcının doğal dilde yazdığı sorguları otomatik olarak SQL sorgularına dönüştürür.  
- OpenAI GPT-3.5-Turbo modeli ile sorgu oluşturma (OpenAI API entegrasyonu).  
- SQLite tabanlı `sakila.db` veritabanında sorgu çalıştırma ve sonuçları çekme.  
- Kullanıcıya basit ve sade bir HTML/CSS arayüzü sunar (Bootstrap veya benzeri framework kullanılmamıştır).  
- Hata durumunda kullanıcıya anlamlı mesajlar gösterir (basit hata yönetimi).

## Gereksinimler

- Python 3.8 veya üzeri  
- Flask  
- openai  
- tabulate  
- sqlite3 (Python ile birlikte gelir)  
- sakila.db (kullanıcı tarafından sağlanmalıdır)

## Kurulum Talimatları

1. Projeyi klonlayın veya zip dosyasını indirin:  
   ```bash
   git clone https://github.com/kullanici/datasage.git
   ```  
2. Proje dizinine gidin:  
   ```bash
   cd datasage
   ```  
3. Bir Python sanal ortamı oluşturun ve etkinleştirin:  
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```  
4. Gerekli Python paketlerini yükleyin:  
   ```bash
   pip install -r requirements.txt
   ```  
5. `sakila.db` veritabanı dosyasını proje kök dizinine kopyalayın.  
6. OpenAI API anahtarınızı ortam değişkeni olarak ayarlayın:  
   ```bash
   export OPENAI_API_KEY="sizin_api_anahtarınız"
   ```  
7. Uygulamayı başlatın:  
   ```bash
   flask run
   ```  
   veya  
   ```bash
   python app.py
   ```  

## Kullanım

- Tarayıcınızda `http://localhost:5000` adresine gidin.  
- Sorgunuzu doğal dilde yazın ve Gönder butonuna basın.  
- SQL sorgusu oluşturulacak ve sonuçlar gösterilecektir.

## Örnek Çıktı

**Sorgu:** "Ücreti 0.99 olan filmleri göster."  
**SQL Çıktısı:**
```sql
SELECT title FROM film WHERE rental_rate = 0.99;
```

**Örnek Sonuç:**

| title             |
|-------------------|
| Academy Dinosaur  |
| Ace Goldfinger    |
| Adaptation Holes  |
| ...               |

## Güvenlik Notu

API anahtarınızı asla kod içinde açık olarak bırakmayın. Ortam değişkeni olarak kullanmanız önerilir.

## Katkıda Bulunma

- Issue açarak katkıda bulunabilirsiniz.  
- Pull request göndererek kod katkısı sağlayabilirsiniz.

## Lisans

Bu proje MIT lisansı ile lisanslanmıştır.
