#!/usr/bin/env python
'''Generate no-rsvp list'''

from argparse import ArgumentParser
import sys

import pandas as pd


def process_arguments(args):

    parser = ArgumentParser(description=__doc__)

    parser.add_argument(dest='recipients', type=str,
                        help='Path to original invitation list')

    parser.add_argument(dest='rsvp', type=str,
                        help='Path to RSVP list')

    parser.add_argument(dest='output', type=str,
                        help='Path to store output')

    return parser.parse_args(args)


if __name__ == '__main__':
    params = process_arguments(sys.argv[1:])

    invitees = pd.read_table(params.recipients,
                             dtype=str,
                             sep=',',
                             na_filter=False)
    invitees['email'] = invitees['email'].apply(lambda x: x.strip().lower())

    rsvp = pd.read_table(params.rsvp,
                         dtype=str,
                         sep=',',
                         na_filter=False)

    rsvp['Email Address'] = rsvp['Email Address'].apply(lambda x: x.strip().lower())

    truants = invitees[~invitees['email'].isin(rsvp['Email Address'])]

    truants.to_csv(params.output, index=False)
