import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class WebDriver:
    def __init__(self):
        print("Building Web Driver...")
        
        load_dotenv()
        self.username = os.getenv("USERNAME")
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")
        self.crm_url = os.getenv("CRM_URL")
        self.fundraising_url = os.getenv("FUNDRAISING_URL")

        self.driver1 = webdriver.Firefox()

        print("Web Driver Built.")

    def OpenCRM() -> None:
        pass

    def OpenFundraising() -> None:
        pass

    def ExportFromFundraising() -> None:
        pass

    def SendReceipts() -> None:
        pass