import time
from WebDriver import WebDriver
from FileHandler import FileHandler


class Application:
    def __init__(self):
        print("Building app...")

        self.webDriver = WebDriver()
        self.fileHandler = FileHandler()

        print("App built.")

    def Run(self):
        print("Running app...")
        self.fileHandler.LoadFile()
        self.webDriver.OpenCRM()

        # Main loop
        while True:
            time.sleep(1)
            self.fileHandler.iterator += 1
            self.fileHandler.SaveFile()

        print("App completed running.") 