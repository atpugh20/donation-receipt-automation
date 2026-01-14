import os
import time
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

        self.targetEmail = "Donation Receipt Copy (Copy)"
        self.createdBy = "BloomerangFundraisingIntegration-Dillon Phillips"

        self.driver1 = webdriver.Firefox()

        print("Web Driver Built.")

    def OpenCRM(self) -> None:
        self.driver1.get(self.crm_url)
        time.sleep(1)
        self.driver1.find_element(By.ID, "usernameField").send_keys(self.username)
        self.driver1.find_element(By.ID, "passwordField").send_keys(self.password)
        time.sleep(1)
        self.driver1.find_element(By.ID, "login-submit").click()
        time.sleep(2)
        self.driver1.find_element(By.ID, "communications-sub-navigation-label").click()
        time.sleep(1)
        self.driver1.find_element(By.ID, "emails-navigation-link-label").click()
        time.sleep(1)
        self.ClickFromClass("email-name-data", self.targetEmail)

        time.sleep(1)

        self.driver1.find_element(By.ID, "recipients-tab").click()
        time.sleep(1)
        self.driver1.find_element(By.CLASS_NAME, "filter-tag-drag-source").click()
        time.sleep(1)

        self.ClickFromClass("name-button", "Acknowledgement Status")

        time.sleep(2)

        self.driver1.find_element(By.CLASS_NAME, "rw-widget-input").click()
        self.ClickFromClass("multiselect-item", "No")
        self.driver1.find_element(By.CLASS_NAME, "btn-primary").click()
        time.sleep(1)
        self.ClickFromClass("cell", "And...")
        self.ClickFromClass("name-button", "Created By")
        time.sleep(1)
        self.ClickFromClass("name-button", "Created By")
        time.sleep(1)
        self.driver1.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[1]/div/div/div[4]/div[4]/div/div/section/div/div[2]/div/div/div/div/section/div/div/div[2]/div/div/input").send_keys(self.createdBy)
        self.driver1.find_element(By.CLASS_NAME, "btn-primary").click()

        time.sleep(1)
        self.driver1.find_element(By.ID, "email-save-and-button").click()
        self.driver1.find_element(By.ID, "email-save-and-button-0").click()



    def OpenFundraising(self) -> None:
        pass

    def ExportFromFundraising(self) -> None:
        pass

    def SendReceipts(self) -> None:
        pass

    def ClickFromClass(self, className: str, targetText: str) -> None:
        collection = self.driver1.find_elements(By.CLASS_NAME, className) 
        
        for e in collection:
            if e.text == targetText:
                print("Clicking on", targetText)
                e.click()
                break