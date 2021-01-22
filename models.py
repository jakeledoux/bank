import card_number
from datetime import datetime
from decimal import Decimal
from exceptions import AccountNotFoundError, InsufficientBalanceError
from passlib.hash import pbkdf2_sha256 # type: ignore
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from random import randrange
from typing import List, Optional

Base = automap_base()


class Account(Base):
    __tablename__ = 'accounts'

    _balance = Column('balance', String)

    transactions = relationship('Transaction')

    def __repr__(self):
        return f'<Account \'{self.name}\' (${self.balance:,.2f})>'

    @property
    def balance(self) -> Decimal:
        """ Gets this user's balance as a Decimal object.
        """
        return Decimal(self._balance)

    @balance.setter
    def balance(self, value: Decimal):
        """ Set's this user's balance. Does not commit to DB.
        """
        if isinstance(value, Decimal):
            value_string = f'{value:.2f}'
            self._balance = value_string
            return True
        raise TypeError('Account.balance must be of type string or Decimal.')

    def update_card(self, card_number: str) -> bool:
        """ Updates the card number on file.

            :param card_number: The new card number to use.

            :returns: Whether the action was successful.
        """
        if isinstance(card_number, str):
            self.card = card_number
            session.commit()
            return True
        return False

    def deposit(self, amount: Decimal):
        """ Deposit funds into account. (For ATMs)

            :param amount: The amount to deposit.
        """
        if amount > 0:
            self.balance += amount
            self.log_transaction(amount, 'ATM Deposit')
            session.commit()
        else:
            raise ValueError('Cannot deposit negative/zero funds.')

    def withdraw(self, amount: Decimal):
        """ Withdraw funds from account. (For ATMs)

            :param amount: The amount to withdraw.
        """
        if amount > 0:
            if amount <= self.balance:
                self.balance -= amount
                self.log_transaction(-amount, 'ATM Withdraw')
                session.commit()
            else:
                raise InsufficientBalanceError(
                    'Amount exceeds current account balance.'
                )
        else:
            raise ValueError('Cannot withdraw negative/zero funds.')

    def charge_card(self, amount: Decimal, card_number: str):
        """ Request funds be transferred from another account. Useful for
            businesses and shops that need to take funds from customers.

            :param amount: The amount to recieve.
            :param card_number: The recipient's public card number.
        """
        if amount > 0:
            # Lookup recipient by card number
            recipient = session.query(Account) \
                    .filter_by(card=card_number).first()
            if recipient:
                if amount <= recipient.balance:
                    # Transfer funds
                    recipient.balance -= amount
                    self.balance += amount
                    # Log transfers
                    recipient.log_transaction(-amount, self.name)
                    self.log_transaction(amount, recipient.name)
                    session.commit()
                else:
                    raise InsufficientBalanceError(
                        'Amount exceeds current account balance.'
                    )
            else:
                raise AccountNotFoundError(
                    'No account with given card number.'
                )
        else:
            raise ValueError('Cannot request negative/zero funds.')

    def send_funds(self, amount: Decimal, public_key: str):
        """ Transfer funds from this account to another.

            :param amount: The amount to send.
            :param public_key: The recipient's public key.
        """
        if amount > 0:
            if amount <= self.balance:
                # Lookup recipient by their public key
                recipient = session.query(Account) \
                        .filter_by(public_key=public_key).first()
                if recipient:
                    # Transfer funds
                    recipient.balance += amount
                    self.balance -= amount
                    # Log transfers
                    recipient.log_transaction(amount, self.name)
                    self.log_transaction(-amount, recipient.name)
                    session.commit()
                else:
                    raise AccountNotFoundError(
                        'No account with given public key.'
                    )
            else:
                raise InsufficientBalanceError(
                    'Amount exceeds current account balance.'
                )
        else:
            raise ValueError('Cannot send negative/zero funds.')

    def log_transaction(self, amount: Decimal, recipient: str, date=None) \
            -> 'Transaction':
        """ Creates a new transaction object belonging to this user. This method
            does not transfer funds and assumes this has already been done.

            :param amount: The amount of money transferred.
            :param recipient: The recipient's display name.
            :param date: When this transaction took place in UTC. Defaults to
                now.

            :returns: The transaction object if successful.
        """
        date = date or datetime.utcnow()
        new_trans = Transaction(_amount=str(amount), recipient=recipient,
                                account=self, date=date,
                                balance=str(self.balance))
        session.add(new_trans)
        session.commit()
        return new_trans

    def check_pass(self, password: str) -> bool:
        """ Checks whether given password matches the stored hash.

            :param password: The password to check.
            :returns: Whether or not the password matches.
        """
        return self.verify_hash(password, self.password)

    def change_pass(self, new_password: str):
        """ Changes this accounts password.

            :param new_password: The password to change to.
        """
        self.password = self.hash_pass(new_password)
        session.commit()

    @staticmethod
    def hash_pass(password: str) -> str:
        """ Salts and hashes a password.

            :param password: The string to hash.
            :returns: The hashed password.
        """
        return pbkdf2_sha256.hash(password)

    @staticmethod
    def verify_hash(password: str, pass_hash: str) -> bool:
        """ Verifies whether the string matches the hash.

            :param password: The string to check.
            :param hash: The hash to check.

            :returs: Whether the string and hash match.
        """
        return pbkdf2_sha256.verify(password, pass_hash)

    @staticmethod
    def gen_card_number(prefix: str = '') -> Optional[str]:
        """ Generates a unique card number and validates against the database.

            :param prefix: Optional issuer number prefix.
            :returns: New card number.
        """
        new_number = card_number.gen_number(
            validator=lambda n: not session.query(Account) \
            .filter_by(public_key=n).count()
        )

        return new_number

    @classmethod
    def create(cls, name: str, email: str, password: str,
               card: Optional[str] = None) -> 'Account':
        """ Creates a new Account object.
        """
        password = cls.hash_pass(password)
        public_key = Account.gen_card_number()
        new_user = Account(name=name, email=email, password=password, card=card,
                           _balance="0.00", public_key=public_key)
        session.add(new_user)
        session.commit()
        return new_user


class Transaction(Base):
    __tablename__ = 'transactions'

    _amount = Column('amount', String)

    account_ID = Column('account_id', Integer, ForeignKey('accounts.id'))
    account = relationship(Account, foreign_keys=account_ID)

    def __repr__(self):
        return f'<Transaction \'{self.account.name}\' (${self.amount:,.2f})>'

    @property
    def amount(self):
        return Decimal(self._amount)


engine = create_engine('sqlite:///bank.db')
Base.prepare(engine, reflect=True)

session = Session(engine)

if __name__ == '__main__':
    accounts = List[Account]
    jake, ishai, chris = accounts = session.query(Account).all()
    print(*accounts)
