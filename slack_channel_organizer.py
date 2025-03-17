import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def login_to_slack(driver, workspace_url):
    driver.get(workspace_url)
    print("Please log into your Slack workspace in the opened browser window.")
    input("Press Enter AFTER you're fully logged in and Slack UI is loaded...")

def create_section(driver, section_name):
    actions = ActionChains(driver)
    try:
        # Click "Channels" header
        channels_header = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-qa='section_heading_button__channels']"))
        )
        channels_header.click()
        time.sleep(1)

        # Hover "Create" menu item via JavaScript to reliably open submenu
        create_menu_item = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'c-menu_item__label') and text()='Create']"))
        )
        driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));", create_menu_item)
        time.sleep(1)

        # Click "Create section"
        create_section_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'c-submenu__container')]//button[.//div[text()='Create section']]"))
        )
        create_section_button.click()
        time.sleep(1)

        # Enter section name
        input_box = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[data-qa='channel_selection_modal_input_text_input']"))
        )
        input_box.clear()
        input_box.send_keys(section_name)

        # Click "Create" confirmation button
        create_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-qa='channel_selection_modal_input_go']"))
        )
        create_btn.click()
        time.sleep(2)

        # Explicitly collapse the newly created section immediately
        accordion_arrow = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((
                By.XPATH,
                f"//div[text()='{section_name}']/ancestor::div[contains(@class,'p-channel_sidebar__section_heading')]//i[@data-qa='channel-section-collapse']"
            ))
        )
        accordion_arrow.click()
        print(f"✅ Section '{section_name}' created and collapsed.")

    except TimeoutException:
        raise Exception("❌ Timeout occurred during section creation or collapsing.")

def move_channels_to_section(driver, search_string, section_name):
    actions = ActionChains(driver)

    try:
        # Step 1: Reliably locate TARGET SECTION (previously confirmed working)
        target_section = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, f"//div[@class='overflow_ellipsis' and text()='{section_name}']"))
        )
        print("✅ Target section found.")

        # Step 2: Grab ALL sidebar channels (assuming baseline channels are unique enough)
        all_channels = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((
                By.CSS_SELECTOR, "div.p-channel_sidebar__channel"
            ))
        )

        # Filter channels clearly by search_string
        matching_channels = [ch for ch in all_channels if search_string in ch.text]

        if not matching_channels:
            print("❌ No matching channels found.")
            return

        print(f"✅ Found {len(matching_channels)} matching channels.")

        # Step 3: Drag each matching channel directly to the target section
        for channel in matching_channels:
            print(f"⚡ Moving channel: {channel.text}")
            actions.click_and_hold(channel).pause(1).move_to_element(target_section).pause(1).release().perform()
            time.sleep(1)

        print("✅ Successfully moved all matching channels.")

    except TimeoutException:
        raise Exception("❌ Timeout: Verify selectors and Slack UI state.")
    except Exception as e:
        raise Exception(f"❌ An unexpected error occurred: {e}")

def main():
    workspace_url = "https://guardian-audits.slack.com"
    section_name = input("Enter the section name to create: ").strip()
    search_string = input("Enter the channel name substring to move: ").strip()

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    try:
        login_to_slack(driver, workspace_url)
        create_section(driver, section_name)
        move_channels_to_section(driver, search_string, section_name)
        print("✅ Done organizing channels.")

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

    finally:
        input("Press Enter to close the browser...")
        driver.quit()

if __name__ == "__main__":
    main()