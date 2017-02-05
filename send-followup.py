#!/usr/bin/env python

from tqdm import tqdm
import yaml

import jinja2
import mimetypes
import pandas as pd
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
    print('Usage: ./send-followup.py rsvp.tsv followup.txt.in')

def get_welcome(arr):
    if arr['welcome'] == "TRUE":
        return True
    else:
        return False

def get_recipients(arr):
    l=[arr['email1'], arr['email2'], arr['email3']]
    r=[]
    for item in l:
        if len(item) > 0:
            r.append(str(item))
    comma=", "
    return comma.join(r)

with open(sys.argv[2], 'r') as fp:
    email_template = fp.read()
template = jinja2.Template(email_template)

invitees = pd.read_csv(sys.argv[1],
                       delimiter='\t',
                       header=None,
                       names=['invitee', 'email1', 'email2', 'email3', 'welcome'],
                       dtype=str,
                       na_filter=False)

# Load the configuration
with open('config.yaml', 'r') as fp:
    config = yaml.load(fp)


server = smtplib.SMTP(config['smtpserver'])
server.starttls()
server.login(config['username'], config['apppass'])


for family in tqdm(invitees.iterrows()):
    family = dict(family[1])
    email_body = template.render(guests=family['invitee'],
                                 welcome = get_welcome(family))
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Katy Huff and Strom Borman Wedding Info'
    msg['Subject'] = '(Info) Wedding of {}'.format(config['wedders'])
    msg['From'] = config['from']
    msg['To'] = str(get_recipients(family))
    msg['Cc'] = config['cc']
    msg['Date'] = email.utils.formatdate()
    msg.attach(MIMEText(email_body, 'plain'))
    from_address = config['from']
    to_address = []
    to_address.extend([str(em.strip()) for em in get_recipients(family).split(', ')])

    #print(email_body)
    server.sendmail(from_address, to_address, msg.as_string())
