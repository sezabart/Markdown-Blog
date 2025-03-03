from fasthtml.common import (
    # FastHTML's HTML tags
    Group, Button, Input, H1, Response, Html, to_xml, A,
)

from PIL import Image
import io

from pathlib import Path
from make_app import app, blogs_config, mail_config, content_dir, domain, image_width
from update import EmailUpdate
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
import re

def send_html_to_subscribers(blog, post_name, html_content, image_paths):
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
    
    blog_config = blogs_config[blog]
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = f"{blog_config['email']['subject']}: {post_name}"
    msg.attach(MIMEText(html_content, 'html'))
    image_paths = [f"{content_dir}/{blog}/{post_name}/{image_path}" for image_path in image_paths]
    for image_path in image_paths:
        with open(image_path, 'rb') as img:
            img = Image.open(image_path)

            img = img.convert("RGB")
            width = image_width
            width_percent = (width / float(img.size[0]))
            height_size = int((float(img.size[1]) * float(width_percent)))
            img = img.resize((width, height_size))
            img_io = io.BytesIO()
            
            img.save(img_io, format="JPEG", quality=95, optimize=True)
            img_io.seek(0)
            mime = MIMEImage(img_io.read(), _subtype="jpeg")

            mime.add_header('Content-ID', '<' + image_path.split('/')[-1] + '>') # TODO: Split? so disgegard extension
            msg.attach(mime)
    
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        print("Logged in")
        try:
            for email in emails:
                #msg['To'] = email  not needed?
                server.sendmail(sender_email, email, msg.as_string())
                print(f"Email sent to {email}")
        except Exception as e:
            print(f"Failed to send email to {email}: {e}")



@rt("/blogs/{blog:str}/post/{post_name:str}/send")
def send_post(request, blog:str, post_name: str):
    password = os.environ.get('ADMIN_PASSWORD')
    if 'password' not in request.query_params or request.query_params['password'] != password:
        return Response("Unauthorized", status_code=401)


    post_dir = content_dir / f"{blog}" / f"{post_name}"
    md_files = sorted([f for f in post_dir.iterdir() if f.suffix == ".md"], reverse=False)
    
    if not md_files:
        return Response("No markdown files found", status_code=404)
    
    updates = [EmailUpdate(path, post_name, blog) for path in md_files]

    html_content = to_xml(
        Html(
            H1(post_name), 
            A(blogs_config[blog]['email']['link'], href=f"{domain}/blogs/{blog}/post/{post_name}"),
            *updates
    ))

    image_paths = re.findall(r'src="([^"]+)"', html_content) # post/image.jpg

    html_content = html_content.replace(f'src="', f'src="cid:')
    
    
    #print(f"Image paths: {image_paths}")
    
    send_html_to_subscribers(blog, post_name, html_content, image_paths)

    
    return Response(f"Emails sent to subscribers", status_code=200)