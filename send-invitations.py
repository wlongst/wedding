#!/usr/bin/env python
'''Invitation email generator'''

from argparse import ArgumentParser
from tqdm import tqdm
import yaml

import jinja2
import pandas as pd
from os.path import basename
import smtplib
import sys
import email
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def process_arguments(args):

    parser = ArgumentParser(description=__doc__)

    parser.add_argument('-a', '--attachment', dest='attachment',
                        type=str, default="resources/invitation.pdf",
                        help='Path to attachment file')

    parser.add_argument('-c', '--config', dest='config',
                        type=str, default='config.yaml',
                        help='Path to the configuration file')

    parser.add_argument('-s', '--send',
                        dest='debug',
                        action='store_false',
                        help='Send emails')

    parser.add_argument('recipients',
                        type=str,
                        help='File containing the table of recipients')

    parser.add_argument('template',
                        type=str,
                        help='File containing the email template')

    return parser.parse_args(args)


def get_comments(arr):
    if len(arr['comments']) > 0:
        return str(arr['comments'])
    else:
        return ''


def get_recipients(arr):
    l = [arr['email1'], arr['email2'], arr['email3']]
    r = []
    for item in l:
        if len(item) > 0:
            r.append(str(item))
    return ', '.join(r)


if __name__ == '__main__':
    params = process_arguments(sys.argv[1:])

    with open(params.template, 'r') as fp:
        template = jinja2.Template(fp.read())

    # Load the configuration
    with open(params.config, 'r') as fp:
        config = yaml.load(fp)

    # Load the pdf
    with open(params.attachment, 'rb') as fp:
        attachment = fp.read()

    if not params.debug:
        server = smtplib.SMTP(config['smtpserver'])
        server.starttls()
        server.login(config['username'], config['apppass'])
    else:
        server = False

    invitees = pd.read_table(params.recipients, dtype=str, na_filter=False)

    subject = 'Invitation to the Wedding of {}'.format(config['wedders'])
    content = 'attachment; filename="{}"'.format(basename(params.attachment))
    for family in tqdm(invitees.iterrows()):
        family = dict(family[1])

        email_body = template.render(guests=family['invitee'],
                                     comments=get_comments(family))

        msg = MIMEMultipart('alternative')

        msg['Subject'] = subject
        msg['From'] = config['from']
        msg['To'] = str(get_recipients(family))
        msg['Cc'] = config['cc']
        msg['Date'] = email.utils.formatdate()

        msg.attach(MIMEText(email_body, 'plain'))

        part = MIMEApplication(attachment)
        part.add_header('Content-Disposition', content)
        msg.attach(part)

        from_address = config['from']

        to_address = [str(em.strip())
                      for em in get_recipients(family).split(', ')]

        if params.debug:
            print('From: {}'.format(from_address))
            print('To: {}'.format(to_address))
            print(email_body)
            print('---')
        else:
            server.sendmail(from_address, to_address, msg.as_string())
