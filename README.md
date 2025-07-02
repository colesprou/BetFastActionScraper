# BetFastAction Scraper

This repository contains a Python script to scrape MLB player prop odds from **classic.betfastaction.ag**.

## Usage

Install dependencies:
```bash
pip install selenium pandas webdriver-manager
```

Set your credentials as environment variables and run the scraper:
```bash
export BETFAST_USERNAME="your_username"
export BETFAST_PASSWORD="your_password"
python scrape_betfastaction.py
```

The script logs in using these environment variables, navigates to the MLB Player Props section and outputs a CSV file named `mlb_player_props.csv` containing the scraped data.
