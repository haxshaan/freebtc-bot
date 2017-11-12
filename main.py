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
        while True:
            if check_internet():
                self.driver.get(url)
                break
            else:
                continue

    def login_homepage(self, user, passw):

        # Wait for Login Script to appear then click
        if self.wait_for_element('/html/body/div[2]/div/nav/section/ul/li[10]/a', 10):
            loginbtn = self.driver.find_element_by_xpath('/html/body/div[2]/div/nav/section/ul/li[10]/a')
            self.driver.execute_script("arguments[0].click();", loginbtn)
        else:
            print("Can't find the Login button")

        # Wait for Login form to appear then submit
        if self.wait_for_element('//*[@id="login_form"]', 10):
            print("Login form found.")
            try:
                username = self.driver.find_element_by_xpath('//*[@id="login_form_btc_address"]')
                password = self.driver.find_element_by_xpath('//*[@id="login_form_password"]')
                self.driver.execute_script('arguments[0].value = arguments[1]', username, user)
                self.driver.execute_script('arguments[0].value = arguments[1]', password, passw)
                self.driver.find_element_by_xpath('//*[@id="login_button"]').click()
                time.sleep(2)
            except:
                print("Can't login")
                raise SystemExit(0)
            else:
                print("Can't find email field!")
        else:
            print("Login form not found in the page")

    def is_element_clickable(self, xpath, time1):
        try:
            WebDriverWait(self.driver, time1).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
        except:
            return False
        return True

    def roll_table(self):

        print("Current Balance: ", self.driver.find_element_by_xpath('//*[@id="balance"]').text)

        # Go to roll tab

        roll_tab = '/html/body/div[2]/div/nav/section/ul/li[2]/a'
        if self.wait_for_element(roll_tab, 15):
            self.driver.execute_script("arguments[0].click;", roll_tab)
        else:
            print("Can't see FreeBTC tab")

        # Wait for roll table

        if self.wait_for_element('//*[@id="free_play_payout_table"]', 7):
            roll_btn = '//*[@id="free_play_form_button"]'
            self.driver.execute_script('arguments[0].scrollIntoView;', roll_btn)

            # Check if Roll available:

            i = 1
            while self.is_element_clickable(roll_btn, 6):

                if i == 1:
                    self.wait_for_captcha()
                    self.driver.find_element_by_xpath(roll_btn).click()
                    time.sleep(2)
                    i += 1
                else:
                    print("Wrong Captcha, try again..")
                    self.wait_for_captcha()
                    self.driver.find_element_by_xpath(roll_btn).click()
                    time.sleep(2)
                    i += 1

            else:
                pass

            # See if modal popup appeared
            if self.wait_for_element('//*[@id="myModal22"]', 4):
                model_btn = self.driver.find_element_by_xpath('/html/body/div[11]/a')
                self.driver.find_element_by_xpath(model_btn).click()
            else:
                pass
            try:

                if self.wait_for_element('//*[@id="free_play_digits"]', 5):
                    time.sleep(1.5)
                    i = self.driver.find_element_by_xpath('//*[@id="free_play_first_digit"]').text
                    ii = self.driver.find_element_by_xpath('//*[@id="free_play_second_digit"]').text
                    iii = self.driver.find_element_by_xpath('//*[@id="free_play_third_digit"]').text
                    iv = self.driver.find_element_by_xpath('//*[@id="free_play_fourth_digit"]').text
                    v = self.driver.find_element_by_xpath('//*[@id="free_play_fifth_digit"]').text

                    print("\nYou Got: {0} {1} {2} {3} {4}".format (i, ii, iii, iv, v))
                else:
                    print("Can't find reward!")
            except:
                pass

        else:
            print("Can't Find Roll table!!")

    def quit_fox(self):
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

    def tether_on(self):
        os.system('adb shell service call connectivity 33 i32 1')

    def tether_off(self):
        os.system('adb shell service call connectivity 33 i32 0')

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


def check_internet():
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


def get_ip():
    i = 5
    j = 20
    while j and not check_internet():
        print("Waiting for Mobile Data!")
        time.sleep(2)
        j -= 1
    else:
        while i:
            try:
                if i % 2 == 0:
                    my_ip = requests.get('https://api.ipify.org/?format=json').json()['ip']
                    return my_ip
                else:
                    my_ip = requests.get('https://wtfismyip.com/text').text
                    return my_ip

            except Exception as e:
                print("Unable to get IP, trying again.. Error: ", e)
                i -= 1
                continue

while True:
    try:
        ip_method = int(input("Select your Internet Connection method.\n1. Dongle, 2. USB TETHERING\n>"))
    except ValueError:
        print("Enter only integers, try again..")
    if ip_method == 1 or ip_method == 2:
        break
    else:
        print("Enter valid response!")
        continue


def modem_off(connection):
    os.system("rasdial " + connection + " /disconnect")


def modem_on(connection):
    os.system("rasdial " + connection)

if ip_method == 1:

    connection_name = str(input("Enter the name of your Dial-up Connection: "))

    if not check_internet():
        modem_on(connection_name)

    def change_ip():
        while True:
            try:
                modem_off(connection_name)
                time.sleep(1)
                modem_on(connection_name)
                time.sleep(3)

            except:
                print("Can't reach modem, check connection.")
                continue
            else:
                break

else:
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
        username = line.split('@')[0]
        ac_list.append(username)
        acc_file.close()

    if not os.path.isfile("dumps/accounts_map.hk"):
        print("No previous account dump detected creating fresh..")
        acc_time = {}

        for ac in ac_list:
            acc_time[ac] = 0.00

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
            print("Added new accounts to dump database")
        else:
            print("No new account found.")
        accounts_time = old_dict

    while True:

        for acc in accounts_time.keys():

            print("Current account: ", acc)

            print("Your current IP Address is: %s" % get_ip())

            t1 = time.time()
            t2 = accounts_time.get(acc)
            time_been = t1 - float(t2)
            if time_been > float(60*60) or time_been == t1:

                HaxObject = HaxBitCoins()

                print("Opening url.")
                try:
                    HaxObject.load_url(captcha_page)
                except:
                    print("Can't open url")

                if os.path.isfile(dump_location + acc + ".hax"):
                    print(acc)
                    print("Cookie file found for the account: " + acc + ".hax")
                    HaxObject.load_session(dump_location + acc + ".hax")
                    print("Previous session restored successfully")
                    print("\nRefreshing page")
                    HaxObject.load_url(captcha_page)
                    time.sleep(4)
                    print("")

                    while HaxObject.is_element_clickable('/html/body/div[3]/div/div[1]/div[5]/div[4]/div/div/div/div/div/div[2]/p[3]', 6)\
                            or HaxObject.is_captcha():
                        HaxObject.roll_table()
                        time.sleep(4)
                    HaxObject.save_session(dump_location + acc + ".hax")
                    HaxObject.quit_fox()
                else:
                    print(acc)
                    with open('accounts.txt', 'r') as f:
                        for line in f:
                            if acc in line:
                                user = line.split(':')[0].strip()
                                password = line.split(':')[1].strip()

                    print(user, password)
                    print("No previous cookie found for this account, trying to log in.")
                    HaxObject.login_homepage(user, password)
                    time.sleep(4)
                    HaxObject.roll_table()
                    print("Saving session to a cookie file.")
                    HaxObject.save_session(dump_location + acc + ".hax")
                    HaxObject.quit_fox()

                counter += 1
                accounts_time[acc] = time.time()
                pickle.dump(accounts_time, open("dumps/accounts_map.hk", "wb"))

                print("Changing your IP before Next Roll")
                change_ip()
                time.sleep(4)

            else:
                print("Waiting for Next challenge!")
                time.sleep(2)
                print("Time left: %.2f minutes" % ((3600 - time_been) / 60))


if __name__ == '__main__':
    main()