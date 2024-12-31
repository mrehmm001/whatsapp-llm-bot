from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from openai import OpenAI
import os
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
name = os.getenv("NAME")


def get_response(message):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "developer",
                "content": f"You are a chatbot named {name}. You should respond to the following messages.",
            },
            {"role": "user", "content": message},
        ],
    )
    return completion.choices[0].message.content


def open_whatsapp():
    driver = webdriver.Chrome()
    driver.get("https://web.whatsapp.com/")
    return driver


def get_recent_message(driver):
    # All messages have the class ._amk6 we just need to get the last one
    messages = driver.find_elements(By.CLASS_NAME, "_amk6")
    last_message = messages[-1]
    return last_message.text


def send_message(driver, message):
    # Find input box that has aria-placeholder="Type a message" property
    elem = driver.find_element(By.CSS_SELECTOR, '[aria-placeholder="Type a message"]')
    elem.send_keys(message)
    elem.send_keys(Keys.RETURN)


def main():
    message_set = set()
    driver = open_whatsapp()
    # give time for me to scan the QR code and select chat
    # we need an infinite loop to keep checking for new messages and send a reply
    while True:
        try:
            message = get_recent_message(driver)
            # Avoid replying to your own messages
            if f"{name}:" in message:
                continue
            if f"@{name.lower()}" in message.lower():
                if message not in message_set:
                    message_set.add(message)
                    response = get_response(message)
                    send_message(driver, f"{name}: " + response)
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(1)  # Wait a bit before retrying


if __name__ == "__main__":
    main()
