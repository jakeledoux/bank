from decimal import Decimal
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String

Base = automap_base()


# SKIP 1: CLASSES
class User(Base):
    __tablename__ = 'users'

    # SKIP 3 ###################################################################
    _balance = Column('balance', String)
    ############################################################################

    # SKIP 2 ###################################################################
    transactions = relationship('Transaction')
    ############################################################################

    def __repr__(self):
        return f'<User \'{self.name}\' (${self.balance:,.2f})>'

    # SKIP 3 ###################################################################
    @property
    def balance(self):
        return Decimal(self._balance)
    ############################################################################

class Transaction(Base):
    __tablename__ = 'transactions'

    # SKIP 3 ###################################################################
    _amount = Column('amount', String)
    ############################################################################

    # SKIP 2 ###################################################################
    account_ID = Column('account', Integer, ForeignKey('users.id'))
    account = relationship(User, foreign_keys=account_ID)
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
# User, Transaction = User, Base.classes.transaction
################################################################################

session = Session(engine)

jake, ishai = session.query(User).all()
print(jake, ishai)
