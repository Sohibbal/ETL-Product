import unittest
from unittest.mock import patch, Mock
import requests
from utils.extract import get_page_content, scrape_fashion_data

class TestExtract(unittest.TestCase):

    # Helper HTML produk dummy
    def _create_dummy_product(self, title="Item 1"):
        return f"""
        <div class="collection-card">
            <h3 class="product-title">{title}</h3>
            <span class="price">$10.00</span>
            <div class="product-details">
                <p>Rating: 5.0</p>
                <p>1 Colors</p>
                <p>Size: S</p>
                <p>Gender: M</p>
            </div>
        </div>
        """

    # Test fungsi get_page_content sukses
    def test_get_page_content_success(self):
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html></html>"
        mock_session.get.return_value = mock_response

        result = get_page_content(mock_session, "http://test.com")
        self.assertEqual(result, b"<html></html>")

    # Test fungsi get_page_content gagal
    def test_get_page_content_failure(self):
        mock_session = Mock()
        mock_session.get.side_effect = requests.exceptions.RequestException("Error")
        result = get_page_content(mock_session, "http://test.com")
        self.assertIsNone(result)

    # Test fungsi scrape_fashion_data sukses
    @patch('utils.extract.requests.Session')
    @patch('utils.extract.get_page_content')
    def test_scrape_fashion_data_success(self, mock_content_func, mock_session_cls):
        """Test parsing data normal dengan HTML lengkap."""
        html_dummy = f"<html><body>{self._create_dummy_product('Baju Test')}</body></html>"
        mock_content_func.return_value = html_dummy.encode('utf-8')

        data = scrape_fashion_data("http://dummy.com", end_page=1, limit=5)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['Title'], "Baju Test")
        self.assertEqual(data[0]['Colors'], "1 Colors")

    # Test fungsi scrape_fashion_data dengan halaman kosong (continue)
    @patch('utils.extract.requests.Session')
    @patch('utils.extract.get_page_content')
    def test_scrape_content_continue(self, mock_content_func, mock_session_cls):
        """Test skip halaman jika konten None."""
        html_success = f"<html><body>{self._create_dummy_product('Item Page 2')}</body></html>"
        mock_content_func.side_effect = [None, html_success.encode('utf-8')]

        data = scrape_fashion_data("http://dummy.com", start_page=1, end_page=2, limit=10)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['Title'], "Item Page 2")

    # Test log warning jika tidak ada produk
    @patch('utils.extract.requests.Session')
    @patch('utils.extract.get_page_content')
    def test_scrape_no_products_found(self, mock_content_func, mock_session_cls):
        """Test log warning jika tidak ada produk."""
        html_empty = "<html><body><div>No items here</div></body></html>"
        mock_content_func.return_value = html_empty.encode('utf-8')
        
        with self.assertLogs(level='WARNING') as log:
            data = scrape_fashion_data("http://dummy.com", end_page=1, limit=5)
            self.assertEqual(len(data), 0)
            self.assertTrue(any("No products found" in m for m in log.output))

    # Test break loop jika limit tercapai
    @patch('utils.extract.requests.Session')
    @patch('utils.extract.get_page_content')
    def test_scrape_limit_break(self, mock_content_func, mock_session_cls):
        """Test break loop jika limit tercapai."""
        html_multi = "<html><body>"
        html_multi += self._create_dummy_product("Item 1")
        html_multi += self._create_dummy_product("Item 2")
        html_multi += self._create_dummy_product("Item 3")
        html_multi += "</body></html>"
        
        mock_content_func.return_value = html_multi.encode('utf-8')

        data = scrape_fashion_data("http://dummy.com", limit=1)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['Title'], "Item 1")

    # Test fungsi scrape_fashion_data gagal (outer exception)
    @patch('utils.extract.requests.Session')
    @patch('utils.extract.get_page_content')
    def test_scrape_critical_failure(self, mock_content_func, mock_session_cls):
        """Test simulasi error generic di luar loop (Outer Exception)."""
        mock_content_func.side_effect = Exception("General Error Out Loop")
        data = scrape_fashion_data("http://dummy.com", end_page=1)
        self.assertEqual(data, [])

    # Test fallback harga di tag <p>
    @patch('utils.extract.requests.Session')
    @patch('utils.extract.get_page_content')
    def test_scrape_price_fallback_p(self, mock_content_func, mock_session_cls):
        """Test fallback harga di tag <p>."""
        html_p_price = """
        <html><body>
            <div class="collection-card">
                <h3 class="product-title">Item P Price</h3>
                <p class="price">$99.99</p>
                <div class="product-details">
                    <p>Rating: 5.0</p>
                    <p>1 Colors</p>
                    <p>Size: S</p>
                    <p>Gender: M</p>
                </div>
            </div>
        </body></html>
        """
        mock_content_func.return_value = html_p_price.encode('utf-8')
        data = scrape_fashion_data("http://dummy.com", end_page=1)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['Price'], "$99.99")

    # Test parsing error di dalam loop (continue)
    @patch('utils.extract.requests.Session')
    @patch('utils.extract.get_page_content')
    def test_scrape_item_parsing_error(self, mock_content_func, mock_session_cls):
        """
        Test simulasi error parsing item di dalam loop.
        1. Item 1: Valid.
        2. Item 2: Rusak Parah (Tidak ada harga -> Crash AttributeError).
        Hasil: Item 1 diambil, Item 2 memicu error, dilog, dan di-skip (continue).
        """
        
        # HTML Campuran: 1 Valid, 1 Rusak (Tanpa tag harga)
        html_mixed = "<html><body>"
        html_mixed += self._create_dummy_product("Item Valid")
        # Item Rusak (Tidak ada harga) -> Akan memicu error saat parsing
        html_mixed += """
        <div class="collection-card">
            <h3 class="product-title">Item Rusak</h3>
            </div>
        """
        html_mixed += "</body></html>"
        
        mock_content_func.return_value = html_mixed.encode('utf-8')

        # Menggunakan assertLogs untuk memastikan error-nya tertangkap dan dicatat
        with self.assertLogs(level='ERROR') as log:
            data = scrape_fashion_data("http://dummy.com", end_page=1)
            
            # 1 data Item Valid
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['Title'], "Item Valid")
            
            self.assertTrue(any("Error parsing product item" in m for m in log.output))

if __name__ == '__main__':
    unittest.main()