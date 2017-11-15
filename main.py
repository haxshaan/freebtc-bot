import os
import pickle
import time
import socket
import requests
from PIL import Image
from io import BytesIO, StringIO
import base64


from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.action_chains import ActionChains

from captcha2upload import CaptchaUpload

binary = FirefoxBinary(r"C:\Program Files\Mozilla Firefox\firefox.exe")
captcha_page = "https://freebitco.in/"
dump_location = "dumps/cookies/"


def timeit(method):
    def wrapper(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r (%r, %r) %2.2f sec' % \
              (method.__name__, args, kw, te-ts))
        return result

    return wrapper()

class HaxBitCoins(object):

    def __init__(self):
        profile = FirefoxProfile()
        profile.set_preference("browser.download.dir", r"C:\Users\Home\PycharmProjects\freebitcoin\dumps\captcha")
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser,helperapps.neverAsk.SaveToDisk", "image/png")
        self.driver = webdriver.Firefox(executable_path="drivers/geckodriver.exe", firefox_binary=binary,
                                        firefox_profile=profile)
        self.TWOCAPTCHA_API_KEY = "fbce4d59de16ac4995cbcb6f65f18a37"
        self.captcha = CaptchaUpload(self.TWOCAPTCHA_API_KEY, log=True)

    def is_element_exist(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    def wait_for_element(self, xpath, t):
        try:
            WebDriverWait(self.driver, t).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except:
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

    def get_captcha2(self):
        path = "dumps/captcha/captcha.png"

        element = self.driver.find_element_by_css_selector('.captchasnet_captcha_content > img:nth-child(1)')

        location = element.location_once_scrolled_into_view
        size = element.size

        print(location, size)

        ss = self.driver.get_screenshot_as_base64()
        b64_img = base64.b64decode(ss)

        image = Image.open(BytesIO(b64_img))

        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']

        print(left, top, right, bottom)

        image = image.crop((left, top, right, bottom))
        image.save(path, 'png')

    def get_captcha_image(self):

        """
        Old Method of capturing Captcha screenshot
        :return: None
        """

        path = "dumps/captcha/captcha.png"

        # save ss
        ss = self.driver.get_screenshot_as_base64()
        b64_image = base64.b64decode(ss)
        # Open image into memory using PIL
        image = Image.open(BytesIO(b64_image))

        left = 531
        top = 420
        right = 771
        bottom = 503

        image = image.crop((left, top, right, bottom))  # defines crop
        image.save(path, "png")

    def load_url(self, url):
        self.driver.get(url)

    def login_homepage(self, user, passw):

        # Wait for Login Script to appear then click
        if self.wait_for_element('/html/body/div[2]/div/nav/section/ul/li[10]/a', 20):
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
            print("Login form not found in the page")

    def is_element_clickable(self, xpath, time1):
        try:
            WebDriverWait(self.driver, time1).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
        except:
            return False
        return True

    def enter_captcha(self):
        cap = input("Enter the captcha value: ")
        try:
            self.driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[5]/div[4]/div/div/div/div/div/input[2]').send_keys(str(cap))
        except:
            return False
        return True

    def wait_by_css(self, css_selector, time1):
        try:
            WebDriverWait(self.driver, time1).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        except:
            return False
        return True

    def roll_table(self):
        try:
            print("Current Balance: ", self.driver.find_element_by_xpath('//*[@id="balance"]').text)
        except:
            pass

        # Go to roll tab

        roll_tab = '/html/body/div[2]/div/nav/section/ul/li[2]/a'

        captcha_path = 'dumps/captcha/captcha.png'

        try:
            if self.wait_for_element(roll_tab, 3):
                self.driver.execute_script("arguments[0].click;", roll_tab)
        except:
            pass

        # Wait for roll table

        if self.wait_for_element('//*[@id="free_play_payout_table"]', 5):
            roll_btn = '//*[@id="free_play_form_button"]'

            # Check if Roll available:

            i = 1
            while self.is_element_clickable(roll_btn, 4):
                print("test, i is: ", i)

                if i == 1:
                    #self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                    # To close TnC bar
                    """
                    try:
                        j = 4
                        while not self.is_element_clickable('/html/body/div[1]/div/a[1]', 1) and j:
                            j -= 1
                            continue
                        else:
                            self.driver.find_element_by_xpath('/html/body/div[1]/div/a[1]').click()
                    except:
                        pass
                    """

                    print("Trying to get the Captcha input box\n")

                    if self.wait_by_css('.captchasnet_captcha_input_box', 10):
                        print("Getting captcha src attribute and saving image")
                        self.get_captcha2()
                        if os.path.isfile(captcha_path):
                            input("Continue?")
                            print("Getting captcha answer..")
                            ti = time.time()
                            value = self.captcha.solve(captcha_path)
                            print("Captcha answer is: ", str(value))
                            tf = time.time()
                            print("Time took by 2captcha: %2.2f" % (tf - ti))
                            try:
                                self.driver.find_element_by_css_selector('.captchasnet_captcha_input_box').send_keys(value)
                            except:
                                print("Can't input value into box, Enter it manually..")
                                if self.enter_captcha():
                                    i += 1
                                else:
                                    self.wait_for_captcha()

                            self.driver.find_element_by_xpath(roll_btn).click()
                            i += 1
                            print("Your account balance is: ", self.captcha.getbalance())
                        else:
                            print("Can't find captcha image")
                            if self.enter_captcha():
                                i += 1
                            else:
                                self.wait_for_captcha()
                            self.driver.find_element_by_xpath(roll_btn).click()
                            i += 1

                    else:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        print("Can't find captcha input box,\nPlease input value in the browser and Press enter here!")
                        print("Getting captcha src attribute and saving image")
                        self.get_captcha_image()
                        if os.path.isfile(captcha_path):
                            input("Continue?")
                            print("Getting captcha answer..")
                            ti = time.time()
                            value = self.captcha.solve(captcha_path)
                            print("Captcha answer is: ", str(value))
                            tf = time.time()
                            print("Time took by 2captcha: %2.2f" % (tf - ti))
                        else:
                            print("Can't find captcha image")
                        self.wait_for_captcha()
                        self.driver.find_element_by_xpath(roll_btn).click()
                        i += 1

                else:
                    print("Wrong Captcha, try again..")

                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                    print("Trying to get the Captcha input box\n")
                    if self.wait_by_css('.captchasnet_captcha_input_box', 10):
                        print("Getting New captcha src attribute and saving image")
                        self.get_captcha_image()
                        if os.path.isfile(captcha_path):
                            input("Continue?")
                            print("Getting captcha answer..")
                            ti = time.time()
                            value = self.captcha.solve(captcha_path)
                            print("Captcha answer is: ", str(value))
                            tf = time.time()
                            print("Time took by 2captcha: %2.2f" % (tf - ti))
                            try:
                                self.driver.find_element_by_css_selector('.captchasnet_captcha_input_box').send_keys(
                                    value)
                            except:
                                print("Can't input value into box, Enter it manually..")
                                if self.enter_captcha():
                                    i += 1
                                else:
                                    self.wait_for_captcha()

                            self.driver.find_element_by_xpath(roll_btn).click()
                            i += 1
                            print("Your account balance is: ", self.captcha.getbalance())
                        else:
                            print("Can't find captcha image")

                    else:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        print("Can't find captcha input box,\nPlease input value in the browser and Press enter here!")
                        try:
                            action = ActionChains(self.driver)
                            box = self.driver.find_element_by_css_selector('.captchasnet_captcha_input_box')
                            action.move_to_element(box).perform()
                        except:
                            pass
                        print("Getting captcha src attribute and saving image")
                        self.get_captcha_image()
                        if os.path.isfile(captcha_path):
                            input("Continue?")
                            print("Getting captcha answer..")
                            ti = time.time()
                            value = self.captcha.solve(captcha_path)
                            print("Captcha answer is: ", str(value))
                            tf = time.time()
                            print("Time took by 2captcha: %2.2f" % (tf - ti))
                        else:
                            print("Can't find captcha image")
                        self.wait_for_captcha()
                        self.driver.find_element_by_xpath(roll_btn).click()
                        i += 1

            try:
                if self.wait_for_element('//*[@id="free_play_digits"]', 2):
                    i = self.driver.find_element_by_xpath('//*[@id="free_play_first_digit"]').text
                    ii = self.driver.find_element_by_xpath('//*[@id="free_play_second_digit"]').text
                    iii = self.driver.find_element_by_xpath('//*[@id="free_play_third_digit"]').text
                    iv = self.driver.find_element_by_xpath('//*[@id="free_play_fourth_digit"]').text
                    v = self.driver.find_element_by_xpath('//*[@id="free_play_fifth_digit"]').text

                    print("\nYou Got: {0} {1} {2} {3} {4}".format(i, ii, iii, iv, v))
                    os.remove(captcha_path)
                else:
                    print("Can't find reward!")
            except:
                pass
        else:
            print("Something went wrong! Can't Find Roll table!!")

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
    connection_name = ''
    with open('config.txt', 'r') as f:
        for line in f.readlines():
            if 'Dial-up' in line:
                connection_name += line.split(':')[1].strip(' ')
                print(connection_name)

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

            print("\nCurrent account: ", acc)

            t1 = time.time()
            t2 = accounts_time.get(acc)
            time_been = t1 - float(t2)
            if time_been > float(60*60) or time_been == t1:

                print("Your current IP Address is: %s" % get_ip())

                HaxObject = HaxBitCoins()

                print("Opening url.")
                try:
                    HaxObject.load_url(captcha_page)
                except:
                    print("Can't open url")

                if os.path.isfile(dump_location + acc + ".hax"):
                    print(acc)
                    print("Cookie file found for the account: " + acc + ".hax")
                    try:
                        HaxObject.load_session(dump_location + acc + ".hax")
                        print("Previous session restored successfully")
                        print("\nRefreshing page")
                        HaxObject.load_url(captcha_page)
                    except:
                        print("Can't restore previous cookie, trying to login..")
                        HaxObject.load_url(captcha_page)
                        with open('accounts.txt', 'r') as f:
                            for line in f:
                                if acc in line:
                                    user = line.split(':')[0].strip()
                                    password = line.split(':')[1].strip()

                        HaxObject.login_homepage(user, password)
                        time.sleep(4)

                    HaxObject.roll_table()
                    HaxObject.save_session(dump_location + acc + ".hax")
                    HaxObject.quit_fox()
                else:
                    with open('accounts.txt', 'r') as f:
                        for line in f:
                            if acc in line:
                                user = line.split(':')[0].strip()
                                password = line.split(':')[1].strip()

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

                print("Accounts left:")

                print("Changing your IP before Next Roll")
                change_ip()
                print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")

            else:
                print("Time left: %.2f minutes" % ((3600 - time_been) / 60))
                print("Waiting for Next challenge!")


if __name__ == '__main__':
    main()