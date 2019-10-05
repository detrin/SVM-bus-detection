# -*- coding: utf-8 -*-

import time

# from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from xvfbwrapper import Xvfb
from bs4 import BeautifulSoup

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
opts = Options()
opts.add_argument("user-agent="+USER_AGENT)

URL = "https://www.ipcamlive.com/kfasevernikamera"

def load_page(browser, URL):
    browser.set_page_load_timeout(12)
    while True:
        try:
            browser.get(URL)
        except TimeoutException:
            print("Timeout, retrying...")
            continue
        else:
            break
    return 
       
def check_exists_by_xpath(xpath):
    try:
        browser.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

display = Xvfb()
display.start()
browser = webdriver.Chrome("/home/hermanda/bin/chromedriver")

# Go to the Google home page
load_page(browser, URL)
time.sleep(15)
# Access requests via the `requests` attribute
URL_STREAM = ""
for request in browser.requests:
    if request.response and "m3u8" in request.path:
        URL_STREAM = request.path

with open("url_stream.txt", "w") as f:
    f.write(URL_STREAM)

browser.close()
display.stop()