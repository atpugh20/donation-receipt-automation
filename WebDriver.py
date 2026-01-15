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

        self.targetTemplate = "Donation Receipt (template)"
        self.emailName = "automated_email"
        self.createdBy = "BloomerangFundraisingIntegration-Dillon Phillips"

        self.driver = webdriver.Firefox()

        print("Web Driver Built.")

    def OpenCRM(self) -> None:
        self.driver.get(self.crm_url)
        self.SendKeys("usernameField", self.username)
        self.SendKeys("passwordField", self.password)
        self.ClickID("login-submit")
        time.sleep(1)  # Extra time for page load
        self.ClickID("communications-sub-navigation-label")
        self.ClickID("emails-navigation-link-label")
        self.ClickFromClass("MuiButton-colorPrimary", "New Email")
        self.ClickID("saved-templates-tab")
        self.ClickFromClass("email-name-data", self.targetTemplate)
        self.ClickID("email-name-input")
        self.ClickID("email-name-modal-confirm")


        
    def SendReceipts(self) -> None:
        '''
        * This is the method that loops.
        '''
        pass

    def ClickID(self, ID: str) -> None:
        time.sleep(1)
        self.driver.find_element(By.ID, ID).click()

    def SendKeys(self, ID: str, sentString: str) -> None:
        time.sleep(1)
        self.driver.find_element(By.ID, ID).send_keys(sentString)

    def ClickFromClass(self, className: str, targetText: str) -> None:
        '''
        * This is a helper function to make it easier to target an HTML
        * element that does not have an ID. It uses the className, then 
        * targets the specific element based on its innerText (targetText).
        '''
        time.sleep(1)
        collection = self.driver.find_elements(By.CLASS_NAME, className) 
        
        for e in collection:
            if e.text == targetText:
                print("Clicking on", targetText)
                e.click()
                break