import tkinter as tk
import os
from tkinter import messagebox, Text, filedialog
import pandas as pd
import time
import datetime
from tkinter import ttk
import random
import re
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException

# Global variables
contacts_df = None
image_path = None  # To store the selected image path
base_url = "https://web.whatsapp.com"
driver = None  # Global WebDriver variable

# Emojis and message variations for personalization
emojis = ['🙏']
message_variations = {
    r"\bhope\b": ["wish", "trust"],
    r"\bhaving a\b": ["enjoying a", "experiencing a"],
    r"\bgreat day\b": ["wonderful day", "fantastic day"],
    r"\blet me know\b": ["feel free to reach out", "do let me know"],
    r"\bthank you\b": ["thanks a lot", "many thanks"],
    r"\bcatch up soon\b": ["talk to you soon", "connect soon"],
}

# Function to validate phone number
def validate_phone_number(phone):
    if not phone.startswith("+"):
        phone = "+91" + phone
    return phone if phone[1:].isdigit() and len(phone) >= 12 else None

# Function to load contacts from a CSV or Excel file
def load_contacts():
    global contacts_df
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
    if file_path:
        try:
            if file_path.endswith('.csv'):
                contacts_df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                contacts_df = pd.read_excel(file_path)
            else:
                messagebox.showerror("Error", "Unsupported file format. Please upload a CSV or XLSX file.")
                return None

            if contacts_df.shape[1] < 2:
                messagebox.showerror("Error", "File must have at least two columns: Name and Phone number.")
                return None
            messagebox.showinfo("Success", "Contacts loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file. Error: {e}")
            return None
    else:
        messagebox.showwarning("Warning", "No file selected.")
        return None

# Function to select an image to attach
def select_image():
    global image_path
    image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if image_path:
        image_label.config(text=f"Selected image: {image_path}")
    else:
        image_label.config(text="No image selected")

# Function to generate advanced and varied message
def generate_advanced_message(name, base_message):
    # Time-based greetings
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        greeting = f"Good morning {name} ji,"
    elif current_hour < 18:
        greeting = f"Good afternoon {name} ji,"
    else:
        greeting = f"Good evening {name} ji,"

    # Add advanced variations for sentence structure and emojis
    varied_message = str(base_message)
    # for pattern, replacements in message_variations.items():
    #     varied_message = re.sub(pattern, random.choice(replacements), varied_message, flags=re.IGNORECASE)

    # emoji_count = random.randint(1, 3)
    # varied_message += " " + " ".join(emojis)

    # Random sign-offs
    sign_offs = f"Thanks for your valuable time {name} Ji"
    signature = sign_offs
    final_m = greeting +'\n'+ varied_message +'\n'+ signature  
    return final_m

# Function to initialize the WebDriver
def initialize_driver():
    global driver
    service = Service('./chromedriver.exe')
    options = Options()
    options.add_argument("user-data-dir=C:/Users/rjang/AppData/Local/Google/Chrome/User Data")
    options.add_argument("profile-directory=Default")
    
    driver = uc.Chrome(service=service, options=options)
    driver.get(base_url)
    time.sleep(random.uniform(8, 10))  # Allow time for WhatsApp Web to load

# Modified send_whatsapp_message function
def send_whatsapp_message(phone_number,message_body,  image_path=None):
    global driver  # Use the global driver variable
    try:
        same_tab_url = f"{base_url}/send?phone={phone_number}&text={message_body}"
        driver.get(same_tab_url)
        time.sleep(random.uniform(8, 10))  # Allow time for the message box to load

        # Wait until the message input is available
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//div[@contenteditable="true"]')))
        time.sleep(2)
        # Find and click the attachment button
        attachment_button = driver.find_element(By.XPATH, '//div[@title="Attach"]')
        attachment_button.click()

        # Find the input for image/video files and send the image file
        image_box = driver.find_element(By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
        image_box.send_keys(os.path.abspath(image_path))  # Use absolute path for the image file

        time.sleep(3)  # Adjust this based on the image upload time
        
        # message_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"]')
        # message_box.click()
        # print(message_body)
        # for line in message_body.split('\n'):
        #         ActionChains(driver).send_keys(line).perform()
        #         ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).perform()
        # print('Success')
        # time.sleep(random.uniform(4, 7))

        # Wait for the send button to appear and click it
        send_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]')))
        send_button.click()

        time.sleep(random.uniform(20, 25))  # Wait for the message to send

        return True  # Return success

    except TimeoutException:
        return "Failed: Timeout occurred while trying to send the message."
    except Exception as e:
        return f"An error occurred: {e}"

# Function to send messages to all contacts
def send_messages():
    global contacts_df, driver
    if contacts_df is None:
        messagebox.showerror("Error", "No contacts loaded. Please load a contacts file first.")
        return

    # Initialize the driver
    if driver is None:
        initialize_driver()

    base_message = message_text.get("1.0", tk.END)
    if not base_message:
        messagebox.showwarning("Warning", "Please enter a message before sending.")
        return

    log = []
    success_count = 0

    for index in range(len(contacts_df)):
        name = contacts_df.iloc[index, 0]
        phone = contacts_df.iloc[index, 1]

        phone_with_code = validate_phone_number(str(phone))
        if phone_with_code is None:
            log.append(f"Failed: Invalid phone number for {name} ({phone}).")
            continue

        personalized_message = generate_advanced_message(name, base_message)
        result = send_whatsapp_message(phone_with_code,personalized_message,  image_path)
        if result is True:
            success_count += 1
            log.append(f"Success: Message sent to {name} ({phone_with_code})")
        else:
            log.append(f"Failed: Could not send message to {name} ({phone_with_code}). Error: {result}")

        progress_var.set((index + 1) / len(contacts_df) * 100)
        progress_bar.update()

        # Short pause after every message (optional for user experience)
        time.sleep(random.uniform(4, 7))

        if (index + 1) % 100 == 0:
            print("Pausing for 30-45 minutes...")
            time.sleep(random.uniform(1800, 2700)) 

    result_message = f"Messages sent successfully: {success_count}/{len(contacts_df)}"
    messagebox.showinfo("Message Log", result_message)
    with open("message_log.txt", "w") as f:
        f.write("\n".join(log))

    # Close the driver after sending all messages
    if driver:
        driver.quit()
        driver = None  # Reset driver

# Create the main Tkinter window
root = tk.Tk()
root.title("WhatsApp Campaign Message Sender")
root.geometry("600x600")

# Frame for inputs
frame = tk.Frame(root)
frame.pack(pady=20)

# Message input
message_label = tk.Label(frame, text="Enter your message:")
message_label.pack()

message_text = Text(frame, height=5, width=50)
message_text.pack()

# Button to load contacts
load_button = tk.Button(frame, text="Load Contacts", command=load_contacts)
load_button.pack(pady=10)

# Button to select an image
image_button = tk.Button(frame, text="Select Image (Optional)", command=select_image)
image_button.pack(pady=10)

# Label to show selected image
image_label = tk.Label(frame, text="No image selected")
image_label.pack()

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=20)

# Button to send messages
send_button = tk.Button(root, text="Send Messages", command=send_messages)
send_button.pack(pady=10)

root.mainloop()
