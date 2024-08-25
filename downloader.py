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
RESOURCE_TYPES = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.eot', '.otf', '.ico', '.mp4', '.webm', '.ogg', '.mp3', '.wav', '.pdf']

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

def save_file(url, save_path):
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=10)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
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

def parse_and_download(url, base_url, save_dir, visited, delay, max_depth, current_depth=0):
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
                resource_path = os.path.join(save_dir, sanitize_filename(resource_parsed_url.path.lstrip('/')))
                make_dirs(os.path.dirname(resource_path))

                if is_valid_url(resource_url) and resource_url not in visited:
                    if resource_ext.lower() in RESOURCE_TYPES:
                        success = save_file(resource_url, resource_path)
                        if success:
                            relative_path = os.path.relpath(resource_path, os.path.dirname(save_path))
                            resource[attr] = relative_path.replace('\\', '/')
                    elif tag == 'a':
                        # Recursive olarak linkleri takip et
                        parse_and_download(resource_url, base_url, save_dir, visited, delay, max_depth, current_depth + 1)

    # HTML dosyasını kaydet
    save_path = sanitize_filename(save_path)
    with open(save_path, 'w', encoding='utf-8') as file:
        file.write(soup.prettify())
        logging.info(f"Kaydedildi: {save_path}")

    time.sleep(delay)

def main():
    parser = argparse.ArgumentParser(description='Web Sitesi İndirici')
    parser.add_argument('url', help='Hedef web sitesi URL\'si')
    parser.add_argument('-d', '--dir', default='downloaded_site', help='Kaydedilecek dizin')
    parser.add_argument('--delay', type=float, default=1.0, help='İstekler arası gecikme süresi (saniye)')
    parser.add_argument('--depth', type=int, default=1, help='Maksimum tarama derinliği')
    parser.add_argument('--user-agent', default='Mozilla/5.0 (Windows NT 10.0; Win64; x64)', help='Custom User-Agent tanımlama')
    args = parser.parse_args()

    global HEADERS
    HEADERS['User-Agent'] = args.user_agent

    if not is_valid_url(args.url):
        logging.error("Geçersiz URL. Lütfen doğru bir URL girin.")
        return

    make_dirs(args.dir)
    visited = set()
    parse_and_download(args.url, args.url, args.dir, visited, args.delay, args.depth)

if __name__ == '__main__':
    main()
