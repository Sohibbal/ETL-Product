## PANDUAN MENJALANKAN PROYEK (ETL & TESTING)
-- subheading
Panduan ini menjelaskan langkah-langkah menjalankan proyek ETL (Extract, Transform, Load) beserta unit testing dan code coverage menggunakan Python 3.12.

Pastikan Anda berada di folder root proyek. Buat dan aktifkan virtual environment agar isolasi dependensi tetap terjaga.

### Membuat virtual environment dengan Python 3.12:

py -3.12 -m venv namavenv
atau
python -m venv namavenv

Catatan: namavenv dapat disesuaikan sesuai kebutuhan.

### Mengaktifkan virtual environment:

Windows (PowerShell):
.\namavenv\Scripts\Activate.ps1

Windows (CMD):
namavenv\Scripts\activate

Mac / Linux:
source namavenv/bin/activate

Pastikan muncul nama environment pada terminal, misalnya (namavenv).

### Install seluruh library yang dibutuhkan proyek (pandas, requests, pytest, dan lainnya) dengan perintah:

pip install -r requirements.txt

Untuk menjalankan proses Extract, Transform, dan Load, jalankan:

python main.py

Testing dilakukan menggunakan pytest untuk memastikan seluruh fungsi berjalan dengan baik dan code coverage pada folder utils mencapai 100%.

### Menjalankan unit test:

python -m pytest tests/

Melihat coverage (persentase):

python -m pytest --cov=utils tests/

Melihat detail baris kode yang belum ter-cover:

python -m pytest --cov=utils --cov-report term-missing tests/

### Google Sheets Output:
https://docs.google.com/spreadsheets/d/1oP5HKps6fFgtbaBqzXqPrB8rNxwdYQyiikr0Zemr_pg/edit?usp=sharing
