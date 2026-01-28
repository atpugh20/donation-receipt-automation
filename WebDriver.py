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


    def OpenCRM(self, d: webdriver.Firefox) -> None:
        '''
        * This method logs in the driver and navigates to the proper page
        * to start the main loop. 
        * 
        * Parameters:
        * - [d]: the webdriver object
        '''
        d.get(self.crmURL)
        print(self.password)
        self.SendKeys("usernameField", self.username, d)
        self.SendKeys("passwordField", self.password, d)
        self.ClickID("login-submit", d)


    def NavigateToExport(self, d: webdriver.Firefox) -> None:
        '''
        * This method logs in the driver to the CRM then navigates to the
        * Fundraising export page.
        *
        * Parameters:
        * - [d]: the webdriver object
        '''
        d.get(self.fundraisingURL)
        self.ClickFromClass("ui-primary-color", "Confirm", d)
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
        self.ClickID("email-copy-button", d)
        d.switch_to.window(d.window_handles[1])
        self.ClickID("edit-email-name-btn", d)
        self.emailNumberName = self.emailName + "_" + str(emailNum)
        self.SendKeys("email-title-input", self.emailNumberName + Keys.ENTER, d)
        self.ClickID("recipients-tab", d)
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
        self.WaitToBeClickable(By.CLASS_NAME, "btn-refresh", d)
        time.sleep(2)

        # Check to see if there are any new donors
        if (self.CheckIfElementExists(By.CLASS_NAME, "summary-row", d)):
            print("Donors found!")
            self.ClickID("email-save-and-button", d)
            self.ClickID("email-save-and-button-0", d)
            self.ClickID("send-bee", d)

            sendMenuElements = d.find_elements(By.CSS_SELECTOR, ".dropdown-menu > li")

            # Check to see if these contacts are able to receive this email
            if (len(sendMenuElements) > 1):
                # Send email
                print("Can send!")
                sendMenuElements[0].click()
                self.ClickFromClass("btn-success", "Yes", d)
                # Close window and refresh page
                d.close()
                d.switch_to.window(d.window_handles[0])
                self.emailPrepped = False
                d.refresh()
            else:
                # Return to donor table screen
                print("Cannot send email...")
                self.ClickFromClass("btn ", "Make Changes", d)
                self.ClickID("recipients-tab", d)

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
        self.ClickFromClass("border-solid", "Export", d)
        self.ClickID("dialog__decline", d)
        print("Export completed!")


    def DeactivateEmail(self, d: webdriver.Firefox) -> bool:
        emailDeactivated = False

        d.get(self.crmURL + "/Mailing/Email/Template/")
        
        # Get all rows
        rows = self.GetClassListElements("data-grid-row", d)

        # Get row that has the right name
        print("Searching rows for email...")
        for row in rows:
            name = row.find_element(By.CLASS_NAME, "email-name-data").text

            # Deactivate that email with name
            if name == self.emailNumberName:
                print(f"Found {self.emailNumberName}!")
                time.sleep(1)
                row.find_element(By.CLASS_NAME, "MuiButtonBase-root").click()
                self.ClickID("toggle-email-menu-action", d)
                emailDeactivated = True
            else:
                print(f"Could not find {self.emailNumberName}")
        
        return emailDeactivated


    def ClickID(self, ID: str, d: webdriver.Firefox) -> None:
        '''
        * Waits for the element with the ID of [ID] to appear, then
        * clicks on it.
        * 
        * Parameters:
        * - [ID]: string of the elements html id
        * - [d]: the webdriver object
        '''
        self.WaitFor(By.ID, ID, d)
        d.find_element(By.ID, ID).click()


    def SendKeys(self, ID: str, sentString: str, d: webdriver.Firefox) -> None:
        '''
        * Clears the selected text field, then sends the value of 
        * [sentString] into the field.
        *
        * Parameters:
        * - [ID]: string of the fields html id
        * - [sentString]: the string of keys that will be input into the field
        * - [d]: the webdriver object
        '''
        self.WaitFor(By.ID, ID, d)
        field = d.find_element(By.ID, ID)
        key = Keys.CONTROL

        # If a mac computer, change CTRL to CMD
        if (self.os == "Darwin"):
            key = Keys.COMMAND

        field.send_keys(key, "a")
        field.send_keys(sentString)


    def ClickFromClass(self, className: str, targetText: str, d: webdriver.Firefox) -> None:
        '''
        * This is a helper function to make it easier to target an HTML
        * element that does not have an ID. It uses the className, then 
        * targets the specific element based on its innerText (targetText).
        * 
        * Parameters:
        * - [className]: string for elements class name to sort through
        * - [targetText]: string for the html innertext that will identify the element
        * - [d]: the webdriver object
        '''
        collection = self.GetClassListElements(className, d)
        
        for e in collection:
            if e.text == targetText:
                print("Clicking on", targetText)
                e.click()
                break
    

    def GetClassListElements(self, className: str, d: webdriver.Firefox):
        '''
        * This method returns a list of all elements that have the
        * specified class name.
        * 
        * Parameters:
        * - [className]: string for the elements class name that will be sorted through
        * - [d]: the webdriver object
        '''
        self.WaitFor(By.CLASS_NAME, className, d)
        collection = d.find_elements(By.CLASS_NAME, className)
        return collection


    def CheckIfElementExists(self, selectorType, selectorName: str, d: webdriver.Firefox) -> bool:
        '''
        * This method returns True if the specified html element exists on the 
        * page, and returns False if it does not.
        *
        * Paramters:
        * - [selectorType]: uses the selenium "By" type. Ex) ID would be: [By.ID]
        * - [selectorName]: string for ID or Class name
        * - [d]: the webdriver object
        '''
        exists = False
        try:
            d.find_element(selectorType, selectorName)
            print(f'"{selectorName}" found!')
            exists = True
        except NoSuchElementException:
            print(f'"{selectorName}" not found...')
            time.sleep(1)
        
        return exists


    def WaitFor(self, selectorType, selectorName: str, d: webdriver.Firefox) -> None:
        '''
        * Will halt web driver automation until a certain element
        * has loaded into the DOM.
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


    def WaitToBeClickable(self, selectorType, selectorName: str, d: webdriver.Firefox) -> None:
        '''
        * Will halt web driver automation until a certain element
        * is able to be clicked.
        *
        * Parameters:
        * - [selectorType]: uses the selenium "By" type. Ex) ID would be: [By.ID]
        * - [selectorName]: string for ID or Class name
        * - [d]: the webdriver object
        ''' 
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