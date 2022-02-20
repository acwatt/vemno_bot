# Python 3.7
# File name: 
# Authors: Aaron Watt
# Date: 2021-07-09
"""Functions to read venmo transactions and make requests."""
# Standard library imports
import csv
import datetime
from pathlib import Path
import pandas as pd
import random

# Third-party imports
import venmo_api.apis.payment_api
from venmo_api import Client

# Local application imports
from txt import send_text


class VenmoBot:
    """Class to do various Venmo and administrative tasks for paying monthly bills."""
    def __init__(self, expected_users=8):
        self.device_id = '54594367-57Y4-5F17-94Y1-6HP31O105YQ3'
        self.access_token = 'a3d7848640360e2442e96748d9d75923ee24adea9969277e76e0e726951b72fe'
        self.my_id = '2566471037222912623'
        self.venmo = self.get_venmo_client()
        self.last_month, self.this_month, self.next_month = self.get_month()
        self.username_csv = Path(r"/media/a/E/Documents/kcgcGoogleDrive/College_future/Housing/The Jungle on Ellsworth/Utilities/usernames.csv")
        self.emoticon_csv = Path.cwd() / 'emoticons.csv'
        self.username_list = self.get_username_list()
        self.username_dict = self.get_user_ids(expected_users=expected_users)
        self.signature = '~Love, VenmoBot'
        self.charge_reason = 'Jungle Water, Internet, Electricity'
        print(self.last_month, self.this_month, self.next_month)

    def get_venmo_client(self):
        print('Generating Venmo Client object with access token.')
        return Client(access_token=self.access_token)

    def get_month(self):
        # todo: get actual billing dates of bills and list those, adding into the request message
        today = datetime.date.today()
        first = today.replace(day=1)
        last = today.replace(day=28)
        thisMonth = today.strftime('%B')
        lastMonth = (first - datetime.timedelta(days=1)).strftime('%B')
        nextMonth = (last + datetime.timedelta(days=10)).strftime('%B')
        year = today.strftime('%Y')
        return f"{lastMonth} {year}", f"{thisMonth} {year}", f"{nextMonth} {year}"

    def get_username_list(self):
        """Return list of housemate usernames from CSV."""
        # todo: change printing to logging
        with open(self.username_csv, mode='r') as infile:
            reader = csv.reader(infile)
            rows = [row for row in reader]
            rows.pop(0) # remove first row
            mylist = [row[0].strip() for row in rows]
        print(f'List of housemate username:\n{mylist}')
        return mylist

    def get_access_token(self):
        """Use password to return Venmo access token -- requires 2-factor authentication."""
        # todo: store password and access_token in file that is .gitignored
        access_token = Client.get_access_token(username='kratzer.canby@gmail.com',
                                               password='L8OS8gbEoaEoG85hvfaxAU6FsUbK9KRP')
        return access_token

    def get_user_ids(self, expected_users=8):
        """Return dict of housemate usernames and IDs."""
        user_dict = {}
        for username in self.username_list:
            users = self.venmo.user.search_for_users(query=username)
            for user in users:
                if user.username in self.username_list:
                    print(f'Found user {user.username}')
                    # todo: add check for multiple matches
                    user_dict[username] = user.id
        if len(user_dict) == expected_users:
            print('Found all housemates!')
            return user_dict
        else:
            print('Found', len(user_dict), 'users! Sending Error message to Aaron.')
            send_text(subject='Venmo App Error :/',
                      body=f'{len(user_dict)} housemate usernames found when 8 expected!')
            raise

    def utilties_amount(self):
        """Return per-housemate total for all utility bills this month.

        1. search emails for this month's bills
        2. download PDF bills to local directory
        3. upload those PDFs to shared google drive folder
        4. append amounts for each bill to shared google spreadsheet
        5. return per-housemate bill (total / 9 housemates)
        """
        # todo: get total utitilies from email bills (or bills.csv)
        total = 600
        return total / 9

    def select_emoticon(self, level):
        """Return randomly selected string of emoji for level from CSV"""
        df = pd.read_csv(self.emoticon_csv)
        row = df[df['level_of_anger']==level]
        n = len(row.T.dropna()) - 1  # number of emoticons in this level of anger
        n = random.randint(1,n)
        col = f'emoticon{n}'  # name of column in CSV
        return row[col].values[0]

    def request_from(self, username, amount, level=0, last_month=None, this_month=None):
        """Submit a Venmo request amount from user_id and store transaction ID to CSV."""
        print(f'Requesting ${amount} from {username}')
        user_id = self.username_dict[username]
        # todo: send text if error
        emoticon = self.select_emoticon(level)
        if last_month is None:
            last_month, this_month = self.last_month, self.this_month
        note = f'{emoticon}\n\n{self.charge_reason}\n{last_month}-{this_month}\n{self.signature}'
        try:
            self.venmo.payment.request_money(amount, note, user_id)
        except Exception as err:
            send_text('Venmo bot error :/', err)
        # todo: check pending charges list to see if the charge posted. If not, charge
        return level
        # todo: save level to charges.csv, add 1 to it each time.

    def save_pending_charges(self):
        """Save dict of pending charges from Venmo api to CSV."""
        # todo: get pending charges print_pending_charges

    def load_pending_charges(self):
        """Return dict of pending charge IDs from pending charges CSV."""
        # todo: add CSV path to __init__
        # todo: load CSV, return list using tools csv_to_dict
        pass

    def send_to(self, username, amount):
        """Submit a Venmo payment for amount to user_id."""
        # todo: find WF checking account in payment method list
        """
        payment_methods = client.payment.get_payment_methods()
        for payment_method in payment_methods:
            print(payment_method.to_json())
        """
        print(f'Sending ${amount} to {username}')
        user_id = self.username_dict[username]
        self.venmo.payment.send_money(amount, f"{self.next_month} rent for room 6", str(user_id))

    def get_pending_payments(self):
        """Return dict of pending payments from Venmo api."""
        charges = self.venmo.payment.get_charge_payments()
        pending = {}
        for charge in charges:
            if charge.status.value == 'pending':
                pending[charge.id] = {}

    def print_charges(self):
        """Print all pending chargest from me to someone else."""
        charges = self.venmo.payment.get_charge_payments()
        for charge in charges:
            print(f'\n{charge.status.value} charge of ${charge.amount} to {charge.target.display_name}')

    def print_pending_charges(self):
        """Print all pending chargest from me to someone else."""
        charges = self.venmo.payment.get_charge_payments()
        for charge in charges:
            if charge.status.value == 'pending':
                print(f'\nPending charge of ${charge.amount} to {charge.target.display_name}. ID: {charge.id}')

    def update_charges(self):
        """Load and update dataframe of charges."""
        # todo: these things below
        # load pending payments from CSV
        # create unique identifier f'{user_id}_{months}'
        # get charges from venmo
        # create df of charges and create uniuqe identifier from notes
        # update local charges df with venmo df
        # save updated charges df to CSV
        pass

    def search_pending_charges(self):
        """Return list of payment object IDs from venmo bot that """

        pass

    def print_rencent_transactions(self, n):
        """Print n recent transactions."""
        transactions = self.venmo.user.get_user_transactions(user_id=self.my_id)
        transaction_counter = 1
        while transactions:
            for transaction in transactions:
                print(f'\nTransaction {transaction_counter}:')
                print_transaction_details(transaction)
                if transaction_counter == n:
                    return
                transaction_counter += 1

            print("\n" + "=" * 15 + "\n\tNEXT PAGE\n" + "=" * 15 + "\n")
            transactions = transactions.get_next_page()

    def print_all_transactions(self):
        """Print all recent transactions."""
        transactions = self.venmo.user.get_user_transactions(user_id=self.my_id)
        while transactions:
            for transaction in transactions:
                # print(transaction)
                print_transaction_details(transaction)
            return

            print("\n" + "=" * 15 + "\n\tNEXT PAGE\n" + "=" * 15 + "\n")
            transactions = transactions.get_next_page()

    def check_if_paid(self, user_id):
        """Check if user_id has paid this month's request."""
        # check transactions if
        # TODO: see what the status of a request is in the transaction list,
        # wnat to check that status to see if someone has paid (daily) and send reminder if not
        # Get all the transactions possible (prints 50 per request until nothing has left)
        transactions = self.venmo.user.get_user_transactions(user_id=user_id)
        while transactions:
            for transaction in transactions:
                print(transaction)

            print("\n" + "=" * 15 + "\n\tNEXT PAGE\n" + "=" * 15 + "\n")
            transactions = transactions.get_next_page()


def get_unique_charge_identifier(user_id, note):
    """Parse the note and return a unique charge identifier."""
    left_delim = '|| '
    right_delim = f'\n{self.signature}'
    months = note.lstrip(left_delim).rstrip(right_delim)
    return f'{user_id}_{months}'


def print_transaction_details(transaction):
    if transaction.payment_type == 'charge':
        message = f'{transaction.actor.display_name} charged ' \
                  f'{transaction.target.display_name} ' \
                  f'{transaction.amount} ' \
                  f'and it is {transaction.status}.'
    if transaction.payment_type == 'pay':
        message = f'{transaction.actor.display_name} paid ' \
                  f'{transaction.target.display_name} ' \
                  f'{transaction.amount}'
    print(message)


# MAIN -------------------------------
if __name__ == "__main__":
    import time
    bot = VenmoBot(expected_users=8)
    # madi = 'Madison-Raa'
    # aaron = 'Aaron-Kau'

    for user in bot.username_dict.keys():
        bot.request_from(user, 121.00, level=1, last_month='Jan 2022', this_month='Feb 2022')

    # updated documents are in /media/a/E/Documents/kcgcGoogleDrive/College_future/Housing/The Jungle on Ellsworth/Utilities

    # Charge for Feb 121.00
    # Charge for Jan 140.24
    # Charge for Dec 125.43
    # Charge for Nov 109.83
    # Charge for (before) Oct 47.85
    # Charge for Sep 133.06
    # Charge for Aug 80.75
    # bot.request_from(aaron, 0.75, level=2)
    bot.print_pending_charges()
    # bot.request_from(aaron, 1, level=2)
    # bot.print_pending_charges()
    # todo: figure out why requests aren't working
    #    perhaps the Venmo api has been updated but the python wrapper has not?


# REFERENCES -------------------------
"""
python wrapper on the Venmo api:
https://github.com/mmohades/venmo
"""
