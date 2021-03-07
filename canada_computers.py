"""
Webscraping script for canada computers
"""
import argparse
from email.message import EmailMessage
from time import sleep
from bs4 import BeautifulSoup
from smtplib import SMTP_SSL
import requests


def find_item_status(
        item_url: str, available_html_name_tag: str, available_html_class_tag: str
        , unavailable_status: str, item_html_name_tag: str, item_html_class_tag: str
):
    """
    Finds the availability status of the item
    Returns False when unavailable, else True, meaning you can order anywhere
    """
    page = requests.get(item_url).text
    parsed_page = BeautifulSoup(page, "lxml")
    availability = parsed_page.find(available_html_name_tag, class_=available_html_class_tag).text
    item_name = parsed_page.find(item_html_name_tag, class_=item_html_class_tag).text
    return False if unavailable_status in availability else True, item_name


def send_notification_to_self(email: str, password: str, item: str):
    """
    Construct an email and send to email address provided
    """
    msg = EmailMessage()
    msg["Subject"] = "Item available"
    msg["From"] = email
    msg["To"] = email
    msg.set_content(f"{item} is available to order online")

    try:
        with SMTP_SSL("smtp.live.com", 465) as smtp:
            smtp.login(email, password)
            smtp.send_message(msg)
        return True
    except:
        return False


def main():
    AVAILABILITY_HTML_NAME_TAG = "div"
    AVAILABILITY_HTML_CLASS_TAG = "pi-prod-availability"
    UNAVAILABLE_STATUS = "Not Available Online"
    ITEM_HTML_NAME_TAG = "h1"
    ITEM_HTML_CLASS_TAG = "h3 mb-0"

    parser = argparse.ArgumentParser(description="Script to scrape canada computers")
    parser.add_argument("email", help="Email address to send from", type=str)
    parser.add_argument("password", help="Password of the email", type=str)
    parser.add_argument("item_url", help="Url of the item", type=str)
    args = parser.parse_args()

    success = False
    item_name = None
    while not success:
        sleep(60)
        success, item_name = find_item_status(
                args.item_url, AVAILABILITY_HTML_NAME_TAG, AVAILABILITY_HTML_CLASS_TAG
                , UNAVAILABLE_STATUS, ITEM_HTML_NAME_TAG, ITEM_HTML_CLASS_TAG
        )

    send_notification_to_self(args.email, args.password, item_name)


if __name__ == "__main__":
    main()
