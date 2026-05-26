import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.getenv('BASE_URL', 'https://www.vayuyantra.com')
TIMEOUT = int(os.getenv('SELENIUM_TIMEOUT', '20'))


@pytest.fixture
def driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(30)
    yield browser
    browser.quit()


def save_failure_screenshot(driver, test_name):
    os.makedirs('screenshots', exist_ok=True)
    timestamp = time.strftime('%Y%m%d-%H%M%S')
    path = os.path.join('screenshots', f'{test_name}_{timestamp}.png')
    driver.save_screenshot(path)
    print(f'Failure screenshot saved to: {path}')


def wait_for_document_ready(driver, wait):
    wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')


def type_text(wait, locator, value):
    element = wait.until(EC.element_to_be_clickable(locator))
    element.clear()
    element.send_keys(value)
    return element


def get_invalid_control_labels(driver):
    script = "return Array.from(document.querySelectorAll('input, textarea, select')).filter(function(e){return e.willValidate && !e.checkValidity();}).map(function(e){return e.getAttribute('placeholder') || e.getAttribute('aria-label') || e.getAttribute('name') || e.id || e.tagName;});"
    return driver.execute_script(script)


def test_contact_form_requires_mandatory_fields(driver):
    test_name = 'test_contact_form_requires_mandatory_fields'
    wait = WebDriverWait(driver, TIMEOUT)

    contact_link = (By.CSS_SELECTOR, 'a[href="/contact"], a[href$="/contact"]')
    home_heading = (By.XPATH, '//*[self::h1 or self::h2 or self::h3][contains(normalize-space(.), "Our Solutions")]')
    contact_heading = (By.XPATH, '//*[self::h1 or self::h2 or self::h3][contains(normalize-space(.), "How can we help you today?")]')
    first_name_input = (By.CSS_SELECTOR, 'input[placeholder="First Name *"]')
    last_name_input = (By.CSS_SELECTOR, 'input[placeholder="Last Name"]')
    send_message_button = (By.XPATH, '//button[normalize-space()="Send Message"]')

    try:
        driver.get(f'{BASE_URL}/home')
        wait_for_document_ready(driver, wait)
        wait.until(EC.title_contains('VayuYantra'))
        wait.until(EC.visibility_of_element_located(home_heading))
        assert '/home' in driver.current_url, f'Expected home URL, got {driver.current_url}'

        wait.until(EC.element_to_be_clickable(contact_link)).click()
        wait.until(EC.url_contains('/contact'))
        wait_for_document_ready(driver, wait)
        wait.until(EC.title_contains('VayuYantra'))
        wait.until(EC.visibility_of_element_located(contact_heading))
        assert driver.current_url.rstrip('/').endswith('/contact'), f'Expected contact page URL, got {driver.current_url}'

        first_name = type_text(wait, first_name_input, 'test')
        assert first_name.get_attribute('value') == 'test', 'First Name value was not retained after typing.'

        last_name = type_text(wait, last_name_input, 'test')
        assert last_name.get_attribute('value') == 'test', 'Last Name value was not retained after typing.'

        wait.until(EC.element_to_be_clickable(send_message_button)).click()

        wait.until(lambda d: '/contact' in d.current_url)
        wait.until(EC.visibility_of_element_located(contact_heading))

        invalid_controls = wait.until(lambda d: get_invalid_control_labels(d))
        body_text = wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'body'))).text.lower()
        app_validation_present = any(token in body_text for token in ['required', 'mandatory', 'please enter', 'valid email', 'email is required'])
        success_present = any(token in body_text for token in ['thank you', 'thanks for contacting', 'message sent', 'successfully submitted'])

        assert invalid_controls or app_validation_present, 'Submitting an incomplete contact form should expose required-field validation.'
        assert not success_present, 'Incomplete contact form appeared to submit successfully.'
        assert driver.current_url.rstrip('/').endswith('/contact'), f'Incomplete submission should remain on contact page, got {driver.current_url}'
        assert wait.until(EC.visibility_of_element_located(first_name_input)).get_attribute('value') == 'test'
        assert wait.until(EC.visibility_of_element_located(last_name_input)).get_attribute('value') == 'test'

    except Exception:
        save_failure_screenshot(driver, test_name)
        raise
