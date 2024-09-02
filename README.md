
### `README.md`

```markdown
# WebSiteFetcher v1.0

## Açıklama

**WebSiteFetcher** v1.0, belirli bir web sitesini tarayıp, HTML içeriği ve diğer kaynak dosyalarını (görseller, scriptler, stiller vb.) yerel bir dizine indirmenizi sağlayan bir Python uygulamasıdır. Beta sürümünde kullanılabilir, ancak Pro sürümü ücretlidir.

## Özellikler

- Web sitesinin tamamını veya belirli derinliklere kadar tarama
- HTML sayfalarını ve ilgili kaynakları indirme
- Kesintiye uğrayan indirmeleri devam ettirme desteği
- İndirme sürecinde günlük kaydı ve hata raporlama
- Farklı dosya türleri için genişletilmiş destek

## Gereksinimler

- Python 3.6 veya üzeri

## Kurulum

1. Projeyi klonlayın veya indirin:

    ```bash
    git clone https://github.com/username/web-site-fetcher.git
    cd web-site-fetcher
    ```

2. Gerekli Python kütüphanelerini yükleyin:

    ```bash
    pip install -r requirements.txt
    ```

## Kullanım

Programı çalıştırmak için aşağıdaki komutu kullanabilirsiniz:

```bash
python web_site_fetcher.py [URL] [OPTIONS]
```

### Seçenekler

- `-d`, `--dir`: Dosyaların kaydedileceği dizin (varsayılan: `downloaded_site`)
- `--delay`: İstekler arasında bekleme süresi (saniye cinsinden)
- `--depth`: Maksimum tarama derinliği
- `--user-agent`: Özel User-Agent
- `--chunk-size`: İndirme parçası boyutu (bayt cinsinden)
- `--timeout`: İndirme istekleri için zaman aşımı (saniye cinsinden)
- `--retries`: Başarısız indirmeler için yeniden deneme sayısı
- `--retry-delay`: Yeniden denemeler arasındaki gecikme (saniye cinsinden)
- `--resume`: Kesintiye uğrayan indirmeleri devam ettirme
- `--log-file`: Günlük dosyası yolu
- `--verbose`, `-v`: Ayrıntılı çıktı
- `--all`: Her türlü dosyayı indirme

## Örnek

```bash
python web_site_fetcher.py https://example.com --depth 2 --all
```

Bu komut, `https://example.com` adresindeki siteyi 2 derinlik seviyesine kadar tarar ve tüm dosyaları indirir.

## Katkıda Bulunma

Herhangi bir katkıda bulunmak istiyorsanız, lütfen bir çekme isteği (pull request) açın veya bir sorun raporlayın.

## Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.
```

### `requirements.txt`

```plaintext
requests==2.28.2
beautifulsoup4==4.12.2
tqdm==4.65.0
```

### Açıklamalar:
- **Proje Adı**: `WebSiteFetcher` olarak belirledim. Bu ad, projenin amacını açıkça belirtir ve genel bir adlandırma yapar.
- **Versiyon**: `v1.0`, projenin ilk sürümünü temsil eder. Bu versiyon numarasını projenizin gelişimine göre güncelleyebilirsiniz.
- **README.md**: Projenin adı, açıklaması, özellikleri, kurulum ve kullanım bilgilerini içerir.
- **requirements.txt**: Projeyi çalıştırmak için gereken Python kütüphanelerini belirtir.

Başka bir şey eklemek veya değiştirmek isterseniz, lütfen bana bildirin!
