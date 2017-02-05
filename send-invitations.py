#!/usr/bin/env python

from tqdm import tqdm
import yaml

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
    print('Usage: ./send-invitations.py invitees.csv invitation.txt.in')

def get_comments(arr):
  if len(arr['comments']) > 0:
    return arr['comments']
  else :
    return ''

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
        dtype={'names': ('invitee','email1','email2','email3','comments'),
            'formats': ('S128', 'S128', 'S128', 'S128', 'S256')})

# Load the configuration

with open('config.yaml', 'r') as fp:
    config = yaml.load(fp)

filename="resources/invitation.pdf"
password = getpass.getpass('password:')
server = smtplib.SMTP(config['smtpserver'])
server.starttls()
server.login(config['username'], password)


for family in tqdm(invitees):
    email_body = template.render(guests=family['invitee'],
                                 comments = get_comments(family))
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Invitation to the Wedding of {}'.format(config['wedders'])
    msg['From'] = config['from']
    msg['To'] = get_recipients(family)
    msg['Cc'] = config['cc']
    msg['Date'] = email.utils.formatdate()
    msg.attach(MIMEText(email_body, 'plain'))
    part=MIMEApplication(open(filename).read()) 
    part.add_header('Content-Disposition',
            'attachment; filename="%s"' % os.path.basename(filename))
    msg.attach(part)
    from_address = config['from']
    to_address = []
    to_address.extend([em.strip() for em in get_recipients(family).split(', ')])

    print(email_body)
    #server.sendmail(from_address, to_address, msg.as_string())
