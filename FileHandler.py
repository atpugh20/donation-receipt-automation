class FileHandler:
    def __init__(self):
        self.filePath = "./data/number.txt"
        self.iterator = 0


    def SaveFile(self) -> None:
        '''
        * This method saves the iterator into a text file. This iterator
        * is used to identify which email number we are currently on. 
        '''
        try:
            with open(self.filePath, 'w') as f:
                f.write(str(self.iterator))
                print(f"Iterator ({self.iterator}) successfully saved to {self.filePath}")
        except IOError as e:
            print(f"Error saving file: {e}")
        

    def LoadFile(self) -> bool:
        '''
        * This method loads the iterator from a tet file. The iterator
        * is used to identify which email number we are currently on.
        '''
        try:
            with open(self.filePath, "r") as f:
                self.iterator = int(f.readline())
                return True
        except FileNotFoundError:
            print(f"File not found at {self.filePath}")
            self.SaveFile()
        except ValueError:
            print(f"No value found in {self.filePath}")
            self.SaveFile()
            