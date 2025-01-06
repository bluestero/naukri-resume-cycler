import sys
import json
from time import sleep
from pathlib import Path
from itertools import cycle
from traceback import print_exc
from dotenv import dotenv_values
from botasaurus_driver import Wait, Driver

#-Custom imports-#
sys.path.insert(0, Path(__file__).parent)
import utils


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

        #-Creating the logger object-#
        self.logger = utils.LogManager("nrc", debug = self.config["debug"])


    #-Function to initialize the driver and log in to the Naukri account-#
    def __login(self) -> None:

        #-Navigating to the login page-#
        self.logger.debug("Navigating to the login page.")
        self.driver.google_get(self.config["login_page"], wait = Wait.SHORT)

        #-Finding and filling the username field-#
        self.logger.debug("Finding the email input.")
        email_input = self.driver.get_element_containing_text("usernameField")
        email_input.type(self.env_file.get("USERNAME"))

        #-Finding and filling the password field-#
        self.logger.debug("Finding the password input.")
        password_input = self.driver.get_element_containing_text("passwordField")
        password_input.type(self.env_file.get("PASSWORD"))

        #-Finding and clicking the submit button-#
        self.logger.debug("Finding the login button.")
        login_button = self.driver.get_element_containing_text("waves-effect waves-light btn-large btn-block btn-bold blue-btn textTransform")
        login_button.click()

        #-Waiting for the homepage redirect-#
        self.logger.debug("Waiting for the homepage reload.")
        self.driver.sleep(3)


    #-Function to update the resume in the profile page-#
    def __update_resume(self) -> None:

        #-Navigating to the profile page-#
        self.logger.debug("Navigating to the profile page.")
        self.driver.google_get(self.config["profile_page"], wait = Wait.SHORT)

        #-Finding the upload resume button and uploading the next resume in cycle-#
        self.logger.debug("Finding the upload resume button.")
        file_input = self.driver.get_element_containing_text("attachCV", type = "input")
        file_input.upload_file(self.current_resume)

        #-Adding some interval to upload and update the resume-#
        self.logger.debug("Waiting for the resume to be uploaded and updated.")
        self.driver.sleep(Wait.SHORT)


    #-Function to cycle and update the resume in the profile page-#
    def cycle_resumes(self) -> None:

        #-Try block to handle exceptions-#
        try:

            #-Counter for the iterations-#
            counter = 1

            #-Logging the start-#
            self.logger.info("Script started.\n")

            #-Logging the available resume-#
            self.logger.info(f"Provided resumes:")

            #-Iterating the resumes and logging them-#
            for index, resume in enumerate(self.config["resume_files"]):

                #-Logging with a breakline if its the last iteration-#
                if index + 1 == len(self.config["resume_files"]):
                    self.logger.info(f"- {resume}\n")

                #-Else logging without any breaklines-#
                else:
                    self.logger.info(f"- {resume}")

            #-Creating an infinite loop-#
            while True:

                #-Getting the next resume and logging it-#
                self.current_resume = self.resume_generator.__next__()
                self.logger.info(f"Iteration number: {counter}.")
                self.logger.info(f"Current resume: {self.current_resume}.\n")

                #-Initializing the driver object-#
                self.driver = Driver()

                #-Logging in to the Naukri account-#
                self.logger.info("Logging in to the account.")
                self.__login()
                self.logger.info("Login successful.\n")

                #-Updating the resume through in the profile page-#
                self.logger.info("Updating the resume in the profile page.")
                self.__update_resume()
                self.logger.info("Resume updated successfully.\n")

                #-Closing the driver to avoid any potential memory issues-#
                self.logger.debug("Closing the driver.")
                self.driver.close()

                #-Adding an interval in seconds-#
                self.logger.info(f"Sleeping for {self.config["interval"]} seconds.\n\n{'-' * 120}\n")
                sleep(self.config["interval"])

                #-Incrementing the counter-#
                counter = counter + 1

        #-Printing the exception-#
        except:
            self.logger.error("", exc_info = True)

        #-Showing script completed and archiving the logs-#
        finally:
            self.logger.info("Script run completed.")
            self.logger.archive_logs(log_rotation = 30)


#-Safeguarding the code from import-#
if __name__ == "__main__":

    #-Creating the class object-#
    nrc = NaukriResumeCycler()
    nrc.cycle_resumes()
