import requests
from bs4 import BeautifulSoup
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


CHANNEL_NAME = "فری ۱"

CHANNEL_URL = "https://t.me/s/poshtehpardehtv"

LAST_FILE = "last_message.txt"


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

        text = item.find(
            "div",
            class_="tgme_widget_message_text"
        )

        if text:

            message = text.get_text(
                "\n",
                strip=True
            )

            if message:
                result.append(message)

    return result[-20:]



def read_old():

    if os.path.exists(LAST_FILE):

        with open(
            LAST_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read().split(
                "\n---MESSAGE---\n"
            )

    return []



def save_old(messages):

    with open(
        LAST_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n---MESSAGE---\n".join(messages)
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

old_messages = read_old()


for message in new_messages:

    if message not in old_messages:

        send_email(message)

        old_messages.append(
            message
        )


save_old(
    old_messages[-100:]
)


print(
    "بررسی تمام شد"
)
