from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from typing import Union

Base = automap_base()


# SKIP 1: CLASSES
class Account(Base):
    __tablename__ = 'accounts'

    # SKIP 3 ###################################################################
    _balance = Column('balance', String)
    ############################################################################

    # SKIP 2 ###################################################################
    transactions = relationship('Transaction')
    ############################################################################

    def __repr__(self):
        return f'<Account \'{self.name}\' (${self.balance:,.2f})>'

    # SKIP 3 ###################################################################
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
            value = f'{value:.2f}'
            self._balance = value
            return True
        raise TypeError('Account.balance must be of type string or Decimal.')
    ############################################################################

    # SKIP 4 ###################################################################
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
                                account=self, date=date)
        session.add(new_trans)
        session.commit()
        return new_trans

    @classmethod
    def create(cls, name: str, email: str, password: str,
               card: Union[str, None] = None) -> 'Account':
        """ Creates a new Account object.
        """
        new_user = Account(name=name, email=email, password=email, card=card,
                           _balance="0.00")
        session.add(new_user)
        session.commit()
        return new_user
    ############################################################################

class Transaction(Base):
    __tablename__ = 'transactions'

    # SKIP 3 ###################################################################
    _amount = Column('amount', String)
    ############################################################################

    # SKIP 2 ###################################################################
    account_ID = Column('account_id', Integer, ForeignKey('accounts.id'))
    account = relationship(Account, foreign_keys=account_ID)
    ############################################################################

    def __repr__(self):
        return f'<Transaction \'{self.account.name}\' (${self.amount:,.2f})>'

    # SKIP 3 ###################################################################
    @property
    def amount(self):
        return Decimal(self._amount)
    ############################################################################


engine = create_engine('sqlite:///bank.db')
Base.prepare(engine, reflect=True)

# UNSKIP 1 #####################################################################
# Account, Transaction = Base.classes.account, Base.classes.transaction
################################################################################

session = Session(engine)

jake, ishai, chris = accounts = session.query(Account).all()
print(*accounts)
