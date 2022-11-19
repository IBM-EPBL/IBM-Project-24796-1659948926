import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

message = Mail(
    from_email='ajithtony@student.tce.edu',
    to_emails='ajithtony@student.tce.edu',
    subject='Containment Zone ',
    html_content='<strong> Alert!! You are currently entering a Containment Zone. Please turn back immediately </strong>')
try:
    sg = SendGridAPIClient("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")
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)