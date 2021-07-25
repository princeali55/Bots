from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


def login(browser):  # this function opens the webpage instagram and logs you in
    browser.get('https://www.instagram.com/')
    time.sleep(5)
    username = browser.find_element_by_css_selector("[name='username']")
    # getting the css selector so the bot selects username field
    password = browser.find_element_by_css_selector("[name='password']")
    # getting the css selector so the bot selects password field
    login = browser.find_element_by_css_selector("button")
    username.send_keys("username")  # input username here
    password.send_keys("password")  # input password here
    login.click()

    time.sleep(5)


def visit_tag(browser, url):
    browser.get(url)
    time.sleep(5)

    pictures = browser.find_elements_by_css_selector("div[class='_9AhH0']")
    image_count = 0
    # finds a random tag and starts at the picture position 0 which is the first one

    for picture in pictures:
        # iterates through the pictures under the tag to like them

        if image_count >= 40:
            # breaks after 40 images
            break
        picture.click()
        time.sleep(5)
        heart = browser.find_element_by_css_selector("[aria-label='Like']")
        heart.click()

        close = browser.find_element_by_css_selector("[aria-label='Close']")
        close.click()

        image_count += 1
        time.sleep(3)


def main():
    browser = webdriver.Chrome()
    login(browser)
    # opens instagram

    # you can choose your personals profile link to visit it
    visit_tag(browser, "https://www.instagram.com/")


main()
