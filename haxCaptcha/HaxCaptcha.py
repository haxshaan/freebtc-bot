from os.path import exists
from requests import post, get
from time import sleep
import pickle


class CaptchaUpload:
    def __init__(self, key, log=None, waittime=None, counter=15):
        self.settings = {"url_request": "http://2captcha.com/in.php",
                         "url_response": "http://2captcha.com/res.php",
                         "key": key}
        if counter:
            self.counter = counter
        else:
            self.counter = 15

        if log:
            self.log = log
            self.logenabled = True
        else:
            self.logenabled = False

        if waittime:
            self.waittime = waittime
        else:
            self.waittime = 10

    def getbalance(self):
        """
        This request need for get balance
        :return: <YOURBALANCE> OK | 1 ERROR!
        """
        fullurl = "%s?action=getbalance&key=%s" % (
            self.settings['url_response'], self.settings['key'])
        request = get(fullurl)
        if "." in request.text:
            if self.logenabled:
                self.log.info("[2CaptchaUpload] Balance: %s" % request.text)
            return request.text
        elif request.text == "ERROR_KEY_DOES_NOT_EXIST":
            if self.logenabled:
               self.log.error("[2CaptchaUpload] You used the wrong key in "
                              "the query")
            return 1
        elif request.text == "ERROR_WRONG_ID_FORMAT":
            if self.logenabled:
                self.log.error("[2CaptchaUpload] Wrong format ID CAPTCHA. "
                               "ID must contain only numbers")
            return 1

    def getresult(self, id):
        """
        This function return the captcha solved
        :param id: id captcha returned by upload
        :return: <captchaword> OK | 1 ERROR!
        """
        if self.logenabled:
            self.log.info("[2CaptchaUpload] Wait %s second.." % self.waittime)
        sleep(self.waittime)
        fullurl = "%s?key=%s&action=get&id=%s" % (self.settings['url_response'],
                                                  self.settings['key'], id)
        if self.logenabled:
            self.log.info("[2CaptchaUpload] Get Captcha solved with id %s"
                          % id)
        request = get(fullurl)
        if request.text.split('|')[0] == "OK":
            return request.text.split('|')[1]
        elif request.text == "CAPCHA_NOT_READY" and self.counter:
            if self.logenabled:
                self.log.error("[2CaptchaUpload] CAPTCHA is being solved, "
                              "repeat the request several seconds later, wait "
                              "another %s seconds" % self.waittime)
            self.counter -= 1
            return self.getresult(id)
        elif request.text == "CAPCHA_NOT_READY" and not self.counter:
            if self.logenabled:
                self.log.error("Can't solve Captcha, tried many times.")
            return 2
        elif request.text == "ERROR_KEY_DOES_NOT_EXIST":
            if self.logenabled:
               self.log.error("[2CaptchaUpload] You used the wrong key in "
                             "the query")
            return 1
        elif request.text == "ERROR_WRONG_ID_FORMAT":
            if self.logenabled:
                self.log.error("[2CaptchaUpload] Wrong format ID CAPTCHA. "
                               "ID must contain only numbers")
            return 1
        elif request.text == "ERROR_CAPTCHA_UNSOLVABLE":
            if self.logenabled:
                self.log.error("[2CaptchaUpload] Captcha could not solve "
                               "three different employee. Funds for this "
                               "captcha not")
            return 1

    def refund(self):

        ids = pickle.load(open("captcha_id.p", "rb"))

        print("Saved id: ", ids)

        fullurl = "%s?key=%s&action=reportbad&id=%s" % (self.settings['url_response'],
                                                        self.settings['key'], ids)

        if self.logenabled:
            self.log.info("[2CaptchaUpload] Requesting refund for the captcha id %s"
                          % ids)
        request = get(fullurl)

        print("Response of Complaint: ", request.text)

    def solve(self, pathfile):
        """
        This function upload read, upload and is the wrapper for solve
            the captcha
        :param pathfile: path of image
        :return: <captchaword> OK | 1 ERROR!
        """
        if exists(pathfile):
            files = {'file': open(pathfile, 'rb')}
            payload = {'key': self.settings['key'], 'method': 'post'}
            if self.logenabled:
                self.log.info("[2CaptchaUpload] Uploading to 2Captcha.com..")
            request = post(self.settings['url_request'], files=files,
                           data=payload)
            if request.ok:
                if request.text.split('|')[0] == "OK":
                    if self.logenabled:
                        self.log.info("[2CaptchaUpload] Upload Ok")

                    idx = request.text.split('|')[1]
                    pickle.dump(idx, open("captcha_id.p", "wb"))

                    return self.getresult(request.text.split('|')[1])

                elif request.text == "ERROR_WRONG_USER_KEY":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] Wrong 'key' parameter"
                                       " format, it should contain 32 symbols")
                    return 1
                elif request.text == "ERROR_KEY_DOES_NOT_EXIST":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] The 'key' doesn't "
                                       "exist")
                    return 1
                elif request.text == "ERROR_ZERO_BALANCE":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] You don't have money "
                                       "on your account")
                    return 1
                elif request.text == "ERROR_NO_SLOT_AVAILABLE":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] The current bid is "
                                       "higher than the maximum bid set for "
                                       "your account.")
                    return 1
                elif request.text == "ERROR_ZERO_CAPTCHA_FILESIZE":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] CAPTCHA size is less"
                                       " than 100 bites")
                    return 1
                elif request.text == "ERROR_TOO_BIG_CAPTCHA_FILESIZE":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] CAPTCHA size is more"
                                       " than 100 Kbites")
                    return 1
                elif request.text == "ERROR_WRONG_FILE_EXTENSION":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] The CAPTCHA has a "
                                       "wrong extension. Possible extensions "
                                       "are: jpg,jpeg,gif,png")
                    return 1
                elif request.text == "ERROR_IMAGE_TYPE_NOT_SUPPORTED":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] The server cannot "
                                       "recognize the CAPTCHA file type.")
                    return 1
                elif request.text == "ERROR_IP_NOT_ALLOWED":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] The request has sent "
                                       "from the IP that is not on the list of"
                                       " your IPs. Check the list of your IPs "
                                       "in the system.")
                    return 1
                elif request.text == "IP_BANNED":
                    if self.logenabled:
                        self.log.error("[2CaptchaUpload] The IP address you're"
                                       " trying to access our server with is "
                                       "banned due to many frequent attempts "
                                       "to access the server using wrong "
                                       "authorization keys. To lift the ban, "
                                       "please, contact our support team via "
                                       "email: support@2captcha.com")
                    return 1

        else:
            if self.logenabled:
                self.log.error("[2CaptchaUpload] File %s not exists" % pathfile)
            return 1
