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
    def __init__(self, usesFundrasing: bool):
        print("Building Web Driver...")        
        load_dotenv()
        self.os = platform.system()
        self.username = os.getenv("B_USERNAME")
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
        if usesFundrasing:
            self.d2 = webdriver.Firefox()  # Fundraising

        self.a1 = ActionChains(self.d1) # Action chain for CRM Driver

        print(f"Operating system identified: {self.os}")
        print("Web Driver Built.")


    def LoginCRM(self, d: webdriver.Firefox) -> None:
        '''
        * This method logs in the driver and navigates to the proper page
        * to start the main loop. 
        * 
        * Parameters:
        * - [d]: the webdriver object
        '''
        self.SendKeys("usernameField", self.username, True, d)
        self.SendKeys("passwordField", self.password, True, d)
        self.ClickID("login-submit", True, d)


    def NavigateToExport(self, d: webdriver.Firefox) -> None:
        '''
        * This method logs in the driver to the CRM then navigates to the
        * Fundraising export page.
        *
        * Parameters:
        * - [d]: the webdriver object
        '''
        d.get(self.fundraisingURL)
        self.ClickFromClass("ui-primary-color", "Confirm", False, d)
        d.get(self.fundraisingURL)


    def NavigateToEmailSend(self, emailNum: int, d: webdriver.Firefox) -> None:
        '''
        * This method prepares a new email to be sent, using [emailNum] to
        * identify which email number we are on. 
        *
        * Parameters:
        * - [emailNum]: the iterator that says wh
        * - [d]: the webdriver object
        '''
        d.get(self.crmURL + "/Mailing/Email/Template/Edit/23")
        self.ClickID("email-copy-button", False, d)
        d.switch_to.window(d.window_handles[1])
        self.ClickID("edit-email-name-btn", False, d)
        self.emailNumberName = self.emailName + "_" + str(emailNum)
        self.SendKeys("email-title-input", self.emailNumberName + Keys.ENTER, False, d)
        self.ClickID("recipients-tab", False, d)
        self.emailPrepped = True


    def SendReceipts(self, d: webdriver.Firefox) -> bool:
        '''
        * This method will loop.
        * 
        * From the email send page, this method:
        * 1. Checks for any new donors
        * 2. Checks if these new donors are able to receive the email
        * 3. Sends the email if they are able to receive it
        * 
        * Paramters:
        * - [d]: the webdriver object
        '''
        self.WaitToBeClickable(By.CLASS_NAME, "btn-refresh", False, d)
        time.sleep(2)

        # Check to see if there are any new donors
        self.CheckLogin(d)
        if (self.CheckIfElementExists(By.CLASS_NAME, "summary-row", False, d)):
            print("Donors found!")
            self.ClickID("email-save-and-button", False, d)
            self.ClickID("email-save-and-button-0", False, d)
            self.ClickID("send-bee", False, d)

            self.WaitFor(By.CSS_SELECTOR, ".dropdown-menu > li", False, d)
            sendMenuElements = d.find_elements(By.CSS_SELECTOR, ".dropdown-menu > li")

            # Check to see if these contacts are able to receive this email
            if (len(sendMenuElements) > 1):
                print("Can send!")

                # Send email
                for e in sendMenuElements:
                    if e.text == "Send Now":
                        e.click()
                        break
                
                # Confirm sent email
                self.ClickFromClass("btn-success", "Yes", False, d)

                # Close window and refresh page
                d.close()
                d.switch_to.window(d.window_handles[0])
                self.emailPrepped = False
                d.refresh()
            else:
                # Return to donor table screen
                print("Cannot send email...")
                self.ClickFromClass("btn ", "Make Changes", False, d)
                self.ClickID("recipients-tab", False, d)

        else:
            print("No donors yet...")
            return False


    def ExportDontations(self, d: webdriver.Firefox) -> None:
        '''
        * This method will loop. It will continuously click the export
        * button that is located on the fundraising page integrations page.
        *
        * Paramters:
        * - [d]: the webdriver object
        '''
        print("Starting Export...")
        self.ClickFromClass("border-solid", "Export", False, d)
        self.ClickID("dialog__decline", False, d)
        print("Export completed!")


    def DeactivateEmail(self, d: webdriver.Firefox) -> bool:
        emailDeactivated = False

        d.get(self.crmURL + "/Mailing/Email/Template/")
        
        # Get all rows
        self.CheckLogin(d)
        rows = self.GetClassListElements("data-grid-row", False, d)

        # Get row that has the right name
        print("Searching rows for email...")
        for row in rows:
            self.CheckLogin(d)
            name = row.find_element(By.CLASS_NAME, "email-name-data").text

            # Deactivate that email with name
            if name == self.emailNumberName:
                print(f"Found {self.emailNumberName}!")
                time.sleep(1)
                row.find_element(By.CLASS_NAME, "MuiButtonBase-root").click()
                self.ClickID("toggle-email-menu-action", False, d)
                emailDeactivated = True
            else:
                print(f"Could not find {self.emailNumberName}")
        
        return emailDeactivated


    def ClickID(self, ID: str, loggingIn: bool, d: webdriver.Firefox) -> None:
        '''
        * Waits for the element with the ID of [ID] to appear, then
        * clicks on it.
        * 
        * Parameters:
        * - [ID]: string of the elements html id
        * - [loggingIn]: boolean to determine if the driver is on the login page
        * - [d]: the webdriver object
        '''
        if not loggingIn: 
            self.CheckLogin(d)
        self.WaitFor(By.ID, ID, loggingIn, d)
        d.find_element(By.ID, ID).click()


    def SendKeys(self, ID: str, sentString: str, loggingIn: bool, d: webdriver.Firefox) -> None:
        '''
        * Clears the selected text field, then sends the value of 
        * [sentString] into the field.
        *
        * Parameters:
        * - [ID]: string of the fields html id
        * - [sentString]: the string of keys that will be input into the field
        * - [loggingIn]: boolean to determine if the driver is on the login page
        * - [d]: the webdriver object
        '''
        self.WaitFor(By.ID, ID, loggingIn, d)
        field = d.find_element(By.ID, ID)
        key = Keys.CONTROL

        # If a mac computer, change CTRL to CMD
        if (self.os == "Darwin"):
            key = Keys.COMMAND

        field.send_keys(key, "a")
        field.send_keys(sentString)


    def ClickFromClass(self, className: str, targetText: str, loggingIn: bool, d: webdriver.Firefox) -> None:
        '''
        * This is a helper function to make it easier to target an HTML
        * element that does not have an ID. It uses the className, then 
        * targets the specific element based on its innerText (targetText).
        * 
        * Parameters:
        * - [className]: string for elements class name to sort through
        * - [targetText]: string for the html innertext that will identify the element
        * - [loggingIn]: boolean to determine if the driver is on the login page
        * - [d]: the webdriver object
        '''
        if not loggingIn:
            self.CheckLogin(d)

        collection = self.GetClassListElements(className, loggingIn, d)
        
        for e in collection:
            if e.text == targetText:
                print("Clicking on", targetText)
                e.click()
                break
    

    def GetClassListElements(self, className: str, loggingIn: bool, d: webdriver.Firefox):
        '''
        * This method returns a list of all elements that have the
        * specified class name.
        * 
        * Parameters:
        * - [className]: string for the elements class name that will be sorted through
        * - [loggingIn]: boolean to determine if the driver is on the login page
        * - [d]: the webdriver object
        '''
        if not loggingIn:
            self.CheckLogin(d)

        self.WaitFor(By.CLASS_NAME, className, loggingIn, d)
        collection = d.find_elements(By.CLASS_NAME, className)
        return collection


    def CheckIfElementExists(self, selectorType, selectorName: str, loggingIn: bool, d: webdriver.Firefox) -> bool:
        '''
        * This method returns True if the specified html element exists on the 
        * page, and returns False if it does not.
        *
        * This method is called in CheckLogin(), so CheckLogin() must be called
        * before this method is called, to prevent recursion loop.
        *
        * Paramters:
        * - [selectorType]: uses the selenium "By" type. Ex) ID would be: [By.ID]
        * - [selectorName]: string for ID or Class name
        * - [loggingIn]: boolean to determine if the driver is on the login page
        * - [d]: the webdriver object
        '''
        exists = False

        if not loggingIn:
            self.CheckLogin(d) 

        try:
            d.find_element(selectorType, selectorName)
            print(f'"{selectorName}" found!')
            exists = True
        except NoSuchElementException:
            print(f'"{selectorName}" not found...')
            time.sleep(1)
        
        return exists


    def WaitFor(self, selectorType, selectorName: str, loggingIn: bool, d: webdriver.Firefox) -> None:
        '''
        * Will halt web driver automation until a certain element
        * has loaded into the DOM.
        *
        * Parameters:
        * - [selectorType]: uses the selenium "By" type. Ex) ID would be: [By.ID]
        * - [selectorName]: string for ID or Class name
        * - [loggingIn]: boolean to determine if the driver is on the login page
        * - [d]: the webdriver object
        '''
        while True:
            if not loggingIn:
                self.CheckLogin(d)

            if (self.CheckIfElementExists(selectorType, selectorName, loggingIn, d)):
                return
            else:
                print(f"Searching for {selectorName}")
                continue


    def WaitToBeClickable(self, selectorType, selectorName: str, loggingIn: bool,  d: webdriver.Firefox) -> None:
        '''
        * Will halt web driver automation until a certain element
        * is able to be clicked.
        *
        * Parameters:
        * - [selectorType]: uses the selenium "By" type. Ex) ID would be: [By.ID]
        * - [selectorName]: string for ID or Class name
        * - [loggingIn]: boolean to determine if the driver is on the login page
        * - [d]: the webdriver object
        ''' 
        while True:
            time.sleep(1)
            if not loggingIn:
                self.CheckLogin(d) 

            try:
                element = d.find_element(selectorType, selectorName)
                d.execute_script("arguments[0].scrollIntoView(true);", element)
                element.click()

                print(f"{selectorName} clicked!")
                return
            except ElementClickInterceptedException:
                print(f"{selectorName} not yet clickable...")

    
    def CheckLogin(self, d: webdriver.Firefox) -> bool:
        '''
        * Checks the window to see if the login page has popped up. If it has,
        * then it will log the user in. If not, it will continue as normal.
        * This should be called before any action is performed so that the 
        * driver will stay logged in as long as possible.
        *
        * Parameters:
        * - [d]: the webdriver object
        ''' 
        if (self.CheckIfElementExists(By.ID, "usernameField", True, d)):
            print("Logging in...") 
            self.LoginCRM(d)
            print("Logged in!")
            return True 
        return False
        