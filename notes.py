# Floats are inprecise.
#   - Cannot represent 1/3 in decimal
#   - Cannot represent 1/10 in binary
0.1 + 0.1 + 0.1 - 0.3 != 0
# Tiny imprecisions are fine for landing rockets
# They are not fine for explicit things like finances
# Python comes with a library to handle this
from decimal import Decimal
a, b = Decimal('0.1'), Decimal('0.3')
a + a + a - b == 0
# Notice we pass the number as a string.
# This is what happens if we don't
print(Decimal(0.1))
