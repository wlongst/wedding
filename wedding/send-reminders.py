#!/usr/bin/env python

import jinja2
import mimetypes
import numpy as np
import os
import smtplib
import sys
import getpass
import email
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
# Here are the email package modules we'll need
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication

if len(sys.argv) < 3:
    print('Usage: ./send-reminders.py no_rsvp.csv reminder.txt.in')

def get_recipients(arr):
  l=[arr['email1'],arr['email2'],arr['email3']]
  r=[]
  for item in l:
    if len(item) > 0:
      r.append(item)
  comma=", "
  return comma.join(r)

with open(sys.argv[2], 'r') as fp:
    email_template = fp.read()
template = jinja2.Template(email_template)

invitees = np.loadtxt(sys.argv[1],
        delimiter='\t',
        dtype={'names': ('invitee','email1','email2','email3'),
            'formats': ('S128', 'S128', 'S128', 'S128')})

username = 'katyhuff@gmail.com'
password = getpass.getpass('password:')
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username, password)

for family in invitees:
    email_body = template.render(guests=family['invitee'])
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Wedding of Katy Huff and Strom Borman'
    msg['From'] = 'Katy Huff and Strom Borman <stromandkaty@gmail.com>'
    msg['To'] = get_recipients(family)
    msg['Cc'] = 'Matthew Strom Borman <stromborman@gmail.com>,Katy Huff <katyhuff@gmail.com>'
    msg['Date'] = email.utils.formatdate()
    msg.attach(MIMEText(email_body, 'plain'))
    from_address = 'Katy Huff <katyhuff@gmail.com>'
    to_address = []
    to_address.extend([em.strip() for em in get_recipients(family).split(', ')])

    print(email_body)
    server.sendmail(from_address, to_address, msg.as_string())
