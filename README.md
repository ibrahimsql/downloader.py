Tabii ki! Aşağıda, geliştirdiğimiz web indirici script'in çeşitli senaryolarda nasıl kullanılacağını gösteren örnek komutlar yer almaktadır. Bu örnekler, script'in esnekliğini ve farklı parametrelerle nasıl çalıştığını anlamanıza yardımcı olacaktır.

### 1. **Basit Kullanım**

Belirtilen URL'deki web sitesini varsayılan ayarlarla indirir ve "indirilen_site" dizinine kaydeder.

```bash
python web_indirici.py "http://example.com"
```

### 2. **Belirli Bir Dizin İçine İndirme**

Belirtilen URL'deki web sitesini "my_website" dizinine indirir.

```bash
python web_indirici.py "http://example.com" --dir my_website
```

### 3. **Tarama Derinliğini Ayarlama**

Script'in bağlantıları takip ederek daha derine inmesini sağlar. Bu örnekte, maksimum 2 seviye derinliğe kadar tarama yapılır.

```bash
python web_indirici.py "http://example.com" --depth 2
```

### 4. **İstekler Arası Gecikme Süresi Belirleme**

İstekler arasında 2 saniye bekleyerek tarama yapar. Bu, sunucu üzerindeki yükü azaltabilir.

```bash
python web_indirici.py "http://example.com" --delay 2
```

### 5. **Özel User-Agent Kullanma**

Belirli bir User-Agent belirterek istek gönderir. Bu, bazı web sitelerinin daha az kısıtlama uygulamasına neden olabilir.

```bash
python web_indirici.py "http://example.com" --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
```

### 6. **Rastgele User-Agent Kullanma**

Her istek için rastgele bir User-Agent kullanır. Bu, tespit edilme olasılığını azaltabilir.

```bash
python web_indirici.py "http://example.com" --random-user-agent
```

### 7. **Proxy Kullanarak İndirme**

Bir proxy sunucusu üzerinden istek gönderir. Bu, kimliğinizi gizlemek veya bölgesel kısıtlamaları aşmak için kullanılabilir.

```bash
python web_indirici.py "http://example.com" --proxy http://proxyserver:port
```

### 8. **SSL Sertifikası Doğrulamasını Atlamak**

SSL sertifikası doğrulamasını atlar. Bu, güvenli olmayan veya kendinden imzalı sertifikalara sahip siteleri indirirken işe yarar.

```bash
python web_indirici.py "http://example.com" --no-verify-ssl
```

### 9. **Maksimum Dosya Boyutunu Belirleme**

Maksimum dosya boyutunu 10 MB ile sınırlar. Daha büyük dosyalar indirilmeyecektir.

```bash
python web_indirici.py "http://example.com" --max-size 10
```

### 10. **Belirli Dosya Türlerini İndirme**

Sadece CSS, JS, ve resim dosyalarını (.png, .jpg) indirir. Bu, belirli türdeki içerikleri filtrelemek için kullanışlıdır.

```bash
python web_indirici.py "http://example.com" --include-types .css,.js,.png,.jpg
```

### 11. **Zaman Aşımı Ayarlama**

Her istek için maksimum 15 saniye bekler. Bu süre zarfında yanıt alamazsa bağlantıyı sonlandırır.

```bash
python web_indirici.py "http://example.com" --timeout 15
```

### 12. **Çerez Kullanımı**

Belirli çerezleri göndererek istek yapar. Bu, oturum açmayı gerektiren siteler için faydalıdır.

```bash
python web_indirici.py "http://example.com" --cookies "sessionid=12345; csrftoken=abcdef"
```

### 13. **Yeniden Deneme Sayısını Ayarlama**

Bağlantı hataları veya sunucu yanıt vermediğinde 5 defa yeniden denemeye çalışır.

```bash
python web_indirici.py "http://example.com" --retry 5
```

### 14. **Eşzamanlı İndirme İş Parçacıklarını Ayarlama**

10 iş parçacığı kullanarak eşzamanlı indirme yapar. Bu, indirmenin daha hızlı tamamlanmasına yardımcı olur.

```bash
python web_indirici.py "http://example.com" --threads 10
```

### Tüm Bu Örnekleri Kombine Etme

Aşağıdaki komut, bir dizi özelliği birleştirerek daha karmaşık bir senaryo oluşturur:

```bash
python web_indirici.py "http://example.com" --dir my_website --depth 3 --delay 1 --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" --random-user-agent --proxy http://proxyserver:port --no-verify-ssl --max-size 10 --include-types .css,.js,.png,.jpg --timeout 10 --cookies "sessionid=12345" --retry 3 --threads 5
```

### Açıklamalar

- **`--dir`**: İndirilen siteyi kaydedeceğiniz dizin.
- **`--depth`**: Takip edilecek bağlantıların derinliği.
- **`--delay`**: İstekler arasındaki bekleme süresi.
- **`--user-agent`** ve **`--random-user-agent`**: Belirli veya rastgele User-Agent ile istek gönderme.
- **`--proxy`**: Proxy sunucusu kullanarak istek gönderme.
- **`--no-verify-ssl`**: SSL doğrulamasını atlama.
- **`--max-size`**: İndirilecek dosyaların maksimum boyut sınırı (MB).
- **`--include-types`**: Sadece belirtilen dosya türlerini indirme.
- **`--timeout`**: Her istek için maksimum bekleme süresi (saniye).
- **`--cookies`**: İsteklerde kullanılacak çerezler.
- **`--retry`**: Başarısız istekler için yeniden deneme sayısı.
- **`--threads`**: Eşzamanlı çalışan iş parçacığı sayısı.


