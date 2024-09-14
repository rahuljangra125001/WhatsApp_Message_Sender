# WhatsApp Campaign Message Sender

## Overview

The WhatsApp Campaign Message Sender is a Python application designed for sending personalized WhatsApp messages to a list of contacts using WhatsApp Web. It employs automation tools like Selenium and undetected-chromedriver to streamline the messaging process.

## Prerequisites

- **Python**: Ensure Python 3.6 or higher is installed. Download from [python.org](https://www.python.org/downloads/).
- **Google Chrome**: The application uses Google Chrome for automation. Make sure you have the latest version installed.
- **Required Python Packages**: The application relies on several Python libraries, which need to be installed via pip.

## Installation Instructions

1. **Download and Install Python**:
   - Download the latest version of Python from [python.org](https://www.python.org/downloads/).
   - Follow the installation instructions, and ensure you check the option to add Python to your system PATH.

2. **Install Required Python Packages**:
   - Open a terminal or command prompt.
   - Install the necessary Python packages by running the following command:
     
     pip install pandas selenium undetected-chromedriver
     
   - This will install `pandas` for data manipulation, `selenium` for browser automation, and `undetected-chromedriver` to handle ChromeDriver detection issues.

3. **Download ChromeDriver**:
   - The `webdriver_manager` package included in the script will handle the ChromeDriver setup automatically.

## Usage Guide

1. **Run the Application**:
   - Open a terminal or command prompt.
   - Navigate to the directory where you have saved the Python script.
   - Execute the script with:
     
     python WhatsApp_Message_Sender.py
    
     

2. **Initialize WebDriver**:
   - The script will open Google Chrome and navigate to WhatsApp Web.
   - Scan the QR code displayed on the screen using the WhatsApp app on your mobile device.
   - After scanning the QR code, press Enter in the terminal or command prompt to proceed.

3. **Load Contacts**:
   - In the application window, click on the "Load Contacts" button.
   - Select a CSV or Excel file containing your contacts. Ensure the file has at least two columns: Name and Phone Number.

4. **Enter Your Message**:
   - Type the message you wish to send in the "Enter your message" text area.
   - You can use predefined placeholders and message variations for personalization.

5. **Send Messages**:
   - Click the "Send Messages to All Contacts" button to start sending messages.
   - Monitor the progress through the progress bar displayed in the application window.

6. **Review Logs**:
   - After the messaging process is complete, check the `message_log.txt` file for detailed logs about each message sent and any errors encountered.

## Advanced Features

- **Personalization**: The application supports personalized messages with variations and emojis to enhance engagement.
- **Smart Delays**: Incorporates intelligent delays and retries to handle sending limits and prevent being flagged for automation.
- **Error Handling**: Includes mechanisms to detect and address common issues like disconnections or message sending failures.

## Troubleshooting

- **Driver Issues**:
  - Ensure that Google Chrome is up-to-date.
  - Verify that no other instances of Chrome are running during the script execution.
  
- **Login Problems**:
  - If you face issues with the QR code or login, try refreshing the page or restarting the script.
  
- **Message Sending Errors**:
  - Check the `message_log.txt` file for detailed error messages and retry sending the message if necessary.
  
- **Contact Loading Errors**:
  - Ensure your CSV or Excel file is properly formatted and contains valid phone numbers.

## License

This software is provided under an open-source license. It is intended for educational and personal use. I disclaims all responsibility for any misuse or damages resulting from the use of this software.
