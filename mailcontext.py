""" Mail handling context manager """
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl

class MailContext:
    def __init__(self, smtp_server, port, ssl_enable=True):
        self.smtp_server = smtp_server
        self.port = port
        self.ssl_enable = ssl_enable
        self.connection = None

    def __enter__(self):
        if self.ssl_enable:
            context = ssl.create_default_context()
            self.connection = smtplib.SMTP_SSL(self.smtp_server, self.port, context)
        else:
            self.connection = smtplib.SMTP(self.smtp_server, self.port)
        return self

    def sendmail(self,sender, receiver, subject, message):
        """_summary_

        Args:
            sender (str): sender mail
            receiver (str): receiver mail
            subject (str): mail subject
            message (str): message text
        """
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        self.connection.send_message(msg)

        del msg

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.connection.close()
