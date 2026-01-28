import os
import time
import platform
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains


class WebDriver:
    def __init__(self):
        print("Building Web Driver...")        
        load_dotenv()
        self.os = platform.system()
        self.username = os.getenv("USERNAME")
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")
        self.crmURL = os.getenv("CRM_URL")
        self.fundraisingURL = os.getenv("FUNDRAISING_URL")

        self.targetTemplate = "Donation Receipt (template)"
        self.emailName = "automated_email"
        self.emailNumberName = ""
        self.createdBy = "BloomerangFundraisingIntegration-Dillon Phillips"

        self.emailPrepped = False

        self.d1 = webdriver.Firefox()  # CRM
        self.d2 = webdriver.Firefox()  # Fundraising

        self.a1 = ActionChains(self.d1) # Action chain for CRM Driver

        print(f"Operating system identified: {self.os}")
        print("Web Driver Built.")

    def OpenCRM(self, d: webdriver.Firefox) -> None:
        '''
        * This method logs in the driver and navigates to the proper page
        * to start the main loop. 
        '''
        d.get(self.crmURL)
        self.SendKeys("usernameField", self.username, d)
        self.SendKeys("passwordField", self.password, d)
        self.ClickID("login-submit", d)


    def NavigateToExport(self, d: webdriver.Firefox) -> None:
        '''
        * This method logs in the driver to the CRM then navigates to the
        * Fundraising export page.
        '''
        d.get(self.fundraisingURL)
        self.ClickFromClass("ui-primary-color", "Confirm", d)
        d.get(self.fundraisingURL)


    def NavigateToEmailSend(self, emailNum: int, d: webdriver.Firefox) -> None:
        d.get(self.crmURL + "/Mailing/Email/Template/Edit/23")
        self.ClickID("email-copy-button", d)
        d.switch_to.window(d.window_handles[1])
        self.ClickID("edit-email-name-btn", d)
        self.emailNumberName = self.emailName + "_" + str(emailNum)
        self.SendKeys("email-title-input", self.emailNumberName + Keys.ENTER, d)
        self.ClickID("recipients-tab", d)
        self.emailPrepped = True


    def SendReceipts(self, d: webdriver.Firefox) -> bool:
        '''
        * This method will loop
        '''

        self.WaitToBeClickable(By.CLASS_NAME, "btn-refresh", d)
        time.sleep(2)

        if (self.CheckIfElementExists(By.CLASS_NAME, "summary-row", d)):
            print("Donors found!")
            self.ClickID("email-save-and-button", d)
            self.ClickID("email-save-and-button-0", d)
            self.ClickID("send-bee", d)

            sendMenuElements = d.find_elements(By.CSS_SELECTOR, ".dropdown-menu > li")
            print(sendMenuElements)
            print(len(sendMenuElements))

            if (len(sendMenuElements) > 1):
                print("Can send!")
                sendMenuElements[0].click()
                self.emailPrepped = False
            else:
                print("Cannot send email...")
                self.ClickFromClass("btn ", "Make Changes", d)
                self.ClickID("recipients-tab", d)

        else:
            print("No donors yet...")
            return False


    def ExportDontations(self, d: webdriver.Firefox) -> None:
        '''
        * This method will loop 
        '''
        self.ClickFromClass("border-solid", "Export", d)
        self.ClickID("dialog__decline", d)


    def DeactivateEmail(self, d: webdriver.Firefox) -> bool:
        emailDeactivated = False 
        
        # Get all rows
        rows = d.find_elements(By.ID, "data-grid-row")

        # Get row that has the right name
        print("Searching rows for email...")
        for row in rows:
            name = row.find_element(By.CLASS_NAME, "email-name-data").text

            # Deactivate that email with name
            if name == self.emailNumberName:
                print("Found email")
                row.find_element(By.CLASS_NAME, "MuiButtonBase-root").click()
                row.find_element(By.ID, "toggle-email-menu-action").click()
                emailDeactivated = True
        
        return emailDeactivated


    def ClickID(self, ID: str, d: webdriver.Firefox) -> None:
        '''
        * Waits for the element with the ID of [ID] to appear, then
        * clicks on it.
        '''
        self.WaitFor(By.ID, ID, d)
        d.find_element(By.ID, ID).click()


    def SendKeys(self, ID: str, sentString: str, d: webdriver.Firefox) -> None:
        '''
        * Clears the selected text field, then sends the value of 
        * [sentString] into the field.
        '''
        self.WaitFor(By.ID, ID, d)
        field = d.find_element(By.ID, ID)
        key = Keys.CONTROL

        if (self.os == "Darwin"):
            key = Keys.COMMAND

        field.send_keys(key, "a")
        field.send_keys(sentString)


    def ClickFromClass(self, className: str, targetText: str, d: webdriver.Firefox) -> None:
        '''
        * This is a helper function to make it easier to target an HTML
        * element that does not have an ID. It uses the className, then 
        * targets the specific element based on its innerText (targetText).
        '''
        self.WaitFor(By.CLASS_NAME, className, d)
        collection = d.find_elements(By.CLASS_NAME, className) 
        
        for e in collection:
            if e.text == targetText:
                print("Clicking on", targetText)
                e.click()
                break


    def CheckIfElementExists(self, selectorType, selectorName: str, d: webdriver.Firefox) -> bool:
        exists = False
        try:
            d.find_element(selectorType, selectorName)
            print(f'"{selectorName}" found!')
            exists = True
        except NoSuchElementException:
            print(f'"{selectorName}" not found...')
            time.sleep(1)
        
        return exists


    def WaitFor(self, selectorType, selectorName: str, d: webdriver.Firefox):
        '''
        * Will halt web driver automation until a certain element
        * is on the screen. This is used to allow the user to login 
        * before the automation starts.
        *
        * Parameters:
        * - [selectorType]: uses the selenium "By" type. Ex) ID would be: [By.ID]
        * - [selectorName]: string for ID or Class name
        * - [d]: the webdriver object
        '''

        while True:
            if (self.CheckIfElementExists(selectorType, selectorName, d)):
                return
            else:
                print(f"Searching for {selectorName}")
                continue


    def WaitToBeClickable(self, selectorType, selectorName: str, d: webdriver.Firefox):
        while True:
            time.sleep(1)
            try:
                element = d.find_element(selectorType, selectorName)
                d.execute_script("arguments[0].scrollIntoView(true);", element)
                element.click()

                print(f"{selectorName} clicked!")
                return
            except ElementClickInterceptedException:
                print(f"{selectorName} not yet clickable...")