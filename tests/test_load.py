import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from utils.load import save_to_csv, save_to_google_sheets, save_to_postgres

class TestLoad(unittest.TestCase):
    
    def setUp(self):
        # Sample DataFrame untuk testing
        self.df = pd.DataFrame({
            'Title': ['T-shirt 2', 'Jeans Regular'],
            'Price': [1634400.0, 500000.0],
            'Rating': [3.9, 4.5],
            'Colors': [3, 2],
            'Size': ['M', 'L'],
            'Gender': ['Women', 'Men'],
            'timestamp': ['2025-12-20 18:01:02', '2025-12-20 18:05:00']
        })

    # Test Sukses (to csv)
    @patch('pandas.DataFrame.to_csv')
    def test_save_to_csv_success(self, mock_to_csv):
        result = save_to_csv(self.df, 'test.csv')
        self.assertTrue(result)
        mock_to_csv.assert_called_with('test.csv', index=False)

    # Test Gagal (to csv)
    @patch('pandas.DataFrame.to_csv')
    def test_save_to_csv_failure(self, mock_to_csv):
        # Test Gagal (Simulasi Error Disk Penuh)
        mock_to_csv.side_effect = Exception("Disk Full")
        result = save_to_csv(self.df, 'test.csv')
        self.assertFalse(result)

    # Test Sukses (to Google Sheets)
    @patch('gspread.authorize')
    @patch('oauth2client.service_account.ServiceAccountCredentials.from_json_keyfile_name')
    def test_save_to_google_sheets_success(self, mock_creds, mock_auth):
        """Test Google Sheets Sukses."""
        # Setup Mock Object
        mock_client = MagicMock()
        mock_sheet = MagicMock()
      
        # Rangkaian Mocking
        mock_auth.return_value = mock_client
        mock_client.open_by_key.return_value.sheet1 = mock_sheet
        result = save_to_google_sheets(self.df, 'dummy.json', 'dummy_id')

        # Assertions
        self.assertTrue(result)
        mock_client.open_by_key.assert_called_with('dummy_id')
        mock_sheet.clear.assert_called()
        mock_sheet.update.assert_called()

    # Test Gagal (to Google Sheets)
    @patch('oauth2client.service_account.ServiceAccountCredentials.from_json_keyfile_name')
    def test_save_to_google_sheets_failure(self, mock_creds):
        """Test Google Sheets Gagal (Simulasi Error Kredensial)."""
        mock_creds.side_effect = Exception("Invalid Credentials")
        
        result = save_to_google_sheets(self.df, 'dummy.json', 'dummy_id')
        self.assertFalse(result)

    # Test Sukses (to PostgreSQL)
    @patch('utils.load.create_engine')
    @patch('pandas.DataFrame.to_sql')
    def test_save_to_postgres_success(self, mock_to_sql, mock_engine):
        result = save_to_postgres(self.df, 'postgresql://user:pass@localhost/testdb')
        self.assertTrue(result)
        mock_to_sql.assert_called()

    # Test Gagal (to PostgreSQL)
    @patch('utils.load.create_engine')
    def test_save_to_postgres_failure(self, mock_engine):
        """Test PostgreSQL Gagal (Simulasi Error Koneksi DB)."""
        mock_engine.side_effect = Exception("Database Down")
        
        result = save_to_postgres(self.df, 'postgresql://user:pass@localhost/testdb')
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()