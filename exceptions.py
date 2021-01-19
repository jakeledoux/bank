from typing import Union


class AccountNotFoundError(Exception):
    """ When querying accounts returns nothing.
    """
    def __init__(self, message: Union[str, None]):
        message = message or 'Failed to find account with matching parameters.'
        super(AccountNotFoundError, self).__init__(message)


class InsufficientBalanceError(Exception):
    """ When an account tries to use funds it doesn't possess.
    """
    def __init__(self, message: Union[str, None]):
        message = message or 'The account has insufficent balance to complete \
                this action.'
        super(InsufficientBalanceError, self).__init__(message)
