import os, sys, pickle, time

from random import uniform

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

binary = FirefoxBinary(r"C:\Program Files\Mozilla Firefox\firefox.exe")
captcha_page = "https://freebitco.in/"


class HaxBitCoins(object):

    def __init__(self):
        self.driver = webdriver.Firefox(executable_path="drivers/geckodriver.exe", firefox_binary=binary)

    def is_element_exist(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    def wait_for_element(self, xpath, time):
        try:
            WebDriverWait(self.driver, time).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except NoSuchElementException or TimeoutException:
            return False
        return True

    def is_captcha(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, 'iframe')))

        except NoSuchElementException or TimeoutException:
            print('No captcha frame found at this page!')
            return False

        self.driver.switch_to.default_content()
        iframe = self.driver.find_element_by_tag_name('iframe')
        print(iframe)
        self.driver.switch_to.frame(iframe)
        try:
            self.driver.find_element_by_xpath('/html/body/div[2]/div[3]/div[1]/div/div/span/div[5]')
            print("Captcha found!")
        except:
            print("No Captcha found")
            return False
        return True

    def wait_for_captcha(self):

        input("Press any Key to continue....")


    def load_url(self, url):
        self.driver.get(url)

    def login_homepage(self):
        # Get url
        self.load_url(captcha_page)

        # Wait for Login Script to appear then click
        if self.wait_for_element('/html/body/div[2]/div/nav/section/ul/li[10]/a', 10):
            loginbtn = self.driver.find_element_by_xpath('/html/body/div[2]/div/nav/section/ul/li[10]/a')
            self.driver.execute_script("arguments[0].click();", loginbtn)
        else:
            print("Can't find the Login button")

        # Wait for Login form to appear then submit
        if self.wait_for_element('//*[@id="login_form"]', 10):
            self.driver.find_element_by_xpath('//*[@id="login_form_btc_address"]').send_keys("shaanhax@gmail.com")
            self.driver.find_element_by_xpath('//*[@id="login_form_password"]').send_keys('s99887766')
            self.driver.find_element_by_xpath('//*[@id="login_button"]').click()
            time.sleep(2)

    def roll_table(self):
        # Wait for roll table
        if self.wait_for_element('//*[@id="free_play_payout_table"]', 10):
            self.wait_for_captcha()
            try:
                self.wait_for_element('//*[@id="free_play_form_button"]', 10)
                self.driver.find_element_by_xpath('roll buton').click()
                print("Succesfully Rolled.")
                if self.wait_for_element('//*[@id="free_play_digits"]', 5):
                    i = self.driver.find_element_by_xpath('//*[@id="free_play_first_digit"]').text
                    ii = self.driver.find_element_by_xpath('//*[@id="free_play_second_digit"]').text
                    iii = self.driver.find_element_by_xpath('//*[@id="free_play_third_digit"]').text
                    iv = self.driver.find_element_by_xpath('//*[@id="free_play_fourth_digit"]').text
                    v = self.driver.find_element_by_xpath('//*[@id="free_play_fifth_digit"]').text

                    print("\nYou Got: %s %s %s %s %s") %(i, ii, iii, iv, v)
                else:
                    print("Can't find reward!")
            except:
                print("Roll Table Button not visible on page!")



    def save_session(self):

        cookies = self.driver.get_cookies()
        pickle.dump(cookies, open("shaanhax.pkl", "wb"))

    def load_session(self):

        cookies = pickle.load(open("shaanhax.pkl", "rb"))

        for cookie in cookies:
            self.driver.add_cookie(cookie)


def main():

    HaxObject = HaxBitCoins()

    HaxObject.load_url(captcha_page)
    time.sleep(5)
    HaxObject.load_session()
    HaxObject.load_url(captcha_page)
    HaxObject.roll_table()


if __name__ == '__main__':
    main()
