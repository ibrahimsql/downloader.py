import os
import argparse
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import logging
import re

# Logger yapılandırması
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# İstekler için varsayılan başlıklar
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

# Desteklenen dosya uzantıları
RESOURCE_TYPES = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.eot', '.otf', '.ico', '.mp4', '.webm', '.ogg', '.mp3', '.wav', '.pdf', '.html', '.htm']

def print_banner():
    banner = """
    ***************************************
    *         Web Sitesi İndirici         *
    *     Gelişmiş İndirici Versiyonu     *
    *   @YourName | GitHub: @YourHandle   *
    ***************************************
    """
    print(banner)

def sanitize_filename(filename):
    """Dosya isimlerindeki geçersiz karakterleri kaldırır."""
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"URL alınırken hata oluştu: {url} - Hata: {e}")
        return None

def save_file(url, save_path, max_file_size=None, overwrite=False):
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=10)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))

        if max_file_size and total_size > max_file_size:
            logging.warning(f"Dosya {url} belirtilen maksimum boyutu ({max_file_size} bayt) aşıyor, atlanıyor.")
            return False

        save_path = sanitize_filename(save_path)

        if os.path.exists(save_path) and not overwrite:
            logging.info(f"Dosya zaten mevcut: {save_path}, atlanıyor.")
            return False

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

def parse_and_download(url, base_url, save_dir, visited, delay, max_depth, current_depth=0, exclude_types=[], max_file_size=None, overwrite=False):
    if current_depth > max_depth:
        return

    if url in visited:
        return
    visited.add(url)

    html_content = get_page(url)
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

            if resource_ext.lower() in RESOURCE_TYPES or tag == 'a':
                if any(resource_ext.lower() == ext for ext in exclude_types):
                    logging.info(f"Dosya {resource_url} hariç tutulan uzantı ({resource_ext}) nedeniyle atlanıyor.")
                    continue

                resource_path = os.path.join(save_dir, sanitize_filename(resource_parsed_url.path.lstrip('/')))
                make_dirs(os.path.dirname(resource_path))

                if is_valid_url(resource_url) and resource_url not in visited:
                    if resource_ext.lower() in RESOURCE_TYPES:
                        success = save_file(resource_url, resource_path, max_file_size=max_file_size, overwrite=overwrite)
                        if success:
                            relative_path = os.path.relpath(resource_path, os.path.dirname(save_path))
                            resource[attr] = relative_path.replace('\\', '/')
                    elif tag == 'a':
                        # Recursive olarak linkleri takip et
                        parse_and_download(resource_url, base_url, save_dir, visited, delay, max_depth, current_depth + 1, exclude_types, max_file_size, overwrite)

    # HTML dosyasını kaydet
    save_path = sanitize_filename(save_path)
    with open(save_path, 'w', encoding='utf-8') as file:
        file.write(soup.prettify())
        logging.info(f"Kaydedildi: {save_path}")

    time.sleep(delay)

def main():
    print_banner()

    parser = argparse.ArgumentParser(description='Gelişmiş Web Sitesi İndirici')
    parser.add_argument('url', help='Hedef web sitesi URL\'si')
    parser.add_argument('-d', '--dir', default='downloaded_site', help='Kaydedilecek dizin')
    parser.add_argument('--delay', type=float, default=1.0, help='İstekler arası gecikme süresi (saniye)')
    parser.add_argument('--depth', type=int, default=1, help='Maksimum tarama derinliği')
    parser.add_argument('--user-agent', default=HEADERS['User-Agent'], help='Custom User-Agent tanımlama')
    parser.add_argument('--timeout', type=int, default=10, help='Her istek için zaman aşımı süresi (saniye)')
    parser.add_argument('--log-file', default=None, help='Logları kaydetmek için dosya yolu')
    parser.add_argument('--no-recursion', action='store_true', help='Linkleri takip etmeden sadece ana sayfayı indir')
    parser.add_argument('--include-media', action='store_true', help='Medya dosyalarını (resimler, videolar) indir')
    parser.add_argument('--exclude-types', type=str, help='Hariç tutulacak dosya uzantılarını belirt (.png,.jpg gibi virgülle ayrılmış)')
    parser.add_argument('--overwrite', action='store_true', help='Zaten mevcut olan dosyaların üzerine yaz')
    parser.add_argument('--retry', type=int, default=3, help='Bir isteğin başarısız olması durumunda yeniden deneme sayısı')
    parser.add_argument('--proxy', type=str, help='Proxy sunucusu (ör. http://proxyserver:port)')
    parser.add_argument('--headers', type=str, help='İsteğe özel HTTP başlıkları ekle (ör. "Authorization: Bearer token")')
    parser.add_argument('--cookies', type=str, help='İsteklere özel çerezler ekle (ör. "sessionid=abcd1234; csrftoken=xyz9876")')
    parser.add_argument('--ignore-certs', action='store_true', help='SSL sertifika hatalarını yoksay')
    parser.add_argument('--silent', action='store_true', help='Sadece kritik hataları göster (sessiz mod)')
    parser.add_argument('--max-file-size', type=int, help='İndirilecek dosyanın maksimum boyutunu bayt cinsinden belirt')
    parser.add_argument('--output-format', type=str, help='Kaydedilen dosyaların adlandırma formatını belirle')
    parser.add_argument('--auth', type=str, help='HTTP Basic Authentication için kullanıcı adı ve şifre ekle (ör. "username:password")')
    args = parser.parse_args()

    global HEADERS
    HEADERS['User-Agent'] = args.user_agent

    if args.log_file:
        file_handler = logging.FileHandler(args.log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)

    if args.silent:
        logging.getLogger().setLevel(logging.CRITICAL)

    if not is_valid_url(args.url):
        logging.error("Geçersiz URL. Lütfen doğru bir URL girin.")
        return

    make_dirs(args.dir)
    visited = set()

    exclude_types = args.exclude_types.split(',') if args.exclude_types else []
    
    parse_and_download(args.url, args.url, args.dir, visited, args.delay, args.depth if not args.no_recursion else 0, exclude_types, args.max_file_size, args.overwrite)

if __name__ == '__main__':
    main()
