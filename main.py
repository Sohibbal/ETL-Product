from utils.extract import scrape_fashion_data
from utils.transform import process_dataframe
from utils.load import save_to_csv, save_to_google_sheets, save_to_postgres
import logging
import pandas as pd

# Konfigurasi PostgreSQL (Sesuaikan dengan milikmu)
# Format: postgresql://user:password@host:port/dbname
DB_URI = "postgresql://sohibbal:sohibbal123@localhost:5432/fashion_db"
GSHEET_JSON = "google-sheets-api.json"

def main():
    logging.info("Pipeline Started")

    # 1. Extract
    raw_data = scrape_fashion_data("https://fashion-studio.dicoding.dev", end_page=50, limit=1000)
    
    if not raw_data:
        logging.error("No data scraped. Exiting.")
        return
    
    try:
        raw_df = pd.DataFrame(raw_data)
        save_to_csv(raw_df, filename='products_raw.csv') # Simpan data mentah
        logging.info("Raw data saved successfully.")
    except Exception as e:
        logging.warning(f"Failed to save raw data: {e}")

    # 2. Transform
    clean_df = process_dataframe(raw_data)
    
    if clean_df.empty:
        logging.error("Data empty after transformation. Exiting.")
        return

    # 3. Load (Advanced: 3 Repositori)
    # A. CSV
    save_to_csv(clean_df)
    
    # B. Google Sheets
    # Pastikan file json ada, jika tidak skip agar tidak error fatal
    SPREADSHEET_ID = "1oP5HKps6fFgtbaBqzXqPrB8rNxwdYQyiikr0Zemr_pg" 

    try:
        save_to_google_sheets(clean_df, GSHEET_JSON, SPREADSHEET_ID)
    except Exception as e:
        logging.warning(f"Google Sheets skipped: {e}")

    # C. PostgreSQL
    try:
        save_to_postgres(clean_df, DB_URI)
    except Exception as e:
        logging.warning(f"PostgreSQL skipped: {e}")

    logging.info("Pipeline Finished")

if __name__ == "__main__":
    main()