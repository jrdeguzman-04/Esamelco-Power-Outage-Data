#  ESAMELCO Power Outage Data Pipeline  

<img width="1469" height="769" alt="Screenshot 2026-04-07 at 10 31 53 PM" src="https://github.com/user-attachments/assets/99d049d5-fbbf-42bf-8072-531e928ec697" />

This project is an ETL (Extract, Transform, Load) data pipeline that processes and analyzes power outage data from ESAMELCO (Eastern Samar Electric Cooperative).  

The data comes from actual ESAMELCO Facebook posts, which were replicated in a dummy page for safe testing and development.  

The goal of this project is to clean messy data, organize it properly, and prepare it for analysis and dashboard visualization.  



## Project Overview  

This pipeline follows a Medallion Architecture (Bronze → Silver → Gold) to improve data quality step by step.  

- **Bronze:** Raw data from sources (Facebook posts, JSON files)  
- **Silver:** Cleaned and standardized data  
- **Gold:** Final validated data ready for dashboard and analysis  

This project shows my skills in **data engineering, data cleaning, and data pipeline design**.  


## Tech Stack  

Language: Python  
- Data Processing: Pandas, JSON  
- Data Source: Facebook Graph API  
- Web Scraping: BeautifulSoup, Requests  
- Database: PostgreSQL  
- Visualization: Streamlit   

---

## 📂 Project Structure  

```
.
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
├── .gitignore
│
├── data/
│   ├── bronze/        # Raw data
│   ├── silver/        # Cleaned data
│   ├── gold/          # Final data
│   └── reference/     # Barangay list
│
├── src/
│   ├── main.py        # Main pipeline
│   ├── dashboard.py   # Dashboard
│   ├── extract/       # Data extraction
│   ├── transform/     # Data cleaning & processing
│   └── load/          # Data loading
│
└── scripts/
```

---

## Data Pipeline Stages  

### 1. Bronze (Raw Data)  
- Stores raw and unprocessed data  
- Includes original Facebook posts and JSON files  

### 2. Silver (Cleaned Data)  
- Filters only relevant data (e.g., interruption posts)  
- Cleans and formats text  
- Standardizes barangay names and outage reasons  

### 3. Gold (Final Data)  
- Fully cleaned and validated data  
- Ready for dashboard and analysis  

---
## Streamlit Dashboard
<img width="1118" height="330" alt="Screenshot 2026-04-07 at 10 13 05 PM" src="https://github.com/user-attachments/assets/523f8045-7041-489c-962e-3ecadf4911c0" />
<img width="1028" height="452" alt="Screenshot 2026-04-07 at 10 13 24 PM" src="https://github.com/user-attachments/assets/8e8dd3cf-c473-44a6-bcea-4fc3971f188f" />
<img width="1067" height="430" alt="Screenshot 2026-04-07 at 10 13 32 PM" src="https://github.com/user-attachments/assets/8008ff15-0b5c-45f5-b70f-61275042cc47" />



##  How to Run  

### Local Setup  

1. Clone the repository  
```
git clone <repository-url>
cd Esamelco-Power-Outage-Data
```

2. Create virtual environment  
```
python -m venv .venv
source .venv/bin/activate
```
*(Windows: .venv\Scripts\activate)*  

3. Install dependencies  
```
pip install -r requirements.txt
```

4. Setup `.env` file  
(Add your environment variables here)  

---

###  Run the Pipeline  

Run full pipeline:  
```
python src/main.py
```

Run dashboard:  
```
python src/dashboard.py
```

---

### 🐳 Docker Setup (need to add)  

```
docker-compose up --build
```

---

##  Features  

- ETL pipeline (Extract, Transform, Load)  
- Medallion Architecture (Bronze → Silver → Gold)  
- Data cleaning and validation  
- Barangay and location matching  
- Standardized outage reasons  
- Simple dashboard for visualization  

---

##  Purpose  

This project was built to practice data pipeline development, handling messy and unstructured data, 
cleaning and transforming data, and preparing it for dashboard visualization.

---


**Last Updated:** April 2026  
