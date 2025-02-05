from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote_plus
import time

#Input Required Settings First
cookies=input("Do you want to clear cookies\nTry if another song is returned(y/n):")
song_name = input("Enter the song name\n>>> ")

# Path to WebDriver executable
driver_path = r"<Enter path of your webdriver>"
service = Service(driver_path)

# Set up Chrome options and enable performance logging
options = Options()
options.add_argument("--mute-audio")  # Mute audio to prevent playback sound
options.add_argument("--disable-extensions")  # Disable extensions
options.add_argument("--disable-gpu")  # Disable GPU for headless performance
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument("--enable-logging")
options.add_argument("--v=1")

# Enable performance logging
capabilities = webdriver.DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # Enable performance logs

# Initialize WebDriver
driver = webdriver.Chrome(service=service, options=options, desired_capabilities=capabilities)

# Clear cookies function
if cookies == "y":
    driver.delete_all_cookies()  # Clear all cookies
    print("Cookies cleared.")

# Encode the query and construct the Google search URL
query = f"{song_name} site:jiosaavn.com"
encoded_query = quote_plus(query)
google_search_url = f"https://www.google.com/search?q={encoded_query}"

# Open the Google search URL directly
driver.get(google_search_url)
print(f"Searching for: {query}")

# Wait for search results to load
WebDriverWait(driver, 30).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h3.LC20lb.MBeuO.DKV0Md"))
)
print("Search results loaded.")

# Extract JioSaavn results from the search page
results = driver.find_elements(By.CSS_SELECTOR, "h3.LC20lb.MBeuO.DKV0Md")
jiosaavn_links = []

for result in results:
    title = result.text  # Extract the result title
    parent_anchor = result.find_element(By.XPATH, "./ancestor::a")  # Find the parent anchor tag
    link = parent_anchor.get_attribute("href")  # Get the link
    if "jiosaavn.com" in link:
        jiosaavn_links.append((title, link))

# Show the first 5 results to the user
if jiosaavn_links:
    print("\nTop 5 JioSaavn results:")
    for i, (title, url) in enumerate(jiosaavn_links[:5]):
        print(f"{i + 1}. {title} - {url}")

    # Let the user select a song
    while True:
        selected_index = int(input("\nSelect a song by number (1-5): ")) - 1
        if 0 <= selected_index < len(jiosaavn_links):
            selected_song_url = jiosaavn_links[selected_index][1]
            print(f"Opening song: {selected_song_url}")
            driver.get(selected_song_url)
            break
        else:
            print("Please select a number between 1 and 5.")
else:
    print("No JioSaavn results found.")
    driver.quit()
    exit()

# Wait for play button and click it
play_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.c-btn.c-btn--primary[data-btn-icon='q']"))
)
for _ in range(2):  # Click the play button twice
    play_button.click()
    time.sleep(1)
print("Successfully clicked the play button.")

# Extract audio URL from network logs
audio_url = None
start_time = time.time()
while time.time() - start_time < 30:  # Wait for up to 30 seconds
    logs = driver.get_log("performance")
    for entry in logs:
        message = entry["message"]
        if "audio" in message:
            if ".mp4" in message or ".aac" in message:
                start_index = message.find("https://")
                end_index = message.find(".mp4") + 4 if ".mp4" in message else message.find(".aac") + 4
                audio_url = message[start_index:end_index]
                break
    if audio_url:
        print(f"Audio URL found: {audio_url}")
        break
    else:
        time.sleep(1)

if not audio_url:
    print("Audio URL not found")

driver.quit()
