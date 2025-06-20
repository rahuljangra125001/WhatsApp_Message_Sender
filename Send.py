import tkinter as tk
import os
from tkinter import messagebox, Text, filedialog
import pandas as pd
import time
import datetime
from tkinter import ttk
import random
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
image_path = None
base_url = "https://web.whatsapp.com"
driver = None

# Validate phone number
def validate_phone_number(phone):
    if not phone.startswith("+"):
        phone = "+91" + phone
    return phone if phone[1:].isdigit() and len(phone) >= 12 else None

# Load contacts
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
                messagebox.showerror("Error", "Unsupported file format.")
                return
            if contacts_df.shape[1] < 2:
                messagebox.showerror("Error", "File must have at least two columns: Name and Phone.")
                return
            messagebox.showinfo("Success", "Contacts loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file. Error: {e}")
    else:
        messagebox.showwarning("Warning", "No file selected.")

# Select image
def select_image():
    global image_path
    image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if image_path:
        image_label.config(text=f"Selected image: {os.path.basename(image_path)}")
    else:
        image_label.config(text="No image selected")

# Generate personalized message
def generate_advanced_message(name, base_message):
    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting = f"Good morning {name} ji,"
    elif hour < 18:
        greeting = f"Good afternoon {name} ji,"
    else:
        greeting = f"Good evening {name} ji,"
    sign_off = f"Thanks for your valuable time {name} ji."
    return f"{greeting}\n{base_message.strip()}\n{sign_off}"

# Initialize browser
def initialize_driver():
    global driver
    service = Service('./chromedriver.exe')  # Update path if necessary
    options = Options()
    options.add_argument("user-data-dir=C:/Users/rjang/AppData/Local/Google/Chrome/User Data")
    options.add_argument("profile-directory=Default")
    driver = uc.Chrome(service=service, options=options)
    driver.get(base_url)
    time.sleep(10)

# Send WhatsApp message
def send_whatsapp_message(phone_number, message_body, image_path=None):
    global driver
    try:
        # Handle image
        if image_path:
            try:
                driver.get(f"{base_url}/send?phone={phone_number}&text&app_absent=0")
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
                )
                time.sleep(random.uniform(8, 10))

                attach_btn = driver.find_element(By.XPATH, '//span[@data-icon="plus"]')
                attach_btn.click()
                time.sleep(1)

                file_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
                )
                file_input.send_keys(os.path.abspath(image_path))

                

                # Wait for the caption input box to appear
                caption_box = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="undefined"]'))
                )

                caption_box.click()

                # Type the message line by line into the caption box
                for line in message_body.strip().split('\n'):
                    caption_box.send_keys(line)
                    ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()

                time.sleep(1)

                caption_box.send_keys(Keys.ENTER)


                # # Find and click the send button for media
                # send_btn = WebDriverWait(driver, 10).until(
                #     EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                # )
                # send_btn.click()


            except Exception as e:
                print(f"[Image Error] {e}")

            return True
        else:
            driver.get(f"{base_url}/send?phone={phone_number}&text&app_absent=0")
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
            )
            time.sleep(random.uniform(8, 10))

            message_box = driver.find_element(By.XPATH, '//div[@data-tab="10"]')
            message_box.click()

            # Type message line by line
            for line in message_body.strip().split('\n'):
                message_box.send_keys(line)
                ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()

            time.sleep(1)
            # Press Enter to send message
            message_box.send_keys(Keys.ENTER)
            time.sleep(2)

        

    except TimeoutException:
        return "Timeout while trying to send."
    except Exception as e:
        return f"Exception: {e}"

# Main message sending loop
def send_messages():
    global contacts_df, driver
    if contacts_df is None:
        messagebox.showerror("Error", "No contacts loaded.")
        return

    if driver is None:
        initialize_driver()

    base_msg = message_text.get("1.0", tk.END).strip()
    if not base_msg:
        messagebox.showwarning("Warning", "Please enter a message.")
        return

    log = []
    success_count = 0

    for i, row in contacts_df.iterrows():
        name = str(row[0])
        phone = str(row[1])

        phone_number = validate_phone_number(phone)
        if not phone_number:
            log.append(f"❌ Invalid number for {name} ({phone})")
            continue

        personalized_msg = generate_advanced_message(name, base_msg)
        print(f"\n📨 Sending to {name} ({phone_number})\nMessage:\n{personalized_msg}")
        if image_path:
            print(f"📷 Attaching image: {image_path}")

        result = send_whatsapp_message(phone_number, personalized_msg, image_path)

        if result is True:
            success_count += 1
            log.append(f"✅ Sent to {name} ({phone_number})")
        else:
            log.append(f"❌ Failed for {name} ({phone_number}): {result}")

        progress_var.set((i + 1) / len(contacts_df) * 100)
        progress_bar.update()
        time.sleep(random.uniform(4, 6))

        if (i + 1) % 100 == 0:
            print("🛑 Pausing to avoid ban...")
            time.sleep(random.uniform(1800, 2700))

    messagebox.showinfo("Done", f"Messages sent: {success_count}/{len(contacts_df)}")
    with open("message_log.txt", "w") as f:
        f.write("\n".join(log))

    if driver:
        driver.quit()
        driver = None

# GUI setup
root = tk.Tk()
root.title("WhatsApp Campaign Message Sender")
root.geometry("600x600")

frame = tk.Frame(root)
frame.pack(pady=20)

tk.Label(frame, text="Enter your message:").pack()

message_text = Text(frame, height=5, width=50)
message_text.pack()

tk.Button(frame, text="Load Contacts", command=load_contacts).pack(pady=10)
tk.Button(frame, text="Select Image (Optional)", command=select_image).pack(pady=10)

image_label = tk.Label(frame, text="No image selected")
image_label.pack()

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=20)

tk.Button(root, text="Send Messages", command=send_messages).pack(pady=10)

root.mainloop()
