import pandas as pd
import re
import logging

# Fungsi transform data price
def clean_price(price_str):
    try:
        if pd.isna(price_str): return 0.0
        # Hapus semua karakter kecuali digit dan titik desimal
        clean_str = re.sub(r'[^\d.]', '', str(price_str))
        if not clean_str: return 0.0
        usd = float(clean_str)
        converted = usd * 16000
        return float(round(converted, 0))
    except Exception:
        return 0.0

# Fungsi transform data rating
def clean_rating(rating_str):
    try:
        text = str(rating_str)
        
        # Regex untuk mengambil angka pertama (bisa desimal)
        match = re.search(r'(\d+(\.\d+)?)', text)
        
        if match:
            return float(match.group(1))
        else:
            return 0.0
            
    except Exception as e:
        logging.error(f"Error cleaning rating '{rating_str}': {e}")
        return 0.0

# Fungsi transform data colors
def clean_colors(color_str):
    try:
        return int(re.search(r'\d+', str(color_str)).group())
    except Exception:
        return 1 

# Fungsi untuk membersihkan field teks dengan prefix tertentu
def clean_text_field(text, prefix):
    try:
        return str(text).replace(prefix, "").strip()
    except Exception:
        return str(text)

# Fungsi utama untuk memproses transform DataFrame
def process_dataframe(data_list):
    logging.info("Starting transformation...")
    
    if not data_list:
        logging.error("No data to transform")
        return pd.DataFrame()

    try:
        df = pd.DataFrame(data_list)
        print("\nInitial DataFrame info (before transformation):")
        df.info()

        # Menghapus Data Duplikat
        df.drop_duplicates(inplace=True)

        # Menghapus Produk dengan Title "Unknown Product"
        df = df[df['Title'] != "Unknown Product"]
        
        # Cleaning & Konversi Tipe Data
        df['Price'] = df['Price'].apply(clean_price).astype(float)
        df['Rating'] = df['Rating'].apply(clean_rating).astype(float)
        df['Colors'] = df['Colors'].apply(clean_colors).astype('int64')
        df['Size'] = df['Size'].apply(lambda x: clean_text_field(x, "Size: ")).astype(str)
        df['Gender'] = df['Gender'].apply(lambda x: clean_text_field(x, "Gender: ")).astype(str)

        # Filtering Data Invalid (Harga > 0 dan Rating > 0) indikasi Price Unavailable atau Invalid Rating
        df = df[(df['Price'] > 0) & (df['Rating'] > 0)]
        print("\nInitial DataFrame info (after transformation):")
        df.info()

        logging.info(f"Transformation done. Rows: {len(df)}")
        return df

    except Exception as e:
        logging.error(f"Error during transformation: {e}")
        return pd.DataFrame()