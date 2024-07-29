import logging
from celery import shared_task
from email_sending.utils import send_email


@shared_task
def send_email_task(subject, message, recipient):
    print(f"Sending email to {recipient} with subject: {subject}")
    send_email(subject, message, recipient)