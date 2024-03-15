# Streamlit Dashboard

This branch contains the Streamlit dashboard for real-time insights into both mentorship application data and traffic analysis on the mentorship website.

### Project Structure
The main script is `streamlit-app.py` which contains the demo dashboard as well as page configurations. The `pages` directory contains the scripts for the two pages of the dashboard: `application.py` and `traffic.py`.
```
├── streamlit-app.py    <-- main script
└── pages
    ├── application.py # insights into mentorship application data
    └── traffic.py # traffic analysis on the mentorship website
```

### Getting Started
```bash
pip install -r requirements.txt
streamlit run streamlit-app.py
# Access the dashboard by navigating to the provided URL in your web browser.
```