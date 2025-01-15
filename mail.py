from fasthtml.common import (
    # FastHTML's HTML tags
    Group, Button, Input,
)

from pathlib import Path

from make_app import app, blogs_config, mail_config
rt = app.route

def MailForm(blog):
    blog_config = blogs_config[blog]
    return Group(
                Input(placeholder="Email", type="email", id="email", style="width: 40%"),
                Button(blog_config['email']['subscribe'], hx_post=f"/blogs/{blog}/subscribe", hx_swap="outerHTML", hx_include="#email"),
                Button(blog_config['email']['unsubscribe'], hx_delete=f"blogs/{blog}/unsubscribe", hx_swap="outerHTML", hx_include="#email", cls="outline"),
                style="width: 100%",
            ),

@rt("/blogs/{blog:str}/subscribe")
def post(blog:str, email: str): # to list
    blog_config = blogs_config[blog]
    mailing_list_file = Path(f"mailing_lists/{blog}.txt")
    if not mailing_list_file.exists():
        mailing_list_file.touch()
    
    with mailing_list_file.open("r+") as file:
        emails = file.read().splitlines()
        if email not in emails:
            file.write(email + "\n")
            return Button(blog_config['email']['subscribe_success'], disabled=True)
        else:
            return Button(blog_config['email']['already_subscribed'], disabled=True)

@rt("/blogs/{blog:str}/unsubscribe")
def delete(blog:str, email: str): # from list
    blog_config = blogs_config[blog]
    mailing_list_file = Path(f"mailing_lists/{blog}.txt")
    if not mailing_list_file.exists():
        return blog_config['email']['not_subscribed']
    
    with mailing_list_file.open("r+") as file:
        emails = file.read().splitlines()
        if email in emails:
            emails.remove(email)
            file.seek(0)
            file.truncate()
            file.write("\n".join(emails) + "\n")
            return Button(blog_config['email']['unsubscribe_success'], disabled=True, cls="outline")
        else:
            return Button(blog_config['email']['not_subscribed'], disabled=True, cls="outline")
        

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os

def send_blog_to_subscribers(blog, post_name, html_content, image_paths):
    mailing_list_file = Path(f"mailing_lists/{blog}.txt")
    
    if not mailing_list_file.exists():
        print("Mailing list file does not exist.")
        return
    
    with mailing_list_file.open("r") as file:
        emails = file.read().splitlines()
    # Validate email addresses
    emails = [email for email in emails if email and "@" in email]
    print(f"Emails: {emails}")
    
    sender_email = mail_config['sender']
    smtp_server = mail_config['smtp']['server']
    smtp_port = mail_config['smtp']['port']
    smtp_user = mail_config['smtp']['user']
    smtp_password = os.getenv('SMTP_PASSWORD')
    if not smtp_password:
        print("SMTP_PASSWORD environment variable is not set.")
        return
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = f"New post: {post_name}"
    msg.attach(MIMEText(html_content, 'html'))
    
    for image_path in image_paths:
        with open(image_path, 'rb') as img:
            mime = MIMEImage(img.read(), )#_subtype="jpeg")
            #TODO resize image
            mime.add_header('Content-ID', '<' + image_path + '>') # TODO: Split? so disgegard extension
            msg.attach(mime)
    
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        print("Logged in")
        try:
            for email in emails:
                msg['To'] = email
                server.sendmail(sender_email, email, msg.as_string())
                print(f"Email sent to {email}")
        except Exception as e:
            print(f"Failed to send email to {email}: {e}")

send_blog_to_subscribers("nlblog", "New Post", '<b>Some <i>HTML</i> text</b> and an image.<br><img src="cid:Test.png"><br>Nifty!', ['Test.png'])
