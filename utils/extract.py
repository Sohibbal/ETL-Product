import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fungsi untuk mendapatkan konten halaman
def get_page_content(session, url):
    try:
        response = session.get(url, timeout=10) 
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return None

# Fungsi utama untuk scraping data fashion
def scrape_fashion_data(base_url, start_page=1, end_page=50, limit=1000):
    data = []
    
    # Menggunakan Session untuk semua request
    with requests.Session() as session:
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        try:
            for page in range(start_page, end_page + 1):
                if len(data) >= limit:
                    break
                
                url = f"{base_url}/page{page}" if page > 1 else base_url # Typo fix: page/
                logging.info(f"Scraping page: {page}")
                
                # Mengambil konten halaman
                content = get_page_content(session, url)
                
                if not content:
                    continue
                
                # Parsing HTML dengan BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                products = soup.find_all('div', class_='collection-card') 

                if not products:
                    logging.warning(f"No products found on page {page}")
                    continue

                for product in products:
                    if len(data) >= limit:
                        break

                    try:
                        # Mengambil title produk
                        title_elem = product.find('h3', class_='product-title')
                        title = title_elem.get_text(strip=True)

                        # Logika Harga (Span vs P)
                        price_elem = product.find('span', class_='price')
                        if not price_elem:
                            price_elem = product.find('p', class_='price')
                        
                        price = price_elem.get_text(strip=True)

                        # Logika Detail Produk (untuk tags p)
                        details_container = product.find('div', class_='product-details')

                        if details_container:
                            paragraphs = details_container.find_all('p')
                            for p in paragraphs:
                                text = p.get_text(strip=True)
                                if "Rating:" in text: rating = text
                                elif "Colors" in text: colors = text
                                elif "Size:" in text: size = text
                                elif "Gender:" in text: gender = text

                        item = {
                            "Title": title,
                            "Price": price,
                            "Rating": rating,
                            "Colors": colors,
                            "Size": size,
                            "Gender": gender,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        data.append(item)
                        
                    except Exception as e:
                        logging.error(f"Error parsing product item: {e}")
                        continue
                        
        except Exception as e:
            logging.error(f"Critical error in scraping process: {e}")
    
    return data