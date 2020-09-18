import time
from datetime import datetime
from pathlib import Path
from random import uniform

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium_firefox import Firefox, By, WebDriverWait, EC
from youtube_uploader_selenium import Constant
import numpy as np
import scipy.interpolate as si

# Randomization Related
MIN_RAND = 0.64
MAX_RAND = 1.27
LONG_MIN_RAND = 4.78
LONG_MAX_RAND = 11.1
RIOT_URL = 'https://developer.riotgames.com/'


class ApiKeyExtractor:
    number = None
    headless = False
    options = None
    profile = None
    capabilities = None

    def login(self):
        self.browser.get(RIOT_URL)
        self.wait_between(MIN_RAND, MAX_RAND)

        if self.browser.has_cookies_for_current_website():
            self.browser.load_cookies()
            self.wait_between(MIN_RAND, MAX_RAND)
            self.browser.refresh()
        else:
            print('Please sign in and then press enter')
            input()
            print('enter pressed')

            self.browser.get(RIOT_URL)
            self.wait_between(MIN_RAND, MAX_RAND)
            self.browser.save_cookies()

    def retrieve_api_key(self):
        self.browser.get(RIOT_URL)
        self.wait_between(MIN_RAND, MAX_RAND)

        self.do_captcha(self.browser.driver)

        self.wait_between(MIN_RAND, MAX_RAND)
        self.browser.driver.switch_to.default_content()
        self.wait_between(MIN_RAND, MAX_RAND)

        reset_api_button = self.browser.find(By.TAG_NAME, "confirm_action")
        reset_api_button.click()

        self.wait_between(MIN_RAND, MAX_RAND)

        api_key_container = self.browser.find(By.ID, "apikey")
        api_key_container.click()

        self.wait_between(MIN_RAND, MAX_RAND)

        api_key_container.send_keys(Keys.CONTROL + 'a')
        self.wait_between(MIN_RAND, MAX_RAND)

        api_key_container.send_keys(Keys.CONTROL + 'c')
        self.wait_between(MIN_RAND, MAX_RAND)

        import win32clipboard

        # get clipboard data
        win32clipboard.OpenClipboard()
        api_key = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        print(api_key)

        self.browser.driver.quit()

    def get_api_key(self):
        try:
            self.login()
            self.retrieve_api_key()
        except Exception as e:
            print(e)
            self.browser.driver.quit()
            raise

    def __init__(self):
        current_working_dir = str(Path.cwd())
        self.browser = Firefox(current_working_dir, current_working_dir, full_screen=True)
        self.browser.driver.profile._install_extension("buster_captcha_solver_for_humans-0.7.2-an+fx.xpi", unpack=False)
        self.browser.driver.profile.set_preference("security.fileuri.strict_origin_policy", False)
        self.browser.driver.profile.update_preferences()

    # Simple logging method
    def log(self, t=None):
        now = datetime.now()
        if t == None:
            t = "Main"
        print("%s :: %s -> %s " % (str(now), t, self))

    # Use time.sleep for waiting and uniform for randomizing
    def wait_between(self, a, b):
        rand = uniform(a, b)
        time.sleep(rand)

    # Using B-spline for simulate humane like mouse movments
    def human_like_mouse_move(self, action, start_element):
        points = [[6, 2], [3, 2], [0, 0], [0, 2]]
        points = np.array(points)
        x = points[:, 0]
        y = points[:, 1]

        t = range(len(points))
        ipl_t = np.linspace(0.0, len(points) - 1, 100)

        x_tup = si.splrep(t, x, k=1)
        y_tup = si.splrep(t, y, k=1)

        x_list = list(x_tup)
        xl = x.tolist()
        x_list[1] = xl + [0.0, 0.0, 0.0, 0.0]

        y_list = list(y_tup)
        yl = y.tolist()
        y_list[1] = yl + [0.0, 0.0, 0.0, 0.0]

        x_i = si.splev(ipl_t, x_list)
        y_i = si.splev(ipl_t, y_list)

        startElement = start_element

        action.move_to_element(startElement)
        action.perform()

        c = 5  # change it for more move
        i = 0
        for mouse_x, mouse_y in zip(x_i, y_i):
            action.move_by_offset(mouse_x, mouse_y)
            action.perform()
            self.log("Move mouse to, %s ,%s" % (mouse_x, mouse_y))
            i += 1
            if i == c:
                break

    def do_captcha(self, driver):

        driver.switch_to.default_content()
        self.log("Switch to new frame")
        iframes = driver.find_elements_by_tag_name("iframe")
        driver.switch_to.frame(iframes[0])

        self.log("Wait for recaptcha-anchor")
        check_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "recaptcha-checkbox-border")))

        self.log("Wait")
        self.wait_between(MIN_RAND, MAX_RAND)

        action = ActionChains(driver)
        self.human_like_mouse_move(action, check_box)

        self.log("Click")
        check_box.click()

        self.log("Wait")
        self.wait_between(MIN_RAND, MAX_RAND)

        self.log("Mouse movements")
        action = ActionChains(driver)
        self.human_like_mouse_move(action, check_box)

        self.log("Switch Frame")
        driver.switch_to.default_content()
        iframes = driver.find_elements_by_tag_name("iframe")
        for i in iframes:
            print(i)
            print(i.get_attribute('title'))
        frame = iframes[-1]
        driver.switch_to.frame(frame)

        self.log("Wait")
        self.wait_between(LONG_MIN_RAND, LONG_MAX_RAND)

        self.log("Find solver button")
        capt_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "solver-button"))
        )

        self.log("Wait")
        self.wait_between(LONG_MIN_RAND, LONG_MAX_RAND)

        self.log("Click")
        capt_btn.click()

        self.log("Wait")
        self.wait_between(LONG_MIN_RAND, LONG_MAX_RAND)

        try:
            self.log("Alert exists")
            alert_handler = WebDriverWait(driver, 20).until(
                EC.alert_is_present()
            )
            alert = driver.switch_to.alert
            self.log("Wait before accept alert")
            self.wait_between(MIN_RAND, MAX_RAND)

            alert.accept()

            self.wait_between(MIN_RAND, MAX_RAND)
            self.log("Alert accepted, retry captcha solver")

            self.do_captcha(driver)
        except:
            self.log("No alert")

        self.log("Wait")
        driver.implicitly_wait(5)
        self.log("Switch")
        iframes = driver.find_elements_by_tag_name("iframe")
        for frame in iframes:
            print(frame)
        # driver.switch_to.frame(iframes[0])


api = ApiKeyExtractor()
api.get_api_key()
