from .config import BaseConfig
import smtplib, ssl 
import win32com.client as win32
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from datetime import datetime
import click
from flask import current_app, g

def get_mail():
    if 'mail' not in g:
        g.mail = win32.Dispatch('Outlook.Application')

    return g.mail

def close_mail(e=None):
    mail = g.pop('mail',None)

    if mail is not None:
        mail.close()

def init_mail():
    mail = get_mail()

@click.command('init-mail')
def init_mail_command():
    """Clear the existing data and create new tables."""
    init_mail()
    click.echo('database inicializado.')

def init_app(app):
    app.teardown_appcontext(close_mail)
    app.init(init_mail())

