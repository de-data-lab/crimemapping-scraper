import re
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil.relativedelta import relativedelta


# Selenium options 
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options=options)

# Go to the Wilmington Police Area: 522
driver.get("https://www.crimemapping.com/map/agency/522")

# Change the date range ----------------------------------------------------------------------------------------
## Click the "When" button
when_button = driver.find_element(By.XPATH, '//*[@id="filtersWhen"]')
when_button.click()

## Click the "Custom Time Range"
custom_time_link = driver.find_element(By.XPATH, '//*[@id="whenPanel"]/ul/li[9]/div/a')
custom_time_link.click()

## Get the current date
to_date_input = driver.find_element(By.XPATH, '//*[@id="dateTo"]')
to_date = datetime.strptime(to_date_input.get_attribute('value'), '%m/%d/%Y')
### NOTE: We can only query up to 1000 records. Probably scraping one month at a time would be reasonable

## Get the max date available on the website (6 months)
oldest_date = to_date - relativedelta(months=6)

## Set the target date for the current query
from_date_target = to_date - relativedelta(months=1)
from_date_input = driver.find_element(By.XPATH, '//*[@id="dateFrom"]')
from_date_input.clear()
from_date_input.send_keys(from_date_target.strftime('%m/%d/%Y'))
# driver.save_screenshot('test.png')

## Click "Apply"
apply_button = driver.find_element(By.XPATH, '//*[@id="customDate"]/a')
apply_button.click()

# Open the Report view ----------------------------------------------------------------------------------------
# Find the display report button: #displayReports
display_report = driver.find_element(By.ID, 'displayReports')
# Click the display report button
display_report.click()

# Wait for the report window to load
try:
    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="CrimeIncidents"]/div[2]/table/tbody/tr[1]/td[3]'))
    )
finally:
    pass

# Save screenshot for testing
# driver.save_screenshot('selenium.png')

def get_items_text():
    # Get the number of items
    items_str = driver.find_element(By.XPATH, '//*[@id="CrimeIncidents"]/div[3]/span')
    items_text = items_str.text
    return items_text

def get_total_items(items_text = get_items_text()):
    # Get the total number of items in the table 
    match_total = re.compile("[0-9]+(?=( items))")
    total_items = match_total.search(items_text).group(0)
    return int(total_items)

def get_max_rendered(items_text = get_items_text()):
    # Get the max number of items rendered in the table
    match_max_rendered = re.compile('[0-9]+(?=( of))')
    max_rendered = match_max_rendered.search(items_text).group(0)
    return int(max_rendered)

max_rendered = get_max_rendered(get_items_text())
total_items =  get_total_items(get_items_text())
print("max rendered: " + str(max_rendered) )
print("total items: " + str(total_items) )

# Paginated scraping begins 
current_page = 0

# Container pd data frame to collect results
output_df = pd.DataFrame()

# TODO: Repeat the set-date routine here

while(total_items > max_rendered):
    current_page = current_page + 1
    print("Processing page: " + str(current_page))
    # Get the rendered table
    # The table header and the main table are in two different elements
    # Get the main table 
    cur_table = driver.find_element(By.XPATH, '//*[@id="CrimeIncidents"]/div[2]')
    cur_table_HTML = cur_table.get_attribute('innerHTML')

    # Convert the HTML table to a pandas data frame
    df = pd.read_html(cur_table_HTML)[0]
    output_df = pd.concat([output_df, df])

    # Get the next button and click
    next_button = driver.find_element(By.XPATH, '//*[@id="CrimeIncidents"]/div[3]/a[3]')
    next_button.click()

    # Wait for the element to load
    try:
        element = WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "k-loading-image"))
        )
    except: 
        print("Error on page: " + current_page)
    finally:
        # Update the numbers
        items_text = get_items_text()
        max_rendered = get_max_rendered(items_text)
        total_items = get_total_items(items_text)
        # driver.save_screenshot('page-' + str(current_page) + '.png')
        print("max rendered: " + str(max_rendered) )
        print("total items: " + str(total_items) )
driver.quit()

# Save the output
output_df.to_csv("output.csv")

# TODO:
# - Add a header to the pd data frame  
# - Select the range of dates to max (6 months)