import pickle

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

# chrome driver init
service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)


def authorize():
    driver.get('https://buff.163.com/')
    input("Press Enter after authorization to continue...")
    pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))


if __name__ == '__main__':
    authorize()
