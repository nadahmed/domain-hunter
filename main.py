import os
import smtplib
from email.message import EmailMessage

import requests

DOMAINS = (domain.strip().lower() for domain in os.environ.get("DOMAINS", "").split(","))

def is_available(domain: str) -> bool:
    # rdap.org automatically redirects to the authoritative registry for the TLD
    res = requests.get(f"https://rdap.org/domain/{domain}", timeout=10)
    # 404 Not Found in RDAP indicates the domain is unregistered
    return res.status_code == 404

def send_email(available_domains: list[str]):
    msg = EmailMessage()
    msg["Subject"] = f"Domain Available: {', '.join(available_domains)}"
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["ALERT_EMAIL"]
    msg.set_content("The following domains are now available:\n\n" + "\n".join(available_domains))

    with smtplib.SMTP_SSL(os.environ["SMTP_HOST"], 465) as smtp:
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        smtp.send_message(msg)

if __name__ == "__main__":
    found = [d for d in DOMAINS if is_available(d)]
    if found:
        send_email(found)