import tkinter as tk
from tkinter import messagebox, Text, filedialog
import pandas as pd
import time
import datetime
from tkinter import ttk
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

# Global variables
contacts_df = None
driver = None

# Emojis and message variations for personalization
emojis = ['😊', '🙂', '✨', '👍', '🙏', '🙌', '😄', '🌟', '🤝']
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
    varied_message = base_message
    for pattern, replacements in message_variations.items():
        varied_message = re.sub(pattern, random.choice(replacements), varied_message, flags=re.IGNORECASE)

    emoji_count = random.randint(1, 3)
    varied_message += " " + " ".join(random.choices(emojis, k=emoji_count))

    # Random sign-offs
    sign_offs = ["Best regards,", "Cheers,", "Thanks again,", "Kind regards,"]
    signature = random.choice(sign_offs) + f" {name}"

    return f"{greeting}\n{varied_message}\n\n{signature}"

# Function to send WhatsApp message using Selenium
def send_whatsapp_message(phone_number, message_body, retries=3):
    try:
        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message_body}"
        driver.get(whatsapp_url)
        time.sleep(random.uniform(15, 25))

        send_button = driver.find_element('xpath', "//div[@role='button'][@data-testid='send']")
        send_button.click()
        time.sleep(random.uniform(15, 30))
        return True
    except Exception as e:
        if retries > 0:
            print(f"Retrying to send message to {phone_number}... ({retries} retries left)")
            time.sleep(random.uniform(10, 20))
            return send_whatsapp_message(phone_number, message_body, retries - 1)
        else:
            print(f"Failed to send message to {phone_number} after retries: {e}")
            return str(e)

# Function to handle smart delays
def smart_delay(message_count, total_messages):
    if message_count % 100 == 0:  # Longer break after every 100 messages
        delay_time = random.uniform(10 * 60, 20 * 60)  # 10 to 20 minutes
    else:
        delay_time = random.uniform(30, 60)  # Regular delay between 30 and 60 seconds

    print(f"Pausing for {delay_time / 60:.2f} minutes...")
    time.sleep(delay_time)

    # Random short pauses
    if random.random() < 0.1:  # 10% chance of a short pause
        short_pause = random.uniform(5, 15)
        print(f"Taking a short pause for {short_pause} seconds...")
        time.sleep(short_pause)

# Function to check for errors and handle reconnection
def check_for_errors():
    try:
        error_elements = driver.find_elements('xpath', "//div[contains(text(), 'Reconnect') or contains(text(), 'logged out')]")
        if error_elements:
            print("Error detected. Trying to reload WhatsApp Web...")
            driver.refresh()
            time.sleep(30)
    except Exception as e:
        print(f"Error checking failed: {e}")

# Function to send messages to all contacts
def send_messages():
    global contacts_df, driver
    if contacts_df is None:
        messagebox.showerror("Error", "No contacts loaded. Please load a contacts file first.")
        return
    
    base_message = message_text.get("1.0", tk.END).strip()
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
        result = send_whatsapp_message(phone_with_code, personalized_message)
        if result is True:
            success_count += 1
            log.append(f"Success: Message sent to {name} ({phone_with_code})")
        else:
            log.append(f"Failed: Could not send message to {name} ({phone_with_code}). Error: {result}")

        progress_var.set((index + 1) / len(contacts_df) * 100)
        progress_bar.update()

        smart_delay(index + 1, len(contacts_df))
        check_for_errors()

        if (index + 1) % 500 == 0:
            stagger_delay = random.uniform(40 * 60, 70 * 60)
            print(f"Sent {index + 1} messages. Pausing for {stagger_delay / 60:.2f} minutes...")
            time.sleep(stagger_delay)

    result_message = f"Messages sent successfully: {success_count}/{len(contacts_df)}"
    messagebox.showinfo("Message Log", result_message)
    with open("message_log.txt", "w") as f:
        f.write("\n".join(log))

# Create the main Tkinter window
root = tk.Tk()
root.title("WhatsApp Campaign Message Sender")
root.geometry("600x500")

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

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=10, fill=tk.X)

# Send button
send_button = tk.Button(frame, text="Send Messages to All Contacts", command=send_messages)
send_button.pack(pady=10)

# Initialize WebDriver
def initialize_driver():
    global driver
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
    driver.get('https://web.whatsapp.com')
    input("Scan the QR code and press Enter to continue...")

# Initialize WhatsApp Web
initialize_driver()

# Run the Tkinter GUI
root.mainloop()
