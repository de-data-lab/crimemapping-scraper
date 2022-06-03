import re
from selenium.webdriver.common.by import By

def get_items_text(driver):
    # Get the number of items
    items_str = driver.find_element(By.XPATH, '//*[@id="CrimeIncidents"]/div[3]/span')
    items_text = items_str.text
    return items_text

def get_total_items(items_text):
    # Get the total number of items in the table 
    match_total = re.compile("[0-9]+(?=( items))")
    total_items = match_total.search(items_text).group(0)
    return int(total_items)

def get_max_rendered(items_text):
    # Get the max number of items rendered in the table
    match_max_rendered = re.compile('[0-9]+(?=( of))')
    max_rendered = match_max_rendered.search(items_text).group(0)
    return int(max_rendered)

def get_min_rendered(items_text):
    # Get the index of the table
    match_min_rendered = re.compile('[0-9]+(?=( - ))')
    min_rendered = match_min_rendered.search(items_text).group(0)
    return int(min_rendered)


class PageMetadata:
    def __init__(self, driver):
        self.driver = driver
    def update_metadata(self):
        self.items_text = get_items_text(self.driver)
        self.max_rendered = get_max_rendered(self.items_text)
        self.min_rendered = get_min_rendered(self.min_rendered)
        self.total_items = get_total_items(self.items_text)
