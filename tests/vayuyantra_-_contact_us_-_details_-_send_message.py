import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


@pytest.fixture(scope="function")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(0)
    yield drv
    drv.quit()


def _save_screenshot(drv, name):
    try:
        os.makedirs("screenshots", exist_ok=True)
        path = os.path.join("screenshots", f"{name}_{int(time.time())}.png")
        drv.save_screenshot(path)
        print(f"Screenshot saved to: {path}")
    except Exception as e:
        print(f"Failed to save screenshot: {e}")


def test_contact_us_form_submission_partial_fields(driver):
    wait = WebDriverWait(driver, 20)
    try:
        # Step 1: Navigate to the home page
        driver.get("https://www.vayuyantra.com/home")
        wait.until(EC.url_contains("/home"))
        assert "vayuyantra.com" in driver.current_url.lower()
        assert "VayuYantra" in driver.title

        # Step 2: Click CONTACT US link
        contact_link = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/contact' and contains(normalize-space(.), 'CONTACT US')]"))
        )
        contact_link.click()

        # Verify navigation to contact page
        wait.until(EC.url_contains("/contact"))
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(.), 'How can we help you today?')]")))
        assert "/contact" in driver.current_url

        # Step 3: Click & fill First Name
        first_name = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='First Name *']"))
        )
        first_name.click()
        first_name.clear()
        first_name.send_keys("agam")
        assert first_name.get_attribute("value") == "agam"

        # Step 4: Click & fill Last Name
        last_name = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Last Name']"))
        )
        last_name.click()
        last_name.clear()
        last_name.send_keys("Singh")
        assert last_name.get_attribute("value") == "Singh"

        # Step 5: Click Send Message
        send_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(.)='Send Message']"))
        )
        send_btn.click()

        # Step 6: Assert post-submission state
        # Either remained on /contact (validation) or shows a flash/confirmation message
        WebDriverWait(driver, 10).until(lambda d: "/contact" in d.current_url or "thank" in d.page_source.lower())
        assert "/contact" in driver.current_url or "thank" in driver.page_source.lower()

    except (TimeoutException, AssertionError, WebDriverException) as e:
        _save_screenshot(driver, "contact_us_form_submission_failure")
        raise
