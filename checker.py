import requests
from bs4 import BeautifulSoup
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


CHANNEL_NAME = "فری ۱"

CHANNEL_URL = "https://t.me/s/poshtehpardehtv"

STATE_FILE = "last_messages.json"


GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_TO = os.environ.get("GMAIL_TO")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")


headers = {
    "User-Agent": "Mozilla/5.0"
}


def get_messages():

    response = requests.get(
        CHANNEL_URL,
        headers=headers,
        timeout=20
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    messages = soup.find_all(
        "div",
        class_="tgme_widget_message"
    )

    result = []

    for item in messages:

        data_id = item.get(
            "data-post"
        )

        text = item.find(
            "div",
            class_="tgme_widget_message_text"
        )

        if data_id and text:

            message = text.get_text(
                "\n",
                strip=True
            )

            if message:
                result.append(
                    {
                        "id": data_id,
                        "text": message
                    }
                )

    return result



def load_old():

    if os.path.exists(STATE_FILE):

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    return []



def save_old(messages):

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            messages,
            file,
            ensure_ascii=False,
            indent=2
        )



def send_email(message):

    mail = MIMEMultipart()

    mail["From"] = GMAIL_USER

    mail["To"] = GMAIL_TO

    mail["Subject"] = (
        f"پیام جدید از {CHANNEL_NAME}"
    )


    body = f"""
کانال:
{CHANNEL_NAME}


پیام جدید:

--------------------

{message}
"""


    mail.attach(
        MIMEText(
            body,
            "plain",
            "utf-8"
        )
    )


    server = smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    )


    server.login(
        GMAIL_USER,
        GMAIL_APP_PASSWORD
    )


    server.sendmail(
        GMAIL_USER,
        GMAIL_TO,
        mail.as_string()
    )


    server.quit()



new_messages = get_messages()

old_messages = load_old()


old_ids = [
    item["id"]
    for item in old_messages
]


for message in new_messages:

    if message["id"] not in old_ids:

        send_email(
            message["text"]
        )

        old_messages.append(
            message
        )


save_old(
    old_messages[-200:]
)


print(
    "بررسی تمام شد"
)
