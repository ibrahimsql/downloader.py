import os
import argparse
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import logging
import re

# Logger configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Default headers for requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

# Supported file types for download (extended)
RESOURCE_TYPES = [
    '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.eot', '.otf', 
    '.ico', '.mp4', '.webm', '.ogg', '.mp3', '.wav', '.pdf', '.html', '.htm', '.xhtml', '.mhtml', '.json', 
    # Additional types...
    '.astx', '.key', '.gmi', '.scss', '.xd', '.ssp', '.btapp', '.xhtm', '.h5p', '.aro', '.p7b', '.mml', 
    # Add all other types you listed
]

def sanitize_filename(filename):
    """Sanitize the filename by replacing invalid characters with underscores."""
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def make_dirs(path):
    """Create directories if they do not exist."""
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        logging.error(f"Error creating directory {path}: {e}")

def is_valid_url(url):
    """Check if the URL is valid."""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_page(url):
    """Fetch page content from the given URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL: {url} - Error: {e}")
        return None

def save_file(url, save_path, chunk_size=1024, retries=3, retry_delay=5, resume=False):
    """Save the file from the URL to the local path."""
    try:
        headers = HEADERS.copy()
        if resume and os.path.exists(save_path):
            headers['Range'] = f'bytes={os.path.getsize(save_path)}-'
        
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        save_path = sanitize_filename(save_path)

        mode = 'ab' if resume else 'wb'
        with open(save_path, mode) as file, tqdm(
            desc=save_path,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=chunk_size):
                size = file.write(data)
                bar.update(size)
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"File download failed: {url} - Error: {e}")
        time.sleep(retry_delay)
        if retries > 0:
            return save_file(url, save_path, chunk_size, retries-1, retry_delay, resume)
        return False

def parse_and_download(url, base_url, save_dir, visited, delay, max_depth, current_depth=0, all_files=False):
    """Parse the webpage and download resources recursively."""
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

    # Find and download all resources
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

            # If --all flag is used, consider all links regardless of the extension
            if all_files or resource_ext.lower() in RESOURCE_TYPES or tag == 'a':
                resource_path = os.path.join(save_dir, sanitize_filename(resource_parsed_url.path.lstrip('/')))
                make_dirs(os.path.dirname(resource_path))

                if is_valid_url(resource_url) and resource_url not in visited:
                    if all_files or resource_ext.lower() in RESOURCE_TYPES:
                        success = save_file(resource_url, resource_path)
                        if success:
                            relative_path = os.path.relpath(resource_path, os.path.dirname(save_path))
                            resource[attr] = relative_path.replace('\\', '/')
                    elif tag == 'a':
                        # Recursively follow links
                        parse_and_download(resource_url, base_url, save_dir, visited, delay, max_depth, current_depth + 1, all_files)

    # Save the modified HTML
    save_path = sanitize_filename(save_path)
    with open(save_path, 'w', encoding='utf-8') as file:
        file.write(soup.prettify())
        logging.info(f"Saved: {save_path}")

    time.sleep(delay)

def main():
    parser = argparse.ArgumentParser(description='Web Site Downloader')
    parser.add_argument('url', help='Target website URL')
    parser.add_argument('-d', '--dir', default='downloaded_site', help='Directory to save files')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests (seconds)')
    parser.add_argument('--depth', type=int, default=1, help='Maximum crawling depth')
    parser.add_argument('--user-agent', default='Mozilla/5.0 (Windows NT 10.0; Win64; x64)', help='Custom User-Agent')
    parser.add_argument('--chunk-size', type=int, default=1024, help='Download chunk size')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout for download requests (seconds)')
    parser.add_argument('--retries', type=int, default=3, help='Number of retries for failed downloads')
    parser.add_argument('--retry-delay', type=int, default=5, help='Delay between retries (seconds)')
    parser.add_argument('--resume', action='store_true', help='Resume interrupted downloads')
    parser.add_argument('--log-file', help='Log file path')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--all', action='store_true', help='Download all files regardless of type')

    args = parser.parse_args()

    # Configure logging
    if args.log_file:
        logging.basicConfig(filename=args.log_file, level=logging.DEBUG if args.verbose else logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    global HEADERS
    HEADERS['User-Agent'] = args.user_agent

    if not is_valid_url(args.url):
        logging.error("Invalid URL. Please enter a correct URL.")
        return

    make_dirs(args.dir)
    visited = set()
    parse_and_download(args.url, args.url, args.dir, visited, args.delay, args.depth, all_files=args.all)

if __name__ == '__main__':
    main()
