import argparse
import httpx
import asyncio
from datetime import datetime
from tqdm import tqdm
from colorama import Fore, Style
import time
import sys
import subprocess
from email.mime.text import MIMEText
from . import apikeys
import sendgrid
import os
from sendgrid.helpers.mail import *

def alert_message(message, subject='URL Outtage Message', me=apikeys.system_email, you=apikeys.admin_email):
	sg = sendgrid.SendGridAPIClient(api_key=apikeys.SENDGRID_API_KEY)
	from_email = Email(me)
	to_email = To(you)
	content = Content("text/plain", message)
	mail = Mail(from_email, to_email, subject, content)
	response = sg.client.mail.send.post(request_body=mail.get())
	print(response.status_code)
	print(response.body)
	print(response.headers)
	return True


CMD = '''
on run argv
  display notification (item 2 of argv) with title (item 1 of argv)
end run
'''

def notify(title, text):
  subprocess.call(['osascript', '-e', CMD, title, text])

# Example uses:
#notify(r'Weird\/|"!@#$%^&*()\ntitle', r'!@#$%^&*()"')

# Banner
BANNER = """
╔═══════════════════════════════╗
║       StatusChecker.py        ║
║   Adapted: Mike iLL MZOO      ║
║   From Tel: @BLACK_SCORP10    ║
╚═══════════════════════════════╝
"""

# Color Codes
COLORS = {
    "1xx": Fore.WHITE,
    "2xx": Fore.GREEN,
    "3xx": Fore.YELLOW,
    "4xx": Fore.RED,
    "5xx": Fore.LIGHTRED_EX,
    "Invalid": Fore.WHITE
}

TIMEOUT = 3600

# Function to check URL status
async def check_url_status(session, url_id, url):
    if "://" not in url:
        url = "https://" + url  # Add https:// if no protocol is specified
    try:
        response = await session.head(url)
        return url_id, url, response.status_code
    except httpx.RequestError:
        return url_id, url, None

"""
Map url to a tuple with two items, 0: failure_level, 1: status
# zero: not failing
# one: one failure
# two: recovered from failure
"""
connection_status = dict(zip([url.split("://")[1] for url in apikeys.url_list], ([x,x] for x in [0] * len(apikeys.url_list))))
# Main function
async def main():

    print(BANNER)

    async with httpx.AsyncClient() as session:
        results = {}
        tasks = [check_url_status(session, url_id, url) for url_id, url in enumerate(apikeys.url_list)]
        if len(apikeys.url_list) >= 1:
            with tqdm(total=len(apikeys.url_list), desc="Checking URLs") as pbar:
                for coro in asyncio.as_completed(tasks):
                    url_id, url, status_code = await coro
                    results[url_id] = (url, status_code)
                    pbar.update(1)
        else:
            print("Add urls to your config list.")

    status_codes = {
        "1xx": [],
        "2xx": [],
        "3xx": [],
        "4xx": [],
        "5xx": [],
        "Invalid": []
    }

    global connection_status
    print(f"\n\n{Fore.CYAN}========== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ({len(apikeys.url_list)} URLs) ========== \n\n{Fore.WHITE}")
    for url_id, (url, status) in results.items():
        if status is not None:
            status_group = str(status)[0] + "xx"
            status_codes[status_group].append((url, status))
        else:
            status_codes["Invalid"].append((url, "Invalid"))
    for code, urls in status_codes.items():
        if urls:
            print(COLORS.get(code, Fore.WHITE) + f'===== {code.upper()} =====')
            for url, status in urls:
              shorturl = url.split("://")[1]
              connection_status[shorturl][1] = status
              if (status != 200):
                  if connection_status[shorturl][0] == 0:
                    connection_status[shorturl][0] = 1
                  elif connection_status[shorturl][0] == 1:
                    notify("URL Down", f"URL: {shorturl} is down with status code {connection_status[shorturl][1]}")
                    alert_message(f"URL: {shorturl} down for more than a minute with status code {connection_status[shorturl][1]}")
                    connection_status[shorturl][0] = 2
              else:
                if connection_status[shorturl][0] == 2:
                    notify("URL Up. Rest easy.", f"URL: {shorturl} is back up with status code {connection_status[shorturl][1]}")
                    alert_message(f"URL Up. Rest easy.: {shorturl} is back up with status code  {connection_status[shorturl][1]}")
                    connection_status[shorturl][0] = 0
                if (connection_status[shorturl][0] == 1): connection_status[shorturl][0] = 2
              print(f'[Status : {status}] = {url}')
            print(Style.RESET_ALL)

if __name__ == "__main__":
    while (1):
        try:
            asyncio.run(main())
            # check sooner if we have any !200 statuses
            time.sleep(60 if any([x[0] for x in connection_status.values()]) else TIMEOUT)
        except KeyboardInterrupt:
            print("\n\nExiting...")
            sys.exit(0)
        except Exception as e:
            print(f"An error occurred: {e}")
            break
