import unittest
from unittest.mock import patch
import pandas as pd
from utils.transform import clean_price, clean_rating, clean_colors, clean_text_field, process_dataframe

class TestTransform(unittest.TestCase):

    # Test fungsi clean_price sukses
    def test_clean_price_success(self):
        """Test jalur sukses konversi harga."""
        self.assertEqual(clean_price("$64.24"), 1027840.0) 
        self.assertEqual(clean_price("Price Unavailable"), 0.0)
        self.assertEqual(clean_price(None), 0.0)

    # Test fungsi clean_price gagal
    @patch('utils.transform.re.sub')
    def test_clean_price_failure(self, mock_sub):
        """Test simulasi error pada regex."""
        mock_sub.side_effect = Exception("Regex Error")
        result = clean_price("$100")
        self.assertEqual(result, 0.0)

    # Test fungsi clean_rating sukses
    def test_clean_rating_success(self):
        """Test jalur sukses konversi rating."""
        self.assertEqual(clean_rating("Rating: ⭐ 4.8 / 5"), 4.8)
        self.assertEqual(clean_rating("Invalid Rating"), 0.0)
        self.assertEqual(clean_rating(None), 0.0)

    # Test fungsi clean_rating gagal
    @patch('utils.transform.re.search')
    def test_clean_rating_failure(self, mock_search):
        """Test simulasi error saat mencari pola rating."""
        mock_search.side_effect = Exception("Regex Boom")
        result = clean_rating("Rating: 5.0")
        self.assertEqual(result, 0.0)

    # Test fungsi clean_colors sukses
    def test_clean_colors_success(self):
        """Test jalur sukses ambil angka warna."""
        self.assertEqual(clean_colors("3 Colors"), 3)
        self.assertEqual(clean_colors("Colors"), 1)
        self.assertEqual(clean_colors(None), 1)

    # Test fungsi clean_colors gagal
    @patch('utils.transform.re.search')
    def test_clean_colors_failure(self, mock_search):
        """Test simulasi error regex warna."""
        mock_search.side_effect = Exception("Unexpected Error")
        result = clean_colors("3 Colors")
        self.assertEqual(result, 1)

    # Test fungsi clean_text_field sukses
    def test_clean_text_field_success(self):
        """Test hapus prefix string."""
        self.assertEqual(clean_text_field("Size: M", "Size: "), "M")
        self.assertEqual(clean_text_field(None, "Size: "), "None")

    # Test fungsi clean_text_field gagal
    def test_clean_text_field_failure(self):
        """Sengaja kirim prefix berupa ANGKA (123).
        Fungsi .replace() akan error karena butuh string, lalu masuk ke except.
        """
        # Input "Size: M", tapi prefix-nya angka 123 (bukan string)
        result = clean_text_field("Size: M", 123)
        
        # Di blok except, akan return str(text) asli
        self.assertEqual(result, "Size: M")

    # Test fungsi process_dataframe sukses
    def test_process_dataframe_success(self):
        """Test transformasi data normal."""
        raw_data = [{"Title": "T-shirt 2", "Price": "$102.15", "Rating": "3.9", "Colors": "3", "Size": "M", "Gender": "Women", "timestamp": "2025"}]
        df = process_dataframe(raw_data)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['Title'], "T-shirt 2")

    # Test fungsi process_dataframe dengan data kosong
    def test_process_dataframe_empty_success(self):
        """Test jika input data kosong."""
        df = process_dataframe([])
        self.assertTrue(df.empty)

    # Test fungsi process_dataframe gagal
    @patch('utils.transform.pd.DataFrame')
    def test_process_dataframe_failure(self, mock_df):
        """
        Test simulasi Pandas Crash.
        Panggilan ke-1: Error (akan masuk exception).
        Panggilan ke-2: Sukses return DF kosong (di dalam exception).
        """
        mock_df.side_effect = [Exception("Pandas Crash"), pd.DataFrame()]
        
        df = process_dataframe([{'Title': 'Test'}])
        self.assertTrue(df.empty)

if __name__ == '__main__':
    unittest.main()