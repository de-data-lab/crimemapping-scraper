import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dateutil.relativedelta import relativedelta
# Local modules
from utils.PageMetadata import PageMetadata
from utils.change_daterange import change_daterange, get_initial_dates


# Selenium options 
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options=options)

# Set the intervals of scraping
scraping_interval = relativedelta(weeks=1)

# Save screenshots for debugging
save_screenshots = False

# Go to the Wilmington Police Area: 522
driver.get("https://www.crimemapping.com/map/agency/522")

# Change the date range ----------------------------------------------------------------------------------------
initial_dates = get_initial_dates(driver)

## Get the oldest date available on the website (6 months)
oldest_date = initial_dates.get('to_date') - relativedelta(months=6)
latest_date = initial_dates.get('to_date')
from_date = oldest_date
to_date = oldest_date + scraping_interval

# Container pd data frame to collect results
output_df = pd.DataFrame()

while (latest_date >= to_date):
    # Get a string for the current daterange 
    current_daterange = from_date.strftime("%Y-%m-%d") + " - " + to_date.strftime("%Y-%m-%d")

    # Print to console
    print('=================')
    print('Date Range: ' + current_daterange)

    # Change the date range ----------------------------------------------------------------------------------------
    cur_dates = change_daterange(driver, from_date=from_date, to_date=to_date)

    # If debug, save screenshot
    if save_screenshots: driver.save_screenshot("screenshots/" + current_daterange + ".png")

    # Open the Report view ----------------------------------------------------------------------------------------
    # Find and click the display report button
    display_report = driver.find_element(By.ID, 'displayReports')
    display_report.click()

    # Wait for the report window to load. Wait for the loading image to be invisible
    try:
        WebDriverWait(driver, 20).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, '#CrimeIncidents > div.k-grid-content > div > div.k-loading-image'))
            )
    except Exception as e:
        driver.save_screenshot("screenshots/" + "log.png")
        print("Error happened. Check log.png for screenshot.")
        print(e)
        break

    # Paginated scraping begins for this report
    current_page = 0

    # Set the parameter to continue to the next page
    continue_next_page = True

    while(continue_next_page):
        current_page = current_page + 1
        print("Processing page: " + str(current_page))

        # Get screenshot for debugging
        if save_screenshots: driver.save_screenshot("screenshots/" + current_daterange + " - " + 'page-' + str(current_page) + '.png')

        # Get current page's metadata
        cur_page_metadata = PageMetadata(driver)
        cur_page_metadata.update_metadata()
        print("Processing items: " + str(cur_page_metadata.min_rendered) + " - " + str(cur_page_metadata.max_rendered))
        print("Total items in this report: " + str(cur_page_metadata.total_items) )

        # Get the rendered table
        # The table header and the main table are in two different elements
        # Get the main table 
        cur_table = driver.find_element(By.XPATH, '//*[@id="CrimeIncidents"]/div[2]')
        cur_table_HTML = cur_table.get_attribute('innerHTML')

        # Convert the HTML table to a pandas data frame
        df = pd.read_html(cur_table_HTML)[0]
        # Set column names
        df.columns = ['map_it', 'type_icon', 'description', 'incident_number', 'location', 'agency', 'date']
        # Only select columns of interest, and sort
        df = df[['date', 'agency', 'location', 'description']]
        # Add to the output dataframe
        output_df = pd.concat([output_df, df])

        # Get the next button and click
        next_button = driver.find_element(By.XPATH, '//*[@id="CrimeIncidents"]/div[3]/a[3]')
        next_button.click()

        # Wait for the element to load
        try:
            element = WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "k-loading-image"))
            )
        except Exception as e: 
            print("Error on page: " + str(current_page))
            print(e)

        # Evaluate if we already got all the items in this report
        continue_next_page = not(cur_page_metadata.total_items == cur_page_metadata.max_rendered)

    # Close the report view (Back to Map)
    back_to_map_element = driver.find_element(By.XPATH, '//*[@id="reportContainer"]/a[3]')
    back_to_map_element.click()

    # Update to the next target dates
    from_date = from_date + scraping_interval
    to_date = to_date + scraping_interval

    # Save the output
    output_df.to_csv("output.csv")


driver.quit()


# TODO: Add a header to the pd data frame  