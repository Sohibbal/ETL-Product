import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy import create_engine
import logging

# Fungsi untuk menyimpan DataFrame ke csv
def save_to_csv(df, filename='products.csv'):
    try:
        df.to_csv(filename, index=False)
        logging.info(f"Data saved to {filename}")
        return True
    except Exception as e:
        logging.error(f"Failed to save CSV: {e}")
        return False

# Fungsi untuk menyimpan DataFrame ke Google Sheets
def save_to_google_sheets(df, json_keyfile, spreadsheet_id):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(spreadsheet_id).sheet1 # Menggunakan open_by_key dengan spreadsheet_id
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
        logging.info("Data saved to Google Sheets")
        return True
    except Exception as e:
        logging.error(f"Failed to save to Google Sheets: {e}")
        return False

# Fungsi untuk menyimpan DataFrame ke PostgreSQL
def save_to_postgres(df, db_uri, table_name='fashion_products'):
    try:
        engine = create_engine(db_uri)
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        logging.info("Data saved to PostgreSQL")
        return True
    except Exception as e:
        logging.error(f"Failed to save to PostgreSQL: {e}")
        return False