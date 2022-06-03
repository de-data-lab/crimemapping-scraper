from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_current_date(driver):
    ## Get the current date
    to_date_input = driver.find_element(By.XPATH, '//*[@id="dateTo"]')
    to_date = datetime.strptime(to_date_input.get_attribute('value'), '%m/%d/%Y')
    ### NOTE: We can only query up to 1000 records. Probably scraping one month at a time would be reasonable
    return to_date

def set_from_date(driver, from_date):
    from_date_field_xpath = '//*[@id="dateFrom"]'
    try: 
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, from_date_field_xpath))
        )
    except Exception as e:
        driver.save_screenshot('screenshots/test.png')
        print(e)

    from_date_input = driver.find_element(By.XPATH, from_date_field_xpath)
    from_date_input.clear()
    from_date_input.send_keys(from_date.strftime('%m/%d/%Y'))

def set_to_date(driver, to_date):
    to_date_input = driver.find_element(By.XPATH, '//*[@id="dateTo"]')
    to_date_input.clear()
    to_date_input.send_keys(to_date.strftime('%m/%d/%Y'))

def get_initial_dates(driver):
    ## Click the "When" button
    when_button = driver.find_element(By.XPATH, '//*[@id="filtersWhen"]')
    when_button.click()

    custom_time_link = driver.find_element(By.XPATH, '//*[@id="whenPanel"]/ul/li[9]/div/a')
    custom_time_link.click()
    
    to_date = get_current_date(driver)
    from_date = to_date - relativedelta(months=1)

    ## Find and click the close link
    close_link = driver.find_element(By.XPATH, '//*[@id="mapPanels"]/ul/li/a')
    close_link.click()

    # Wait for the sidebar to close
    driver.implicitly_wait(3)

    return {'to_date': to_date, 'from_date': from_date}


def change_daterange(driver, by_months=1, from_date=None, to_date=None):

    driver.save_screenshot("screenshots/start_change_daterange.png")
    
    # Elements to look for
    apply_button_xpath = '//*[@id="customDate"]/a'
    custom_time_range_xpath = '//*[@id="whenPanel"]/ul/li[9]/div'

    # html_element = driver.find_element(By.TAG_NAME, "html")
    # html_classes = html_element.get_attribute("class")
    # print(html_classes)

    # Change the date range ----------------------------------------------------------------------------------------
    ## Click the "When" button
    when_button = driver.find_element(By.XPATH, '//*[@id="filtersWhen"]')
    when_button.click()

    ## Wait for the Apply button to appear
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, apply_button_xpath)))

    ## Wait for the "Custom Time Range" text to be clickable
    try:
        WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, custom_time_range_xpath))
        )
    except Exception as e:
        print("Error occurred when trying to find the 'Custom Time Range Text'")
        driver.save_screenshot('screenshots/log.png')

    driver.save_screenshot("screenshots/when_button_clicked.png")

    # Check the custom time link to be clickable
    try: 
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, custom_time_range_xpath))
        )
    except Exception as e:
        print("Error occurred when trying to find the custom time range div.")
        driver.save_screenshot('screenshots/log.png')
    # Click the custom time link
    custom_time_link = driver.find_element(By.XPATH, custom_time_range_xpath)
    custom_time_link.click()

    if not to_date: 
        to_date = get_current_date(driver)

    if not from_date:
        from_date = to_date - relativedelta(months=by_months)
    
    # Check the from field to be clickable
    try: 
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="dateFrom"]'))
        )
    except Exception as e:
        print("Error occurred when trying to find the from field for the date range.")
        driver.save_screenshot('screenshots/log.png')
    
    # Set the target date
    set_from_date(driver, from_date)

    # Set the to_date 
    set_to_date(driver, to_date)

    ## Click "Apply"
    apply_button = driver.find_element(By.XPATH, apply_button_xpath)
    apply_button.click()

    ## Find and click the close link
    close_link = driver.find_element(By.XPATH, '//*[@id="mapPanels"]/ul/li/a')
    close_link.click()

    return {'to_date': to_date, 'from_date': from_date}