# coding: utf-8
"""Scraper for BetFastAction MLB player props using Selenium.

This script logs into the BetFastAction website, navigates to the MLB Player Props
section and downloads the available props table to a CSV file.

Requirements:
    - selenium
    - pandas
    - webdriver-manager

Note: Set the credentials in the environment variables ``BETFAST_USERNAME`` and
``BETFAST_PASSWORD``. The script also assumes the network running it has access
to the site.
"""
from __future__ import annotations

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_driver() -> webdriver.Chrome:
    """Set up ChromeDriver using webdriver-manager with sane defaults."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    return driver


def login(driver: webdriver.Chrome, username: str, password: str) -> None:
    """Log into BetFastAction."""
    driver.get("https://classic.betfastaction.ag/")

    # Wait for username field and login
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "ctl00_ctl00_uxMainContent_uxMainContent_uxLogin1_uxLoginForm_uxUsername"))
    )
    driver.find_element(By.ID, "ctl00_ctl00_uxMainContent_uxMainContent_uxLogin1_uxLoginForm_uxUsername").send_keys(username)
    driver.find_element(By.ID, "ctl00_ctl00_uxMainContent_uxMainContent_uxLogin1_uxLoginForm_uxPassword").send_keys(password)
    driver.find_element(By.ID, "ctl00_ctl00_uxMainContent_uxMainContent_uxLogin1_uxLoginForm_uxSubmit").click()


def navigate_to_player_props(driver: webdriver.Chrome) -> None:
    """Navigate through Sports -> Baseball - Props -> MLB - Player Props."""
    # Wait for Sports link
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Sports"))
    ).click()

    # Wait for Baseball - Props menu item
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Baseball - Props"))
    ).click()

    # Wait for MLB - Player Props checkbox
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//label[contains(., 'MLB - Player Props')]/preceding-sibling::input[@type='checkbox']"))
    ).click()

    # Click Continue
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Continue']"))
    ).click()

    # Wait until the props table header is loaded with expected text
    WebDriverWait(driver, 30).until(
        EC.text_to_be_present_in_element((By.XPATH, "//h3"), "MLB - Player Props")
    )


def scrape_props(driver: webdriver.Chrome) -> pd.DataFrame:
    """Scrape the props table into a pandas DataFrame."""
    rows = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, "//table//tr[contains(@class, 'game')]"))
    )

    data = []
    for row in rows:
        try:
            player = row.find_element(By.XPATH, ".//td[1]").text.strip()
            prop_type = row.find_element(By.XPATH, ".//td[2]").text.strip()
            date_time = row.find_element(By.XPATH, ".//td[3]").text.strip()
            game = row.find_element(By.XPATH, ".//td[4]").text.strip()
            over_odds = row.find_element(By.XPATH, ".//td[5]").text.strip()
            under_odds = row.find_element(By.XPATH, ".//td[6]").text.strip()
            data.append({
                "Player": player,
                "Prop Type": prop_type,
                "Date & Time": date_time,
                "Game": game,
                "Over Odds": over_odds,
                "Under Odds": under_odds,
            })
        except Exception:
            continue

    return pd.DataFrame(data)


def main() -> None:
    """Entry point for running the scraper."""
    username = os.environ.get("BETFAST_USERNAME")
    password = os.environ.get("BETFAST_PASSWORD")
    if not username or not password:
        raise EnvironmentError(
            "BETFAST_USERNAME and BETFAST_PASSWORD environment variables must be set"
        )

    driver = get_driver()
    try:
        login(driver, username, password)
        navigate_to_player_props(driver)
        df = scrape_props(driver)
        df.to_csv("mlb_player_props.csv", index=False)
        print("Saved", len(df), "rows to mlb_player_props.csv")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
