from fasthtml.common import (
    # FastHTML's HTML tags
    Group, Button, Input,
)

from pathlib import Path

from make_app import app, blogs_config
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
        
def send_mail(blog, post_name, email, update):
    blog_config = blogs_config[blog]
    # Send an email to the subscriber
    pass