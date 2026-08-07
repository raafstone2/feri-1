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

        message_id = item.get(
            "data-post"
        )

        text = item.find(
            "div",
            class_="tgme_widget_message_text"
        )

        if message_id and text:

            message_text = text.get_text(
                "\n",
                strip=True
            )

            if message_text:

                result.append(
                    {
                        "id": message_id,
                        "text": message_text
                    }
                )

    return result



def load_state():

    if os.path.exists(STATE_FILE):

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    return []



def save_state(messages):

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



def send_email(messages):

    mail = MIMEMultipart()

    mail["From"] = GMAIL_USER

    mail["To"] = GMAIL_TO

    mail["Subject"] = (
        f"{len(messages)} پیام جدید از {CHANNEL_NAME}"
    )


    body = f"""
کانال:
{CHANNEL_NAME}


تعداد پیام‌های جدید:
{len(messages)}


====================

"""


    for index, message in enumerate(
        messages,
        start=1
    ):

        body += f"""

پیام شماره {index}

--------------------

{message}

====================

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

old_messages = load_state()


old_ids = {
    item["id"]
    for item in old_messages
}


messages_to_send = []


for message in new_messages:

    if message["id"] not in old_ids:

        messages_to_send.append(
            message["text"]
        )

        old_messages.append(
            message
        )


if messages_to_send:

    send_email(
        messages_to_send
    )


save_state(
    old_messages[-500:]
)


print(
    "بررسی تمام شد"
)
