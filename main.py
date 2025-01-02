import json
from time import sleep
from pathlib import Path
from itertools import cycle
from traceback import print_exc
from dotenv import dotenv_values
from botasaurus_driver import Wait, Driver


#-Main class object-#
class NaukriResumeCycler:

    #-Init function for the base initialization-#
    def __init__(self) -> None:

        #-Base objects-#
        self.script_dir = Path(__file__).parent
        self.env_file = dotenv_values(self.script_dir / ".env")

        #-Loading the JSON config file-#
        with open(self.script_dir / "config.json") as file:
            self.config = json.load(file)

        #-Iterator to yield the resume filepaths-#
        self.resume_generator = cycle(self.config["resume_files"])


    #-Function to initialize the driver and log in to the Naukri account-#
    def __login(self) -> None:

        #-Navigating to the login page-#
        self.driver.google_get(self.config["login_page"], wait = Wait.SHORT)

        #-Finding and filling the username field-#
        email_input = self.driver.get_element_containing_text("usernameField")
        email_input.type(self.env_file.get("USERNAME"))

        #-Finding and filling the password field-#
        password_input = self.driver.get_element_containing_text("passwordField")
        password_input.type(self.env_file.get("PASSWORD"))

        #-Finding and clicking the submit button-#
        login_button = self.driver.get_element_containing_text("waves-effect waves-light btn-large btn-block btn-bold blue-btn textTransform")
        login_button.click()

        #-Waiting for the homepage redirect-#
        self.driver.sleep(3)


    #-Function to cycle and update the resume in the profile page-#
    def cycle_resumes(self) -> None:

        #-Try block to handle exceptions-#
        try:

            #-Creating an infinite loop-#
            while True:

                #-Initializing the driver object-#
                self.driver = Driver()

                #-Logging in to the Naukri account-#
                self.__login()

                #-Navigating to the profile page-#
                self.driver.google_get(self.config["profile_page"], wait = Wait.SHORT)

                #-Finding the upload resume button and uploading the next resume in cycle-#
                file_input = self.driver.get_element_containing_text("attachCV", type = "input")
                file_input.upload_file(self.resume_generator.__next__())

                #-Adding some interval to upload and update the resume-#
                self.driver.sleep(Wait.SHORT)

                #-Closing the driver to avoid any potential memory issues-#
                self.driver.close()

                #-Adding an interval in seconds-#
                sleep(self.config["interval"])

        #-Printing the exception-#
        except:
            print_exc()


#-Safeguarding the code from import-#
if __name__ == "__main__":

    #-Creating the class object-#
    nrc = NaukriResumeCycler()
    nrc.cycle_resumes()

