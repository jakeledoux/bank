from decimal import Decimal
import sqlite3

def get_balance(name):
    result = c.execute(
        f'SELECT balance FROM users WHERE name LIKE "{name}";'
    ).fetchone()
    if result:
        return Decimal(result[0])
    return None

def create_account(name, password, card_num):
    # Check if card number is taken
    result = c.execute(f'SELECT card FROM users WHERE card = {card_num};')
    if result.fetchone():
        return (False, 'Card number is taken.')
    else:
        result = c.execute(
            ''' INSERT INTO users (name, password, card, balance)
                VALUES ("{name}", "{password}", "{card_num}", "0.00");
            '''
        )
        if result.rowcount:
            return (True, 'Account created.')
        else:
            return (False, 'Unknown failure.')

conn = sqlite3.connect('bank.db')
c = conn.cursor()

# name = input('Enter the name of the account you wish to check: ').strip()
# balance = get_balance(name)
# if balance:
#     print(balance)
# else:
#     print('No user found with given name.')
