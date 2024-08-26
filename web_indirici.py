import os
import argparse
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import logging
import re
import threading
from queue import Queue
import random

# Log dosyasına yazmak için logger yapılandırması
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='web_indirici.log')

# Varsayılan başlıklar
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

# Desteklenen dosya uzantıları
RESOURCE_TYPES = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.eot', '.otf', '.ico', '.mp4', '.webm', '.ogg', '.mp3', '.wav', '.pdf']

# İş parçacığı yönetimi için kuyruk
download_queue = Queue()

def sanitize_filename(filename):
    """Dosya isimlerindeki geçersiz karakterleri kaldırır."""
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def make_dirs(path):
    """Verilen yolu oluşturur, mevcut değilse."""
    if not os.path.exists(path):
        os.makedirs(path)

def is_valid_url(url):
    """URL'nin geçerli olup olmadığını kontrol eder."""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_page(url, timeout, verify_ssl):
    """Verilen URL'den sayfayı alır ve döner."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout, verify=verify_ssl)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"URL alınırken hata oluştu: {url} - Hata: {e}")
        return None

def save_file(url, save_path, timeout, verify_ssl, max_size):
    """URL'deki dosyayı belirtilen yola kaydeder."""
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=timeout, verify=verify_ssl)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        if total_size > max_size * 1024 * 1024:
            logging.warning(f"Dosya çok büyük: {url} - Atlanıyor")
            return False
        
        save_path = sanitize_filename(save_path)
        with open(save_path, 'wb') as file, tqdm(
            desc=save_path,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Dosya indirilemedi: {url} - Hata: {e}")
        return False

def download_worker(timeout, verify_ssl, max_size):
    """İndirme işlemlerini iş parçacıkları ile yönetir."""
    while True:
        url, save_path = download_queue.get()
        if url is None:
            break
        save_file(url, save_path, timeout, verify_ssl, max_size)
        download_queue.task_done()

def parse_and_download(url, base_url, save_dir, visited, delay, max_depth, current_depth, timeout, verify_ssl, max_size, include_types):
    """Verilen URL'den kaynakları indirir ve iç bağlantıları takip eder."""
    if current_depth > max_depth:
        return

    if url in visited:
        return
    visited.add(url)

    html_content = get_page(url, timeout, verify_ssl)
    if html_content is None:
        return

    parsed_url = urlparse(url)
    path = parsed_url.path
    if path.endswith('/'):
        path += 'index.html'
    elif not os.path.splitext(path)[1]:
        path += '/index.html'

    save_path = os.path.join(save_dir, path.lstrip('/'))
    make_dirs(os.path.dirname(save_path))

    soup = BeautifulSoup(html_content, 'html.parser')

    # Tüm kaynakları bul ve indir
    tags = {
        'img': 'src',
        'script': 'src',
        'link': 'href',
        'a': 'href',
        'video': 'src',
        'audio': 'src',
        'source': 'src'
    }

    for tag, attr in tags.items():
        for resource in soup.find_all(tag):
            src = resource.get(attr)
            if not src or 'nofollow' in resource.attrs.get('rel', []):
                continue
            resource_url = urljoin(url, src)
            resource_parsed_url = urlparse(resource_url)
            resource_ext = os.path.splitext(resource_parsed_url.path)[1]

            if include_types and resource_ext.lower() not in include_types:
                continue

            if resource_ext.lower() in RESOURCE_TYPES or tag == 'a':
                resource_path = os.path.join(save_dir, sanitize_filename(resource_parsed_url.path.lstrip('/')))
                make_dirs(os.path.dirname(resource_path))

                if is_valid_url(resource_url) and resource_url not in visited:
                    if resource_ext.lower() in RESOURCE_TYPES:
                        download_queue.put((resource_url, resource_path))
                        relative_path = os.path.relpath(resource_path, os.path.dirname(save_path))
                        resource[attr] = relative_path.replace('\\', '/')
                    elif tag == 'a':
                        # Recursive olarak linkleri takip et
                        parse_and_download(resource_url, base_url, save_dir, visited, delay, max_depth, current_depth + 1, timeout, verify_ssl, max_size, include_types)

    # HTML dosyasını kaydet
    save_path = sanitize_filename(save_path)
    with open(save_path, 'w', encoding='utf-8') as file:
        file.write(soup.prettify())
        logging.info(f"Kaydedildi: {save_path}")

    time.sleep(delay)

def main():
    parser = argparse.ArgumentParser(description='Gelişmiş Web Sitesi İndirici')
    parser.add_argument('url', help='Hedef web sitesi URL\'si')
    parser.add_argument('-d', '--dir', default='indirilen_site', help='Kaydedilecek dizin')
    parser.add_argument('--delay', type=float, default=1.0, help='İstekler arası gecikme süresi (saniye)')
    parser.add_argument('--depth', type=int, default=1, help='Maksimum tarama derinliği')
    parser.add_argument('--user-agent', default='Mozilla/5.0 (Windows NT 10.0; Win64; x64)', help='Özel User-Agent tanımlama')
    parser.add_argument('--threads', type=int, default=5, help='İndirme iş parçacığı sayısı')
    parser.add_argument('--cookies', help='Özel çerezler (JSON formatında)')
    parser.add_argument('--timeout', type=int, default=10, help='İstek zaman aşımı süresi (saniye)')
    parser.add_argument('--no-verify-ssl', action='store_false', help='SSL sertifikası doğrulamasını atla')
    parser.add_argument('--max-size', type=int, default=50, help='Maksimum dosya boyutu (MB)')
    parser.add_argument('--include-types', help='İndirilecek dosya türlerini belirt (örneğin: .jpg,.png)')
    parser.add_argument('--retry', type=int, default=3, help='Başarısız istekler için yeniden deneme sayısı')
    parser.add_argument('--random-user-agent', action='store_true', help='Her istek için rastgele User-Agent kullan')
    parser.add_argument('--proxy', help='İstekleri bir proxy sunucusu üzerinden gönder (örneğin: http://proxyserver:port)')
    args = parser.parse_args()

    global HEADERS
    HEADERS['User-Agent'] = args.user_agent

    if args.random_user_agent:
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'
        ]
        HEADERS['User-Agent'] = random.choice(user_agents)

    if args.cookies:
        HEADERS['Cookie'] = args.cookies

    if not is_valid_url(args.url):
        logging.error("Geçersiz URL. Lütfen doğru bir URL girin.")
        return

    include_types = [f".{ext.strip()}" for ext in args.include_types.split(',')] if args.include_types else []

    make_dirs(args.dir)
    visited = set()

    # İndirme iş parçacıklarını başlat
    threads = []
    for _ in range(args.threads):
        thread = threading.Thread(target=download_worker, args=(args.timeout, args.no_verify_ssl, args.max_size))
        thread.start()
        threads.append(thread)

    parse_and_download(args.url, args.url, args.dir, visited, args.delay, args.depth, 0, args.timeout, args.no_verify_ssl, args.max_size, include_types)

    # Tüm indirmelerin tamamlanmasını bekleyin
    download_queue.join()

    # İndirme iş parçacıklarını durdur
    for _ in range(args.threads):
        download_queue.put(None)
    for thread in threads:
        thread.join()

if __name__ == '__main__':
    main()
