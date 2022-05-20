from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.by import By


def get_current_date(driver):
    ## Get the current date
    to_date_input = driver.find_element(By.XPATH, '//*[@id="dateTo"]')
    to_date = datetime.strptime(to_date_input.get_attribute('value'), '%m/%d/%Y')
    ### NOTE: We can only query up to 1000 records. Probably scraping one month at a time would be reasonable
    return to_date

def set_from_date(driver, from_date):
    from_date_input = driver.find_element(By.XPATH, '//*[@id="dateFrom"]')
    from_date_input.clear()
    from_date_input.send_keys(from_date.strftime('%m/%d/%Y'))


def change_daterange(driver, by=1, from_date=None, to_date=None):
    # Change the date range ----------------------------------------------------------------------------------------
    ## Click the "When" button
    when_button = driver.find_element(By.XPATH, '//*[@id="filtersWhen"]')
    when_button.click()

    ## Click the "Custom Time Range"
    custom_time_link = driver.find_element(By.XPATH, '//*[@id="whenPanel"]/ul/li[9]/div/a')
    custom_time_link.click()

    if not to_date: to_date = get_current_date(driver)

    if not from_date:
        from_date_target = to_date - relativedelta(months=by)
        set_from_date(driver, from_date_target)

    ## Click "Apply"
    apply_button = driver.find_element(By.XPATH, '//*[@id="customDate"]/a')
    apply_button.click()

    return {'to_date': to_date, 'from_date': from_date_target}