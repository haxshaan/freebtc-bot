import os
import pickle
import time
import socket
import requests
from PIL import Image
from io import BytesIO
import base64
import logging
import subprocess

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

from haxCaptcha.HaxCaptcha import CaptchaUpload

__author__ = "Shantam Mathuria"
__copyright__ = "Copyright 2017"
__credits__ = ["Shantam Mathuria"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Shantam Mathuria"
__email__ = "shantam.m22@gmail.com"
__status__ = "Production"

captcha_page = "https://freebitco.in/"
dump_location = "dumps/cookies/"

print("""
        *=*=*=*=* Welcome to HaxBTC Bot =*=*=*=*=*
        #                                        #
        #      Please read documentation         #
        #    Press CTRL + C to exit anytime      #
        #  Contact me at: shantam.m22@gmail.com  #
        #                                        #
        *=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=
    """)

print("Logging: Enable")

connection_name = ''
with open('config.txt', 'r') as f:
    print("\nReading data from config file:")
    for line in f.readlines():
        if 'Dial-up' in line:
            connection_name += line.split(':')[1].strip()
            print("$ Dial-up - ", connection_name)
        elif 'Firefox' in line:
            bin_loc = line.split(':', 1)[1].strip()
            print("$ Firefox path - ", bin_loc)
        elif 'Chrome' in line:
            chrome_bin = line.split(':', 1)[1].strip()
            print("$ Chrome path: ", chrome_bin)
        elif '2captcha' in line:
            api_2 = line.split(':')[1].strip()
            if len(api_2.strip()):
                print("$ 2Captcha API Key - ", api_2)
            else:
                print("Can't find 2captcha api key from config.")
                time.sleep(10)
                raise SystemExit(0)

print("\nSelect your default browser:")
while True:
    try:
        browser_choice = int(input("1)Firefox  2)Chrome\n>  "))
    except ValueError:
        print("Please enter only integers, try again.")
        continue
    if browser_choice not in [1, 2]:
        print("No such choice available, try again.")
        continue
    else:
        break

# Keep log of errors
logging.basicConfig(level=logging.INFO)
haxlog = logging.getLogger(__name__)


def timeit(method):
    def wrapper(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r (%r, %r) %2.2f sec' % (
            method.__name__, args, kw, te - ts))
        return result

    return wrapper()


class HaxBitCoins(object):
    def __init__(self, browser):

        self.browser = browser

        if self.browser == 1:
            binary = FirefoxBinary(bin_loc)
            self.driver = webdriver.Firefox(executable_path="drivers/geckodriver.exe", firefox_binary=binary)
        else:
            opt = Options()
            opt.binary_location = chrome_bin
            self.driver = webdriver.Chrome(executable_path="drivers/chromedriver.exe", chrome_options=opt)

        self.captcha = CaptchaUpload(api_2, waittime=10, log=haxlog, counter=50)

    def is_element_exist(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    def wait_for_element(self, xpath, t):
        try:
            WebDriverWait(self.driver, t).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except Exception as e:
            print("An exception occured while waiting for element: ", e)
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

    def get_captcha2(self):
        path = "dumps/captcha/captcha.png"

        i = 5
        while not self.is_visible_css_selector('.captchasnet_captcha_content > img:nth-child(1)', 5):
            if i == 3:
                self.driver.refresh()
                i -= 1
                continue
            elif not i:
                return 1
            else:
                i -= 1
                continue
        else:
            element = self.driver.find_element_by_css_selector('.captchasnet_captcha_content > img:nth-child(1)')

        location = element.location_once_scrolled_into_view
        try:
            action = ActionChains(self.driver)
            action.move_to_element(element).perform()
        except Exception as e:
            print("An exception occured: ", e)
            print("Action move to didn't work")

        size = element.size

        # print(location, size)

        ss = self.driver.get_screenshot_as_base64()
        b64_img = base64.b64decode(ss)

        image = Image.open(BytesIO(b64_img))

        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']

        # print(left, top, right, bottom)

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
        """header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Chrome/62.0.3202.94 Safari/537.36'}

        i = 5
        while i:
            resp = requests.get(url, headers=header)
            status = resp.status_code
            if status == 200:
                print("Status OK: ", status)
                self.driver.get(url)
                break
            else:
                print("Status not OK: {0}".format(status))
                print("Trying again..")
                i -= 1
                continue
                """
        while not check_internet():
            change_ip()
        else:
            self.driver.get(url)

    def login_homepage(self, user, passw):

        # Wait for Login Script to appear then click
        if self.wait_for_element('/html/body/div[2]/div/nav/section/ul/li[10]/a', 20):
            loginbtn = self.driver.find_element_by_xpath('/html/body/div[2]/div/nav/section/ul/li[10]/a')
            self.driver.execute_script("arguments[0].click();", loginbtn)
        else:
            print("\nCan't find the Login button")

        # Wait for Login form to appear then submit
        if self.wait_for_element('//*[@id="login_form"]', 10):
            print("\nFilling login credentials.")
            try:
                username = self.driver.find_element_by_xpath('//*[@id="login_form_btc_address"]')
                password = self.driver.find_element_by_xpath('//*[@id="login_form_password"]')
                self.driver.execute_script('arguments[0].value = arguments[1]', username, user)
                self.driver.execute_script('arguments[0].value = arguments[1]', password, passw)
                self.driver.find_element_by_xpath('//*[@id="login_button"]').click()
                time.sleep(2)
            except Exception as e:
                print("\nAn exception occurred while filling login data: ", e)
                print("Can't login")
                raise SystemExit(0)

        else:
            print("\nLogin form not found in the page")

    def is_element_clickable(self, xpath, time1):
        try:
            WebDriverWait(self.driver, time1).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
        except:
            # print("\nAn exception occurred while waiting to be clickable: ", e)
            return False
        return True

    def enter_captcha(self):
        cap = input("Enter the captcha value: ")
        try:
            self.driver.find_element_by_xpath(
                '/html/body/div[2]/div/div[1]/div[5]/div[4]/div/div/div/div/div/input[2]').send_keys(str(cap))
        except Exception as e:
            print("\nAn exception occured while sending manual captcha answer: ", e)
            return False
        return True

    def get_score(self):
        try:
            if self.wait_for_element('//*[@id="free_play_digits"]', 2):
                i = self.driver.find_element_by_xpath('//*[@id="free_play_first_digit"]').text
                ii = self.driver.find_element_by_xpath('//*[@id="free_play_second_digit"]').text
                iii = self.driver.find_element_by_xpath('//*[@id="free_play_third_digit"]').text
                iv = self.driver.find_element_by_xpath('//*[@id="free_play_fourth_digit"]').text
                v = self.driver.find_element_by_xpath('//*[@id="free_play_fifth_digit"]').text

                print("\nYou Got: |{0}|{1}|{2}|{3}|{4}|".format(i, ii, iii, iv, v))
                # os.remove(captcha_path)
            else:
                print("\nCan't find reward!")
        except Exception as e:
            print("\nAn exception occured in score feature: ", e)
            pass

    def is_visible_xpath(self, xpath, t1):
        try:
            WebDriverWait(self.driver, t1).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        except NoSuchElementException or TimeoutException:
            return False
        return True

    def is_visible_css_selector(self, css_selector, t1):
        try:
            WebDriverWait(self.driver, t1).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
        except NoSuchElementException or TimeoutException:
            return False
        return True

    def close_tnc(self):
        # To close TnC bar
        print("\n>> Checking if TnC bar present and closing it.")
        try:
            j = 2
            while not self.is_visible_xpath('/html/body/div[1]/div/a[1]', 2) and j:
                j -= 1
                continue
            else:
                print("Found TnC Footer.")
                tnc_btn = self.driver.find_element_by_xpath('/html/body/div[1]/div/a[1]')
                self.driver.execute_script("arguments[0].click();", tnc_btn)
        except Exception as e:
            print("Warning: ", e)
            print("TnC Footer not found")

    def wait_by_css(self, css_selector, time1):
        try:
            WebDriverWait(self.driver, time1).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        except Exception as e:
            print("\nAn exception occurred while waiting for selector: ", e)
            return False
        return True

    def roll_table(self):
        try:
            print("\nFreebitcoin Balance: ", self.driver.find_element_by_xpath('//*[@id="balance"]').text)
        except Exception as e:
            print("\nProblem in getting balance: ", e)
            pass

        # Go to roll tab

        roll_tab = '/html/body/div[2]/div/nav/section/ul/li[2]/a'

        captcha_path = 'dumps/captcha/captcha.png'

        try:
            if self.is_visible_xpath(roll_tab, 1):
                self.driver.execute_script("arguments[0].click;", roll_tab)
        except Exception as e:
            print("\nException in finding Freebtc Tab: ", e)
            pass

        # Wait for roll table

        if self.wait_for_element('//*[@id="free_play_payout_table"]', 5):
            roll_btn = '//*[@id="free_play_form_button"]'

            # Check if Roll available:

            i = 1
            while self.is_element_clickable(roll_btn, 4):

                if i == 1:
                    # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                    print("\nChecking if Captcha present..")

                    if self.wait_by_css('.captchasnet_captcha_input_box', 10):
                        print("\nCapturing Captcha image using Dynamic src attribute.")

                        if self.get_captcha2() == 1:
                            return 4
                        else:
                            pass
                        self.close_tnc()

                        if os.path.isfile(captcha_path):
                            # input("\nPress Enter to continue!")
                            print("\n>> Requesting answer from 2captcha..\n")

                            while True:
                                ti = time.time()

                                rep = 5
                                while True:
                                    if not rep:
                                        if not check_internet():
                                            change_ip()
                                            rep += 2
                                        else:
                                            rep += 2
                                        continue
                                    else:
                                        try:
                                            value = self.captcha.solve(captcha_path)
                                        except:
                                            print("There is a problem in getting answer, trying again.")
                                            rep -= 1
                                            continue
                                        break

                                print("Captcha answer received is: ", str(value))

                                tf = time.time()
                                if value == 1:
                                    print("Can't solve captcha, getting new image.")
                                    try:
                                        refresh_captcha = self.driver.find_element_by_css_selector(
                                            'p.captchasnet_captcha_change_p:nth-child(3)')
                                        self.driver.execute_script("arguments[0].click();", refresh_captcha)
                                        time.sleep(3)
                                    except:
                                        print("Can't click refresh button")
                                    continue

                                elif value == 2:
                                    try:
                                        refresh_captcha = self.driver.find_element_by_css_selector(
                                            'p.captchasnet_captcha_change_p:nth-child(3)')
                                        self.driver.execute_script("arguments[0].click();", refresh_captcha)
                                        time.sleep(3)
                                    except:
                                        print("Can't click refresh button")
                                    continue

                                else:
                                    break

                            print("Time took by 2captcha: %2.2f" % (tf - ti))
                            try:
                                self.driver.find_element_by_css_selector('.captchasnet_captcha_input_box').send_keys(
                                    value)
                            except Exception as e:
                                print("\nAn exception occured while sending captcha key: ", e)
                                print("Can't input value into box, Enter it manually..")
                                if self.enter_captcha():
                                    i += 1
                                else:
                                    input("Press Enter to continue....")

                            self.driver.find_element_by_xpath(roll_btn).click()
                            i += 1
                            try:
                                print("Your 2captcha balance is: ", self.captcha.getbalance())
                            except TimeoutException:
                                pass
                            time.sleep(1.5)
                            self.get_score()
                        else:
                            print("Can't find captcha image")
                            if self.enter_captcha():
                                i += 1
                            else:
                                input("Press Enter to continue....")
                            self.driver.find_element_by_xpath(roll_btn).click()
                            time.sleep(1.5)
                            self.get_score()
                            i += 1

                    else:
                        print("Can't find captcha input box, Please input value in the browser and Press enter here!")
                        print("\nCapturing Captcha image using Dynamic src attribute.")
                        if self.get_captcha2() == 1:
                            return 4
                        else:
                            pass

                        self.close_tnc()

                        if os.path.isfile(captcha_path):
                            # input("\nPress Enter to continue! ")
                            print("\n>> Requesting answer from 2captcha..\n")
                            while True:
                                ti = time.time()
                                rep = 5
                                while True:
                                    if not rep:
                                        if not check_internet():
                                            change_ip()
                                            rep += 2
                                        else:
                                            rep += 2
                                        continue
                                    else:
                                        try:
                                            value = self.captcha.solve(captcha_path)
                                        except:
                                            print("There is a problem in getting answer, trying again.")
                                            rep -= 1
                                            continue
                                        break
                                print("\nCaptcha answer received is: ", str(value))
                                tf = time.time()
                                if value == 1:
                                    print("\nReceived Error from 2captcha, trying again.")
                                    continue
                                elif value == 2:
                                    return True
                                else:
                                    break
                            print("Time took by 2captcha: %2.2f" % (tf - ti))
                        else:
                            print("\nCan't capture captcha image")

                        input("Press Enter to continue....")
                        self.driver.find_element_by_xpath(roll_btn).click()
                        time.sleep(1.5)
                        try:
                            print("Your 2captcha balance is: ", self.captcha.getbalance())
                        except TimeoutException:
                            pass
                        self.get_score()
                        i += 1

                else:
                    print("\nWrong Captcha, try again..")
                    self.captcha.refund()

                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    print("\nTrying to get the Captcha input box.")
                    time.sleep(1)
                    if self.wait_by_css('.captchasnet_captcha_input_box', 10):
                        print("\n>> Capturing New Captcha image using Dynamic src attribute.")
                        if self.get_captcha2() == 1:
                            return 4
                        else:
                            pass

                        # Check if any error occurred

                        if self.is_visible_css_selector('#free_play_error', 1.5):
                            if 'Captcha is incorrect or has expired' not in self.driver.find_element_by_css_selector(
                                    '#free_play_error').text:
                                print("""!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                                         !!PLEASE VERIFY YOUR ACCOUNT!!
                                         !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!""")
                                return 3

                        else:
                            pass

                        self.close_tnc()

                        if os.path.isfile(captcha_path):
                            # input("\nPress Enter to continue! ")
                            print("\n>> Requesting answer from 2captcha..\n")
                            while True:
                                ti = time.time()
                                rep = 5
                                while True:
                                    if not rep:
                                        if not check_internet():
                                            change_ip()
                                            rep += 2
                                        else:
                                            rep += 2
                                        continue
                                    else:
                                        try:
                                            value = self.captcha.solve(captcha_path)
                                        except:
                                            print("There is a problem in getting answer, trying again.")
                                            rep -= 1
                                            continue
                                        break

                                print("Captcha answer is: ", str(value))
                                tf = time.time()
                                if value == 1:
                                    print("Received Error from 2captcha, trying again.")
                                    continue
                                elif value == 2:
                                    return 2
                                else:
                                    break
                            print("Time took by 2captcha: %2.2f" % (tf - ti))
                            print(">> Entering captcha value in the answer box.")
                            try:
                                self.driver.find_element_by_css_selector('.captchasnet_captcha_input_box').send_keys(
                                    value)
                            except Exception as e:
                                print("\nAn exception occurred while entering answer: ", e)
                                print("Can't input value into box, Enter it manually..")
                                if self.enter_captcha():
                                    i += 1
                                else:
                                    input("Press Enter to continue....")

                        else:
                            print("Can't find captcha image")
                            input("Press any key to continue....")

                        self.driver.find_element_by_xpath(roll_btn).click()
                        i += 1
                        try:
                            print("Your 2captcha balance is: ", self.captcha.getbalance())
                        except TimeoutException:
                            pass
                        self.get_score()

                    else:
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        try:
                            action = ActionChains(self.driver)
                            box = self.driver.find_element_by_css_selector('.captchasnet_captcha_input_box')
                            action.move_to_element(box).perform()
                        except Exception as e:
                            print("\nAn exception occured in moving to captcha box: ", e)
                            pass
                        print("\nCan't find captcha input box, Please input value in the browser and Press enter here!")
                        print("\n>> Getting captcha src attribute and saving image")
                        if self.get_captcha2() == 1:
                            return 4
                        else:
                            pass
                        if os.path.isfile(captcha_path):
                            # input("\nPress Enter to continue!")
                            print("\n>> Requesting answer from 2captcha..\n")
                            while True:
                                ti = time.time()
                                rep = 5
                                while True:
                                    if not rep:
                                        if not check_internet():
                                            change_ip()
                                            rep += 2
                                        else:
                                            rep += 2
                                        continue
                                    else:
                                        try:
                                            value = self.captcha.solve(captcha_path)
                                        except:
                                            print("There is a problem in getting answer, trying again.")
                                            rep -= 1
                                            continue
                                        break
                                print("Captcha answer is: ", str(value))
                                tf = time.time()
                                if value == 1:
                                    print("Received Error from 2captcha, check Log, trying again.")
                                    continue
                                elif value == 2:
                                    return True
                                else:
                                    break
                            print("Time took by 2captcha: %2.2f" % (tf - ti))

                        else:
                            print("Can't find captcha image")
                        input("Press Enter to continue....")
                        self.driver.find_element_by_xpath(roll_btn).click()
                        time.sleep(1.5)
                        self.get_score()
                        i += 1

            else:
                return 1
        else:
            print("Something went wrong! Can't Find Roll table!!")

    def quit_fox(self):
        self.driver.quit()

    def del_session(self):
        self.driver.delete_all_cookies()

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

            except Exception as e:
                print("\nAn exception occured: ", e)
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

            except Exception as e:
                print("\nAn exception occured: ", e)
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

    except Exception as e:
        print("\nAn exception occured in creating socket connection: ", e)
        return False

    return True


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
        ip_method = int(input("\nSelect your Internet Connection method:\n1. USB MODEM, 2. MOBILE TETHERING\n>  "))
    except ValueError:
        print("Enter only integers, try again..")
        continue
    if ip_method == 1 or ip_method == 2:
        break
    else:
        print("Enter valid response, try again.")
        continue


def modem_on(connection, timet):
    cmd = ["rasdial", connection]
    subprocess.run(cmd, timet)


def modem_off(connection, timet):
    cmd = ["rasdial", connection, "/disconnect"]
    subprocess.run(cmd, timet)

ips = []

if ip_method == 1:

    if not check_internet():
        try:
            modem_on(connection_name, 20)
        except subprocess.TimeoutExpired:
            print("Can't dial connection")
            raise SystemExit(0)


    def change_ip():
        while True:
            try:
                modem_off(connection_name, 10)
                print(" ")
                modem_on(connection_name, 15)
            except subprocess.TimeoutExpired:
                print("Problem in Dialup connection, trying again..")
                continue
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

            except Exception as e:
                print("\nAn exception occured while switching dialup: ", e)
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
    t_start = time.time()
    print("\nBot started at: {0}".format(time.ctime(t_start)))
    with open("start_time.txt", 'w') as time_file:
        time_file.write(time.ctime(t_start))

    counter = 0

    print("\n>> Checking accounts file for new accounts...")

    try:
        acc_file = open("accounts.txt", "r")
    except Exception as e:
        print("\nAn exception occured while opening accounts file: ", e)
        print("!!!! - Accounts.txt file not found. Refer documentation -!!!!")
        raise SystemExit(0)

    if os.path.getsize("accounts.txt") == 0:
        print("!!!! - Account file is empty - !!!!")
        raise SystemExit(0)

    ac_list = []

    for line in acc_file.readlines():
        username = line.split('@')[0]
        ac_list.append(username)
        acc_file.close()

    if not os.path.isfile("dumps/accounts_map.hk"):
        print("\nNo accounts dump found, generating new..")
        acc_time = {}

        for ac in ac_list:
            acc_time[ac] = 0.00

        pickle.dump(acc_time, open("dumps/accounts_map.hk", 'wb'))
        accounts_time = acc_time

    else:
        print("\n>> Previous accounts dump found.")
        old_dict = pickle.load(open("dumps/accounts_map.hk", "rb"))
        new_accounts = check_pikle(ac_list)
        if len(new_accounts):
            for item in new_accounts:
                old_dict.update({item: 0.00})

            pickle.dump(old_dict, open("dumps/accounts_map.hk", "wb"))
            print("- Found new accounts, adding them to dump database")
        else:
            print("- No new account found.")
        accounts_time = old_dict

    while True:

        while not check_internet():
            change_ip()

        for acc in accounts_time.keys():

            print("\nCurrent account: ", acc)

            t1 = time.time()
            t2 = accounts_time.get(acc)
            time_been = t1 - float(t2)
            if time_been > float(60 * 60) or time_been == t1:
                try:
                    ip_now = get_ip()
                except:
                    print("Can't get ip address")
                if counter:
                    while ip_now == ips[-1]:
                        print("IP not changed, trying to change.")
                        while not check_internet():
                            change_ip()
                print("Your current IP Address: %s" % ip_now)
                if counter:
                    print("Last IP Address: {0}".format(ips[-1]))

                ips.append(ip_now)

                if not counter:
                    HaxObject = HaxBitCoins(browser_choice)

                print("Opening FreeBitcoin website.")
                while True:
                    try:
                        HaxObject.load_url(captcha_page)
                    except Exception as e:
                        print("\nException occured while loading url: ", e)
                        print("Can't open url")
                        continue
                    break

                if os.path.isfile(dump_location + acc + ".hax"):
                    print("\nCookies file found - " + acc + ".hax")
                    try:
                        print("\n>> Trying to restore cookies, Please wait..")
                        HaxObject.load_session(dump_location + acc + ".hax")
                        HaxObject.load_url(captcha_page)
                    except Exception as e:
                        print("Error in restoring session: ", e)
                        print("Reloading and checking if on Homepage.")
                        HaxObject.load_url(captcha_page)

                    if not HaxObject.is_element_clickable('//*[@id="free_play_form_button"]', 5):
                        print("Can't restore previous session, trying to login..")
                        HaxObject.load_url(captcha_page)
                        with open('accounts.txt', 'r') as f:
                            for line in f:
                                if acc in line:
                                    user = line.split(':')[0].strip()
                                    password = line.split(':')[1].strip()

                        HaxObject.login_homepage(user, password)
                        time.sleep(4)
                    else:
                        print("Success in restoring cookies: Homepage found!")

                    roll_status = HaxObject.roll_table()

                    if roll_status == 3:
                        print("Check verify_accounts.txt file")
                        with open("verify_accounts.txt", "a") as verify_ac:
                            verify_ac.write(acc + "\n")
                    elif roll_status == 2:
                        print("Error: Too many Captcha attemps.")
                    elif roll_status == 4:
                        print("Can't capture Captcha image.")
                    else:
                        accounts_time[acc] = time.time()
                        pickle.dump(accounts_time, open("dumps/accounts_map.hk", "wb"))

                    print("\nSaving current session cookies.")
                    HaxObject.save_session(dump_location + acc + ".hax")
                    # HaxObject.quit_fox()
                    print("\nDeleting current session!")
                    HaxObject.del_session()
                else:
                    with open('accounts.txt', 'r') as f:
                        for line in f:
                            if acc in line:
                                user = line.split(':')[0].strip()
                                password = line.split(':')[1].strip()

                    print("No Cookie found for this account, Trying to Log in.")
                    HaxObject.login_homepage(user, password)
                    time.sleep(4)

                    roll_status = HaxObject.roll_table()

                    if roll_status == 3:
                        print("Check verify_accounts.txt file")
                        with open("verify_accounts.txt", "a") as verify_ac:
                            verify_ac.write(acc + "\n")
                    elif roll_status == 2:
                        print("Error: Too many Captcha attemps.")
                    elif roll_status == 4:
                        print("Can't capture Captcha image.")
                    else:
                        accounts_time[acc] = time.time()
                        pickle.dump(accounts_time, open("dumps/accounts_map.hk", "wb"))
                    print("Saving current session cookies.")
                    HaxObject.save_session(dump_location + acc + ".hax")
                    # HaxObject.quit_fox()
                    HaxObject.del_session()

                counter += 1

                t_now = time.time()
                print("\nTime Elapsed: %2.2f minutes" % ((t_now - t_start) / 60))
                print("Accounts processed: %d" % counter)

                print("\nChanging your IP before Next Roll\n")
                change_ip()

                print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")

            else:
                print("\nWaiting for Next challenge!")
                print("Time left: %.2f minutes" % ((3600 - time_been) / 60))
                print("- - - - - - - - - - - - - - -")


if __name__ == '__main__':
    main()
