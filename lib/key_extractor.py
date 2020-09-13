from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium_firefox import Firefox, By

RIOT_URL = 'https://developer.riotgames.com/'
# <div class="recaptcha-checkbox-border" role="presentation"></div>
current_working_dir = str(Path.cwd())
browser = Firefox(current_working_dir, current_working_dir, full_screen=False)
browser.get(RIOT_URL)
print(browser.find(By.CLASS_NAME, "recaptcha-checkbox-border"))
print('Please sign in and then press enter')
input()
print('enter pressed')

browser.get(RIOT_URL)
browser.save_cookies()