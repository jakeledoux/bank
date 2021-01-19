from random import randrange
from typing import Callable, Optional


def calc_luhn(number: str):
    """ Calculates the check digit for a given number using the Luhn Algorithm.

        :param number: The number to check for as a string.

        :returns: The calculated check digit.
    """
    doubled = list(number)
    doubled[1::2] = [str(int(n) * 2) for n in doubled[1::2]]
    summed = [sum([int(c) for c in n]) for n in doubled]
    summed = sum(summed)
    check_digit = (summed * 9) % 10
    return check_digit


def verify_luhn(number: str):
    """ Verifies the check digit for a given number using the Luhn Algorithm.

        :param number: The number to verify as a string.

        :returns: Whether the number is valid.
    """
    check_digit = calc_luhn(number[:-1])
    return check_digit == int(number[-1])


def gen_number(issuer_number: str = '', length: int = 16,
               validator: Optional[Callable[[str], bool]] = None) \
        -> Optional[str]:
    """ Generates a new card number with a valid check digit.

        :param issuer_number: The issuer's number prefix.
        :param length: How long the number should be in total.
        :param validator: A function that determines whether the number is
            valid.

        :returns: The generated number as a string or None if number failed to
            validate after a number of attempts.
    """
    # If omitted, set validator to something that will return True
    validator = validator or bool
    for _ in range(1000):
        digits = [str(randrange(10))
                  for _ in range(length - len(issuer_number) - 1)]
        partial_number = issuer_number + ''.join(digits)

        full_number = partial_number + str(calc_luhn(partial_number))
        if validator(full_number):
            return full_number
    return None

if __name__ == '__main__':
    # Tests
    num = '79927398713'
    assert calc_luhn(num[:-1]) == 3
    assert verify_luhn(num)

    for prefix in ('4', '3528', '6011'):
        new_num = gen_number(prefix)
        assert verify_luhn(new_num)
