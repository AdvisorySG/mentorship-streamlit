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

First set up [Poetry](https://python-poetry.org/docs/#installation), which is used to manage dependencies.

Then execute the following commands:
```bash
$ poetry shell # enter the virtualenv created by Poetry
$ poetry install --no-root # install dependencies using Poetry
$ streamlit run streamlit-app.py # access the dashboard by navigating to the provided URL in your web browser
```

Now set up [pre-commit hooks](https://pre-commit.com/):

```bash
$ pre-commit install
```
