from WebDriver import WebDriver

class Application:
    def __init__(self):
        print("Building app...")

        self.webDriver = WebDriver()

        print("App build.")

    def Run(self):
        print("Running app...")

        self.webDriver.OpenCRM()

        print("App completed running.") 