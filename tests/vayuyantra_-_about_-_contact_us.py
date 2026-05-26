import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = 'https://www.vayuyantra.com'
HOME_URL = BASE_URL + '/home'
SCREENSHOT_DIR = os.path.join(os.getcwd(), 'artifacts')


@pytest.fixture
def driver():
    options = ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1440,1000')
    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(30)
    yield browser
    browser.quit()


def save_failure_screenshot(browser, test_name):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    screenshot_path = os.path.join(SCREENSHOT_DIR, f'{test_name}.png')
    browser.save_screenshot(screenshot_path)
    return screenshot_path


def wait_for_document_ready(browser, timeout=20):
    WebDriverWait(browser, timeout).until(lambda d: d.execute_script('return document.readyState') == 'complete')


def test_navigate_from_home_to_about_then_contact(driver):
    wait = WebDriverWait(driver, 20)
    test_name = 'test_navigate_from_home_to_about_then_contact'
    try:
        driver.get(HOME_URL)
        wait.until(EC.url_contains('/home'))
        wait_for_document_ready(driver)
        assert 'VayuYantra' in driver.title, f'Expected title to contain VayuYantra, got {driver.title!r}'
        home_heading = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[self::h1 or self::h2 or self::h3][contains(normalize-space(.), 'Our Solutions')]")))
        assert 'Our Solutions' in home_heading.text, f'Expected home heading Our Solutions, got {home_heading.text!r}'

        about_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href$='/about']")))
        about_link.click()
        wait.until(EC.url_matches(r'.*/about/?$'))
        wait_for_document_ready(driver)
        assert 'VayuYantra' in driver.title, f'Expected title to contain VayuYantra after About navigation, got {driver.title!r}'
        about_heading = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[self::h1 or self::h2 or self::h3][contains(normalize-space(.), 'Shaping Tomorrow') and contains(normalize-space(.), 'Aerial') and contains(normalize-space(.), 'Terrestrial Systems')]")))
        about_text = ' '.join(about_heading.text.split())
        assert 'Shaping Tomorrow' in about_text, f'Expected About heading to contain Shaping Tomorrow, got {about_text!r}'
        assert 'Aerial' in about_text, f'Expected About heading to mention Aerial, got {about_text!r}'
        assert 'Terrestrial Systems' in about_text, f'Expected About heading to mention Terrestrial Systems, got {about_text!r}'

        contact_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href$='/contact']")))
        contact_link.click()
        wait.until(EC.url_matches(r'.*/contact/?$'))
        wait_for_document_ready(driver)
        assert 'VayuYantra' in driver.title, f'Expected title to contain VayuYantra after Contact navigation, got {driver.title!r}'
        contact_heading = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[self::h1 or self::h2 or self::h3][contains(normalize-space(.), 'How can we help you today?')]")))
        contact_text = ' '.join(contact_heading.text.split())
        assert 'How can we help you today?' in contact_text, f'Expected Contact heading How can we help you today?, got {contact_text!r}'
        assert driver.current_url.rstrip('/').endswith('/contact'), f'Expected final URL to end with /contact, got {driver.current_url!r}'
    except Exception:
        screenshot_path = save_failure_screenshot(driver, test_name)
        print(f'Failure screenshot saved to: {screenshot_path}')
        raise
