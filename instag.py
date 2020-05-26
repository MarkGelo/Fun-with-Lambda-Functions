from time import sleep
from selenium import webdriver
import autoit
from selenium.webdriver.common.keys import Keys

username = 'user'
password = 'pass'
images_path = r'path'
caption = ''

class insta:
    def __init__(self):
        # mobile emulation
        mobile_emulation = {'deviceName' : 'iPhone X'}
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('mobileEmulation', mobile_emulation)

        self.driver = webdriver.Chrome(executable_path = 'chromedriver.exe', options = chrome_options)
        self.driver.get('https://www.instagram.com')
        sleep(3)
    
    def login(self, username, password):
        self.username = username
        self.driver.find_element_by_xpath("//button[contains(text(),'Log In')]").click() # click login button
        sleep(2)
        # input username and password
        self.driver.find_element_by_xpath("//input[@name='username']").send_keys(username)
        sleep(2)
        self.driver.find_element_by_xpath("//input[@name='password']").send_keys(password)
        
        #click login button again
        self.driver.find_element_by_xpath('//button[@type="submit"]').click() # click login button
        sleep(2)
        
    def close_notifications(self):
        # login info
        try:
            sleep(3)
            self.driver.find_element_by_xpath("//button[contains(text(),'Not Now')]").click()
        except:
            pass
        # home screen
        try:
            sleep(3)
            self.driver.find_element_by_xpath("//button[contains(text(),'Cancel')]").click()
        except:
            pass
        # notif
        try:
            sleep(3)
            self.driver.find_element_by_xpath("//button[contains(text(),'Not Now')]").click()
        except:
            pass
    
    def post(self, image, caption, hashtags):
        self.driver.find_element_by_xpath('//div[contains(@class, "q02Nz _0TPg")]').click() # click new post
        # go to the popped up open browser to select the image
        handle = "[CLASS:#32770; TITLE:Open]"
        autoit.win_wait(handle, 60)
        sleep(1)
        autoit.control_set_text(handle, "Edit1", '{}\{}'.format(images_path, image))
        sleep(2)
        autoit.control_click(handle, "Button1")
        sleep(2)
        # expand the image
        self.driver.find_element_by_xpath('//button[contains(@class, "pHnkA")]').click()
        sleep(2)
        # click next
        self.driver.find_element_by_xpath("//button[contains(text(),'Next')]").click()
        sleep(3)
        # add caption
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/div[2]/section[1]/div[1]/textarea').click()
        self.driver.find_element_by_xpath('//*[@id="react-root"]/section/div[2]/section[1]/div[1]/textarea').send_keys('{}\n\n{}'.format(caption, ' '.join(hashtags)))
        sleep(2)
        # click share button
        self.driver.find_element_by_xpath('//button[contains(text(), "Share")]').click()
    
    def exit(self):
        self.driver.quit()

if __name__ == '__main__':
    instaAcc = insta()

    instaAcc.login(username, password)
    instaAcc.close_notifications()
    instaAcc.post('fileName with jpg or whatever', 'caption', ['#hashtags'])
    # turn on notifications notif after posting, can just ignore and straight up exit?
    instaAcc.exit()