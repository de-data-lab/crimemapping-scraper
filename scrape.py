import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil.relativedelta import relativedelta
# Local modules
from utils.PageMetadata import PageMetadata
from utils.change_daterange import change_daterange


# Selenium options 
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options=options)

# Go to the Wilmington Police Area: 522
driver.get("https://www.crimemapping.com/map/agency/522")

# Change the date range ----------------------------------------------------------------------------------------
initial_dates = change_daterange(driver)

## Get the oldest date available on the website (6 months)
oldest_date = initial_dates.get('to_date') - relativedelta(months=6)
latest_date = initial_dates.get('to_date')

# Open the Report view ----------------------------------------------------------------------------------------
# Find and click the display report button
display_report = driver.find_element(By.ID, 'displayReports')
display_report.click()

# Wait for the report window to load
try:
    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="CrimeIncidents"]/div[2]/table/tbody/tr[1]/td[3]'))
    )
finally:
    pass

# Get current page's metadata
cur_page_metadata = PageMetadata(driver)
cur_page_metadata.update_metadata()
print("max rendered: " + str(cur_page_metadata.max_rendered) )
print("total items: " + str(cur_page_metadata.total_items) )

# Container pd data frame to collect results
output_df = pd.DataFrame()

# TODO: Repeat the set-date routine here

# Paginated scraping begins 
current_page = 0

while(cur_page_metadata.total_items > cur_page_metadata.max_rendered):
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

    # Update the metadata
    cur_page_metadata.update_metadata()

    # driver.save_screenshot('page-' + str(current_page) + '.png')
    print("max rendered: " + str(cur_page_metadata.max_rendered) )
    print("total items: " + str(cur_page_metadata.total_items) )

# Close the report view (Back to Map)
back_to_map_element = driver.find_element(By.XPATH, '//*[@id="reportContainer"]/a[3]')
back_to_map_element.click()

# TODO: Change the date and loop through

driver.quit()

# Save the output
output_df.to_csv("output.csv")

# TODO: Add a header to the pd data frame  