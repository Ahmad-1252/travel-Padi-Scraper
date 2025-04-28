# Travel-Padi Scraper
A Python-based web scraper that extracts hotel and dive resort data from PADI Travel APIs and webpages, and saves the compiled information into structured Excel files.

## Features
Fetches resort, dive center, liveaboard, and activity listings from PADI Travel.

### Extracts detailed information including:

Hotel/Resort Name

Address

Phone Number

Email

Website

### Activities Offered

Handles API pagination and category-based scraping.

Automatically saves the data into Excel files (.xlsx) with backup management.

Graceful handling of network errors and missing data.

### Technologies Used
Python 3

Requests - For API and webpage HTTP requests.

lxml - For fast and flexible HTML parsing with XPath.

Pandas - For structured data handling and Excel export.

os - For file management (backup and save operations).

### Setup Instructions
Clone the repository:

git clone https://github.com/your-username/Travel-Padi-Scraper.git

cd Travel-Padi-Scraper

### Install dependencies:
pip install requests pandas lxml

### Run the scraper:
python file.py


### Output Files
all_urls.csv: List of all resort/activity page URLs categorized by type.

tarve_padi_data.xlsx: Scraped hotel/resort/activity information.

tarve_padi_data_backup.xlsx: Backup of the previous data run.

### Project Structure
├── travel_padi_scraper.py   # Main scraper script
├── all_urls.csv             # URLs collected
├── tarve_padi_data.xlsx      # Final extracted data
├── tarve_padi_data_backup.xlsx  # Backup of previous extraction
├── README.md                # Project documentation

### Notes
The scraper respects a timeout and retries on failures to avoid overwhelming the server.

Some categories like dive-centers, dive-trips, and courses are limited to the first 30 pages to manage server load.

### License
This project is for educational and personal use only. Please respect PADI Travel's terms of service and robots.txt when scraping.

### Author
Ahmad
GitHub: Ahmad-1252
