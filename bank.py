# from models import Account, Transaction
from prompt_toolkit.shortcuts import button_dialog

choice = button_dialog(title='WAMPA BANK', text='Hello, world!',
                       buttons=[('Log in', 0),
                                ('Sign up', 1),
                                ('Exit', 2)]).run()
print(choice)
