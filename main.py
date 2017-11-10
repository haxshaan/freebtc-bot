import os
import pickle
import time
import socket
import requests

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

binary = FirefoxBinary(r"C:\Program Files\Mozilla Firefox\firefox.exe")
captcha_page = "https://freebitco.in/"
dump_location = "dumps/cookies/"


class HaxBitCoins(object):

    def __init__(self):
        self.driver = webdriver.Firefox(executable_path="drivers/geckodriver.exe", firefox_binary=binary)

    def is_element_exist(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    def wait_for_element(self, xpath, t):
        try:
            WebDriverWait(self.driver, t).until(EC.presence_of_element_located((By.XPATH, xpath)))
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
        except NoSuchElementException:
            print("No Captcha found")
            return False

        return True

    def wait_for_captcha(self):

        input("Press any Key to continue....")

    def load_url(self, url):
        self.driver.get(url)

    def login_homepage(self):

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

        # Go to roll tab

        if self.wait_for_element('/html/body/div[2]/div/nav/section/ul/li[2]/a', 3):
            self.driver.find_element_by_xpath('/html/body/div[2]/div/nav/section/ul/li[2]/a').click()
        else:
            print("Can't see earnBTC tab")

        # Wait for roll table

        if self.wait_for_element('//*[@id="free_play_payout_table"]', 10):

            # Check if Roll available:
            if self.wait_for_element('//*[@id="wait"]', 4):
                print("Roll countdown detected!")

            else:

                self.wait_for_captcha()
                try:
                    self.wait_for_element('//*[@id="free_play_form_button"]', 10)
                    self.driver.find_element_by_xpath('//*[@id="free_play_form_button"]').click()
                    print("Succesfully Rolled.")

                except NoSuchElementException or TimeoutException:
                    print("Roll Table Button not visible on page!")

                # See if modal popup appeared
                if self.wait_for_element('//*[@id="myModal22"]', 4):
                    self.driver.find_element_by_xpath('/html/body/div[11]/a').click()
                else:
                    pass

                if self.wait_for_element('//*[@id="free_play_digits"]', 5):
                    i = self.driver.find_element_by_xpath('//*[@id="free_play_first_digit"]').text
                    ii = self.driver.find_element_by_xpath('//*[@id="free_play_second_digit"]').text
                    iii = self.driver.find_element_by_xpath('//*[@id="free_play_third_digit"]').text
                    iv = self.driver.find_element_by_xpath('//*[@id="free_play_fourth_digit"]').text
                    v = self.driver.find_element_by_xpath('//*[@id="free_play_fifth_digit"]').text

                    print("\nYou Got: %r %r %r %r %r") % (i, ii, iii, iv, v)
                else:
                    print("Can't find reward!")
        else:
            print("Can't Find Roll table!!")

        self.driver.quit()

    def save_session(self, cookie_name):
        cookies = self.driver.get_cookies()
        pickle.dump(cookies, open(cookie_name, "wb"))

    def load_session(self, cookie_name):
        cookies = pickle.load(open(cookie_name, "rb"))

        for cookie in cookies:
            self.driver.add_cookie(cookie)


class AutomateMobile(object):
    def __init__(self):
        pass

    def check_internet(self):
        remote_server = "www.google.com"

        try:
            # Lets check if DNS could be resolved
            host = socket.gethostbyname(remote_server)
            s = socket.create_connection((host, 80), 2)
            s.getsockname()
            return True

        except:
            pass
        return False

    def tether_on(self):
        os.system('adb shell service call connectivity 33 i32 1')

    def tether_off(self):
        os.system('adb shell service call connectivity 33 i32 0')

    def get_ip(self):
        i = 5
        j = 20
        while j and not self.check_internet():
            if j == 1:
                try:
                    self.tether_off()
                    time.sleep(2)
                    self.tether_on()
                    time.sleep(4)
                    j = 20
                except:
                    print("Check USB connection!")
                    j = 20
                    pass

            else:
                print("Waiting for Mobile Data!")
                time.sleep(2)
                j -= 1
        else:
            while i:
                try:
                    if i % 2 == 0:
                        my_ip = requests.get('https://api.ipify.org/?format=json').json()['ip']
                        return my_ip + "\n"
                    else:
                        my_ip = requests.get('https://wtfismyip.com/text').text
                        return my_ip + "\n"

                except Exception as e:
                    print("Unable to get IP, trying again.. Error: ", e)
                    i -= 1
                    continue

    def data_on(self):
        os.system("adb shell svc data enable")

    def data_off(self):
        os.system("adb shell svc data disable")

    def turn_off_data(self):
        while True:
            try:
                print("Turning OFF Mobile Data, please wait..")
                self.data_off()
                time.sleep(1)

            except:
                print("Something went wrong, trying again..")
                continue
            else:
                print("Mobile Data turned OFF!\n")
                break

    def turn_on_data(self):
        while True:
            try:
                print("Now Turning Mobile Data ON, please wait..")

                self.data_on()

                time.sleep(1)

            except:
                print("Check connections! trying again..")
                continue

            else:
                print("Mobile Data turned ON!\n")
                break


mobile = AutomateMobile()


def change_ip():
    while True:
        try:
            mobile.turn_off_data()

            time.sleep(1)

            mobile.turn_on_data()

            time.sleep(3)

        except:
            print("Can't interact with Phone, check usb connection!")
            continue
        else:
            break


def check_pikle(new_ac_list):
    """
    :param new_ac_list: New dict object
    :return: A list containing new keys
    """
    account_time_dict = pickle.load(open("dumps/accounts_map.hk", "rb"))

    new_keys = []
    for x in new_ac_list:
        if x not in account_time_dict.keys():
            new_keys.append(x)
    return new_keys


def main():

    counter = 0

    if os.path.getsize("accounts.txt") == 0:
        print("Account file is empty!")
        raise SystemExit(0)

    try:
        acc_file = open("accounts.txt", "r")
    except:
        print("Accounts.txt file not found. Refer documentation!")
        raise SystemExit(0)

    ac_list = []

    for line in acc_file.readlines():
        acname = line.split('@')[0]
        ac_list.append(acname)

    if not os.path.isfile("dumps/accounts_map.hk"):
        print("No previous account dump detected creating fresh..")
        acc_time = {}

        for ac in ac_list:
            acc_time[ac] = '%f' % 0.00

        pickle.dump(acc_time, open("dumps/accounts_map.hk", 'wb'))
        accounts_time = acc_time

    else:
        print("Previous accounts dump found.")
        print("\nGetting new accounts from txt file...")
        old_dict = pickle.load(open("dumps/accounts_map.hk", "rb"))
        new_accounts = check_pikle(ac_list)
        if len(new_accounts):
            for item in new_accounts:
                old_dict.update({item: 0.00})

            pickle.dump(old_dict, open("dumps/accounts_map.hk", "wb"))
        else:
            print("No new account found.")
        accounts_time = old_dict

    HaxObject = HaxBitCoins()

    while True:
        t1 = time.time()

        for acc in accounts_time.keys():
            t2 = float(accounts_time[acc])
            time_left = t1 - t2
            if time_left > 60*60 or time_left == t1:

                time.sleep(4)

                HaxObject.load_url(captcha_page)

                if os.path.isfile(dump_location + acc + ".hax"):
                    HaxObject.load_session(dump_location + acc + ".hax")
                    HaxObject.load_url(captcha_page)
                    time.sleep(4)
                    HaxObject.roll_table()
                    HaxObject.save_session(dump_location + acc + ".hax")
                else:
                    HaxObject.login_homepage()
                    time.sleep(4)
                    HaxObject.save_session(dump_location + acc + ".hax")
                    HaxObject.roll_table()
                    HaxObject.save_session(dump_location + acc + ".hax")

                counter += 1
                continue

            else:
                print("Waiting for Next challenge!")
                time.sleep(10)
                print("Time left: %s") % (str(time_left))
                continue


if __name__ == '__main__':
    main()