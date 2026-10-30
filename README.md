# ⚡ ElectWatch

**Intelligent Electricity Consumption Monitoring and Analytics**

ElectWatch is a Python-based electricity consumption analytics project that processes household power consumption data and presents meaningful insights through an interactive dashboard.

## Features

- Household electricity consumption analysis
- Data loading and preprocessing
- Daily, hourly, and monthly consumption visualizations
- Consumption statistics and insights
- Interactive dashboard using Streamlit
- Automated tests for core modules

## Tech Stack

- **Language:** Python
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly
- **Dashboard:** Streamlit
- **Testing:** Pytest

## Project Structure

```text
ElectWatch/
├── backend/
├── data/
├── database/
├── frontend/
│   └── app.py
├── ml/
├── notebooks/
├── src/
│   ├── data_loader.py
│   ├── data_cleaner.py
│   ├── consumption.py
│   └── visualizations.py
├── test_cleaner.py
├── test_consumption.py
├── test_insights.py
├── test_loader.py
├── test_visualizations.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/MinalMaurya/ElectWatch.git
cd ElectWatch
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the dataset

ElectWatch uses the **Individual Household Electric Power Consumption** dataset from the UCI Machine Learning Repository.

Download the dataset and place `household_power_consumption.txt` inside the `data/` directory.

The raw dataset is excluded from Git because of its large file size.

### 5. Run the application

```bash
streamlit run frontend/app.py
```

Open the local URL provided by Streamlit in your browser.

## Running Tests

```bash
pytest
```

## Future Scope

- Machine learning-based anomaly detection
- Electricity consumption forecasting
- FastAPI backend integration
- Database integration
- Docker containerization
- Kubernetes deployment
- Live or simulated electricity monitoring

## Author

**Minal Maurya**

GitHub: [MinalMaurya](https://github.com/MinalMaurya)

---

*ElectWatch — Making electricity consumption easier to understand through data and analytics.*
