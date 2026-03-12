# 🏙️ Urban Services Intelligence — Cairo

A **Data Engineering pipeline** that scrapes, stages, cleans, enriches, and warehouses urban service locations across Cairo using **Google Maps, Python, Selenium, and SQL Server**.

The system builds a structured dataset of key city services such as hospitals, schools, gas stations, clubs, and universities, enabling **spatial analytics and urban service distribution analysis**.

---

# 📌 Project Overview

Urban data is often scattered across web platforms and not readily available in structured formats for analysis. This project collects location-based service data from Google Maps and processes it through a complete **ETL pipeline**.

The pipeline performs:

* Automated data scraping
* Raw data staging
* Data cleaning and normalization
* Geographic enrichment using reverse geocoding APIs
* Data warehouse modeling

The final dataset enables analysis of **how urban services are distributed across Cairo districts**.

---

# 🏗️ System Architecture

The project follows a layered **Data Engineering architecture** that separates data extraction, processing, and analytics.

```
                 ┌────────────────────┐
                 │    Google Maps     │
                 │   (Data Source)    │
                 └─────────┬──────────┘
                           │
                           ▼
                ┌───────────────────┐
                │ Selenium Scrapers │
                │   Python Scripts  │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │   Raw CSV Files   │
                │   Data Sources/   │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │   Staging Layer   │
                │   staging_c_db    │
                │   stg_* tables    │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │  Cleaning Layer   │
                │  cleaning_c_db    │
                │  clean_* tables   │
                │ + API enrichment  │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │   Data Warehouse  │
                │      dw_c_db      │
                │ dim_urban_services│
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │   BI & Analytics  │
                │   Power BI / SQL  │
                └───────────────────┘
```

---

# 🗂️ Project Structure

```
Urban Services Intelligence/
│
├── Data Sources/                  # Raw CSVs output from scrapers
│   ├── clubs.csv
│   ├── gas_stations.csv
│   ├── hospitals.csv
│   ├── schools.csv
│   └── universities.csv
│
├── clubs_scraping.py
├── gas_stations_scraping.py
├── hospitals_scraping.py
├── moles_scraping.py
├── schools_scraping.py
├── university_scraping.py
│
├── staging.ipynb                  # Load CSVs → staging_c_db
├── cleaning.ipynb                 # Clean + enrich → cleaning_c_db
└── dw.ipynb                       # Load cleaned data → dw_c_db
```

---

# 🔄 ETL Pipeline

```
Google Maps
     │
     ▼
[Selenium Scrapers] ──► CSV files (Data Sources/)
     │
     ▼
[staging.ipynb] ──► staging_c_db
     │
     ▼
[cleaning.ipynb] ──► cleaning_c_db
     │
     ▼
[dw.ipynb] ──► dw_c_db
```

---

# 🔄 Data Flow

## 1️⃣ Data Collection

Automated Python scrapers collect service information from Google Maps.

Extracted attributes include:

* Service name
* Rating
* Reviews
* Address
* Phone number
* Website
* Image URL
* Plus Code location

The extracted data is exported to CSV files inside:

```
Data Sources/
```

---

## 2️⃣ Staging Layer

Raw CSV files are loaded into **SQL Server** staging tables.

Purpose of staging:

* Preserve raw scraped data
* Enable debugging
* Separate ingestion from transformation

Example staging tables:

```
stg_clubs
stg_gas_stations
stg_hospitals
stg_schools
stg_universities
```

---

## 3️⃣ Cleaning Layer

The cleaning stage transforms the raw data into a standardized structure.

### Data Standardization

Transformations include:

* Converting Arabic numbers to English numbers
* Normalizing ratings and review counts
* Cleaning phone numbers
* Extracting location codes

### Location Processing

Google Maps sometimes returns **Plus Codes instead of coordinates**.

Example:

```
5F8V+M2
```

The pipeline decodes these codes into **latitude and longitude** using the Open Location Code library.

---

# 🌍 Reverse Geocoding API Integration

## Why the API is Important

After decoding Plus Codes, we obtain geographic coordinates but still lack structured address information.

To enrich the dataset, the system performs **reverse geocoding**, converting coordinates into structured address components such as:

* Street
* District
* Region (City)
* Governorate
* Postal Code

This enrichment enables:

* Geographic analysis
* Map visualizations
* District-level filtering
* Urban service coverage studies

---

## API Used

The project uses the **Nominatim Reverse Geocoding API** from OpenStreetMap.

Example endpoint:

```
https://nominatim.openstreetmap.org/reverse
```

---

## API Mechanism

### 1. Send Coordinates

Latitude and longitude are sent to the API.

Example request:

```python
url = "https://nominatim.openstreetmap.org/reverse"

params = {
    "lat": lat,
    "lon": lon,
    "format": "json",
    "addressdetails": 1
}
```

---

### 2. API Response

The API returns structured address data in JSON format.

Example response:

```
{
  "address": {
    "road": "Tahrir Street",
    "suburb": "Dokki",
    "city": "Giza",
    "state": "Giza Governorate",
    "postcode": "12611"
  }
}
```

---

### 3. Extract Address Components

The pipeline maps API fields into dataset columns:

| API Field              | Dataset Column |
| ---------------------- | -------------- |
| road                   | street         |
| suburb / neighbourhood | district       |
| city                   | region         |
| state                  | governorate    |
| postcode               | postcode       |

These fields are then stored in the **cleaning database**.

---

### 4. Rate Limiting

To respect API usage limits, the system waits **1 second between requests**.

```python
time.sleep(1)
```

This prevents request throttling or temporary blocking.

---

# ⭐ Data Warehouse Design

The cleaned datasets are integrated into a **dimensional model** for analytics.

### Main Analytical Table

```
dim_urban_services
```

| Column       | Description           |
| ------------ | --------------------- |
| City         | City name             |
| Category     | Service type          |
| Sub Category | Detailed service type |
| English Name | Service name          |
| Arabic Name  | Arabic name           |
| Rating       | Google rating         |
| Reviews      | Number of reviews     |
| Street       | Street                |
| District     | District              |
| Region       | City                  |
| Governorate  | Governorate           |
| Latitude     | Latitude              |
| Longitude    | Longitude             |

---

## Why a Dimensional Model?

Using a dimensional design allows:

* Faster analytical queries
* Easy integration with Power BI
* Efficient aggregation
* Simplified dashboard building

The warehouse is designed to allow future expansion with additional dimensions such as:

* `dim_location`
* `dim_category`
* `fact_service_metrics`

---

# 📊 Example Analytics Enabled

The dataset can support questions such as:

* Which districts in Cairo have the **highest number of hospitals**?
* Which areas have **low access to services**?
* What services have the **highest user ratings**?
* How does service distribution vary across districts?

---

# 🎨 Dashboard Color Palette

| Category     | Color  |
| ------------ | ------ |
| Hospitals    | Coral  |
| Schools      | Blue   |
| Gas Stations | Teal   |
| Clubs        | Purple |
| Universities | Amber  |

These colors are used consistently in dashboards and maps.

---

# ⚙️ Setup & Requirements

## Python Dependencies

```
pip install selenium webdriver-manager pandas sqlalchemy pyodbc pyarrow fastparquet
```

---

## SQL Server Requirements

Create the following databases before running the notebooks:

```
staging_c_db
cleaning_c_db
dw_c_db
```

---

# ▶️ Run Order

1️⃣ Run scraping scripts
2️⃣ Run **staging.ipynb** → load CSVs into staging DB
3️⃣ Run **cleaning.ipynb** → clean and enrich data
4️⃣ Run **dw.ipynb** → load data into warehouse

---

# 🚀 Parallel Scraping

Scrapers can run simultaneously using Python threads.

Example:

```python
with ThreadPoolExecutor(max_workers=len(scripts)) as executor:
    executor.map(run_script, scripts)
```

Running multiple Chrome instances requires **at least 8GB RAM**.

---

# 🐛 Known Issues

* Google Maps HTML structure may change
* XPath selectors may require updates
* Some records may contain duplicated locations
* Postal code extraction may capture unrelated numbers

---

# 📄 License

MIT License — free to use and extend.

---

# 👤 Author

**Maged Magdy**
Data Engineering Project — Urban Services Intelligence
