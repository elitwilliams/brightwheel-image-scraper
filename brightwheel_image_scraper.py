import logging
import os
import re
import time
import yaml
import argparse
import random
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def setup_logging():
    """Set up logging configuration."""
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler("scraper.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def load_config():
    """
    Load the configuration from the YAML file.

    Returns:
        dict: Configuration dictionary.

    Raises:
        SystemExit: If the config file is not found.
    """
    try:
        with open("config.yml", "r") as config_file:
            return yaml.safe_load(config_file)
    except FileNotFoundError:
        logger.error("No config file found. Please check the config file!")
        raise SystemExit


def get_random_wait_time(min_time=2, max_time=3):
    """
    Generate a random wait time.

    Args:
        min_time (int): Minimum wait time in seconds.
        max_time (int): Maximum wait time in seconds.

    Returns:
        float: Random wait time in seconds.
    """
    return random.uniform(min_time, max_time)


def sign_in(browser, username, password, signin_url):
    """
    Sign in to the Brightwheel website.

    Args:
        browser: Selenium WebDriver instance.
        username (str): User's username.
        password (str): User's password.
        signin_url (str): URL of the signin page.

    Returns:
        browser: Authenticated Selenium WebDriver instance.

    Raises:
        SystemExit: If authentication fails.
    """
    browser.get(signin_url)
    time.sleep(get_random_wait_time())

    username_field = browser.find_element(By.XPATH, '//input[@id="username"]')
    password_field = browser.find_element(By.ID, "password")

    username_field.send_keys(username)
    time.sleep(get_random_wait_time())
    password_field.send_keys(password)

    try:
        password_field.submit()
        WebDriverWait(browser, 45).until(EC.url_changes(signin_url))
    except:
        logger.error("Unable to authenticate. Please check your credentials.")
        raise SystemExit

    time.sleep(get_random_wait_time(3, 5))
    return browser


def find_student_profile(browser, kidlist_url, student_number=None):
    """
    Find and select a student profile.

    Args:
        browser: Selenium WebDriver instance.
        kidlist_url (str): URL of the student list page.
        student_number (int, optional): Index of the student to select.

    Returns:
        str: URL of the selected student's profile.

    Raises:
        SystemExit: If unable to find the profile page.
    """
    browser.get(kidlist_url)
    time.sleep(get_random_wait_time())

    try:
        students = browser.find_elements(By.XPATH, "//a[contains(@href, '/students/')]")
        logger.info("Found student list.")

        if not students:
            raise Exception("No student URLs found")

        if student_number is not None:
            profile_url = students[student_number - 1].get_property("href")
        else:
            logger.info("Select a student:")
            for i, student in enumerate(students, 1):
                logger.info(f"{i}. {student.text}")
            selection = int(input("Enter a number: ")) - 1
            profile_url = students[selection].get_property("href")

        return profile_url
    except Exception as e:
        logger.error(f"Unable to find profile page: {e}")
        raise SystemExit


def apply_filters(browser, start_date, end_date):
    """
    Apply date range and photo filters on the feed page.

    Args:
        browser: Selenium WebDriver instance.
        start_date (str): Start date for filtering.
        end_date (str): End date for filtering.
    """
    start_date_field = browser.find_element(By.NAME, "start_date")
    start_date_field.send_keys(start_date)

    end_date_field = browser.find_element(By.NAME, "end_date")
    end_date_field.send_keys(end_date)

    select = browser.find_element(By.ID, "select-input-2")
    select.send_keys("Photo")
    select.send_keys(Keys.ENTER)

    browser.find_element(By.XPATH, '//*[@id="main"]/div/div/div[2]/div/form/button').click()
    logger.info("Applied date range and photo filter.")


def scroll_and_load(browser):
    """
    Scroll the page and load more content until the end is reached.

    Args:
        browser: Selenium WebDriver instance.
    """
    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:
        try:
            load_more_button = WebDriverWait(browser, 7).until(
                EC.presence_of_element_located((By.XPATH, '//button[text()="Load more"]'))
            )
            load_more_button.click()
        except:
            logger.info("No more 'Load more' button found.")

        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            logger.info("Page fully loaded.")
            break

        last_height = new_height


def download_images(browser):
    """
    Download images from the loaded page.

    Args:
        browser: Selenium WebDriver instance.
    """
    if not os.path.exists("./pics/"):
        os.makedirs("./pics/")

    soup = BeautifulSoup(browser.page_source, "html.parser")
    activities = soup.find_all("div", attrs={"data-testid": re.compile("^activity-")})

    current_date = None
    counter = 1

    for activity in activities:
        day_label = activity.find_previous("div", class_="activity-card-module-dayLabel-f37cc2d548384577")
        if day_label:
            date_match = re.search(r"(\d{2}/\d{2}/\d{4})", day_label.text)
            if date_match:
                date_str = date_match.group(1)
                try:
                    new_date = datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")
                    if new_date != current_date:
                        current_date = new_date
                        counter = 1
                        logger.info(f"New date detected: {current_date}")
                except ValueError:
                    logger.error(f"Unable to parse date: {date_str}")
            else:
                logger.error(f"No valid date found in label: {day_label.text}")

        if not current_date:
            current_date = datetime.now().strftime("%Y-%m-%d")
            logger.warning("No valid date found, using current date")

        img = activity.find("img")
        if img and img.get("src"):
            image_url = img["src"]
            try:
                filename = f"{current_date}-{counter:04d}.jpg"
                request = requests.get(image_url)
                with open(os.path.join("./pics/", filename), "wb") as f:
                    f.write(request.content)
                logger.info(f"Downloaded {filename}")
                counter += 1
            except Exception as e:
                logger.error(f"Failed to save image: {str(e)}")

    logger.info("Finished downloading images")


def main():
    """Main function to run the Brightwheel scraper."""
    setup_logging()

    parser = argparse.ArgumentParser(description="Brightwheel Scraper")
    parser.add_argument("-n", "--student-number", type=int, help="Select a student by number, indexed starting at 1")
    args = parser.parse_args()

    config = load_config()

    try:
        username = config["bwuser"]
        password = config["bwpass"]
        signin_url = config["bwsignin"]
        kidlist_url = config["bwlist"]
        start_date = config["startdate"]
        end_date = config["enddate"]
    except KeyError as e:
        logger.error(f"Missing required value in config file: {e}")
        raise SystemExit

    browser = uc.Chrome()

    try:
        browser = sign_in(browser, username, password, signin_url)
        profile_url = find_student_profile(browser, kidlist_url, args.student_number)

        feed_url = profile_url.rsplit("/", 1)[0] + "/feed"
        browser.get(feed_url)
        time.sleep(3)

        apply_filters(browser, start_date, end_date)
        scroll_and_load(browser)
        download_images(browser)
    finally:
        browser.quit()


if __name__ == "__main__":
    main()
