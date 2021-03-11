"""
Webscraping script for canada computers
"""
import argparse
from dataclasses import dataclass
from email.message import EmailMessage
from time import sleep
from smtplib import SMTP_SSL
from bs4 import BeautifulSoup
import requests


@dataclass
class HtmlTag:
    name_tag: str
    class_tag: str


def find_item_status(
        item_url: str, availability_tag: HtmlTag, unavailable_status: str, item_tag: HtmlTag
):
    """
    Finds the availability status of the item
    Returns False when unavailable, else True, meaning you can order anywhere
    """
    page = requests.get(item_url).text
    parsed_page = BeautifulSoup(page, "lxml")
    availability = search_page(parsed_page, availability_tag).casefold()
    item_name = search_page(parsed_page, item_tag)
    return True if unavailable_status.casefold() not in availability else False, item_name


def search_page(parsed_page: BeautifulSoup, tag: HtmlTag):
    return parsed_page.find(tag.name_tag, class_=tag.class_tag).text


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
    available_tag = HtmlTag("div", "pi-prod-availability")
    item_tag = HtmlTag("h1", "h3 mb-0")
    unavailable_status = "Not Available Online"

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
            args.item_url, available_tag, unavailable_status, item_tag
        )
        print(success)

    send_notification_to_self(args.email, args.password, item_name)


if __name__ == "__main__":
    main()
