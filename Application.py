import time
from WebDriver import WebDriver
from FileHandler import FileHandler


class Application:
    def __init__(self):
        print("Building app...")

        self.usesFundraising = False

        self.wd = WebDriver(self.usesFundraising)
        self.fh = FileHandler()

        print("App built.")

    def Run(self):
        print("Running app...")
        self.fh.LoadFile()

        # Open CRM and Fundraiser
        self.wd.d1.get(self.wd.crmURL)
        self.wd.CheckLogin(self.wd.d1)

        if self.usesFundraising:
            self.wd.d2.get(self.wd.crmURL)
            self.wd.CheckLogin(self.wd.d2)
            self.wd.NavigateToExport(self.wd.d2)

        # Main loop
        while True:
            print("Looping...")

            # If the email is not prepped, then prep it
            if not self.wd.emailPrepped:
                self.wd.NavigateToEmailSend(self.fh.iterator, self.wd.d1)

            # Refresh Exports            
            if self.usesFundraising:
                self.wd.ExportDontations(self.wd.d2)

            # Check if the emails can be sent
            self.wd.SendReceipts(self.wd.d1)

            # If the email was sent, iterate email number, then deactivate email
            if not self.wd.emailPrepped:
                self.fh.iterator += 1
                self.fh.SaveFile()

                if self.wd.DeactivateEmail(self.wd.d1):
                    print(f"{self.wd.emailNumberName} deactivated!")
                else:
                    print(f"{self.wd.emailNumberName} failed to deactivate")
                    break

            time.sleep(60)  # Wait one minute before looping again

        # Out of the main loop 
        print("App completed running.") 