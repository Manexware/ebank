"""

(C) Copyright 2009 Manuel Vega Ulloa

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

""" Class used do inform errors.
"""


# Exception used to indicate that the value that setting in the bit is large than the iso limit to that bit!


class ValueToLarge(Exception):
    """Exception that indicates that a value that want to set inside the bit is larger than the "ISO" limit.
    This can happen when you have a different specification of mine.
    If this is the case, you should use "ISO8583.redefineBit()" method and redefine the limit.	"""

    def __init__(self, value):
        self.str = value

    def __str__(self):
        return repr(self.str)


# Exception to indicate that bit dosen't Exist!
class BitInexistent(Exception):
    """Exception that indicates that a bit that you try to manage doesn't exist!
    Try to check your "setBit". Remember that ISO8583 1993 has only bits from 1 to 128! 	"""

    def __init__(self, value):
        self.str = value

    def __str__(self):
        return repr(self.str)


# Exception to indicate that value type is not valid
class InvalidValueType(Exception):
    """Exception that indicate that a value that you try to insert is out of specification.
    For example, You try to insert a value "ABC" in a bit of type "N" (Number), this is invalid!
    This can happen when you have a different specification of mine.
    If this is the case, you should use "ISO8583.redefineBit()" method and redefine the type.	"""

    def __init__(self, value):
        self.str = value

    def __str__(self):
        return repr(self.str)


# Exception to indicate that bit type is not valid
class InvalidBitType(Exception):
    """Exception that indicates that the type that you try to set is invalid.
    For example, You try to set type "X"; that doesn't exist.
    Valid type are: B, N, A, AN, ANS, LL, LLL"""

    def __init__(self, value):
        self.str = value

    def __str__(self):
        return repr(self.str)


# Exception that indicate a invalid iso, maybe invalid size etc...
class InvalidIso8583(Exception):
    """Exception that indicate a invalid ASCII message, for example, without a piece... Error size, etc.	"""

    def __init__(self, value):
        self.str = value

    def __str__(self):
        return repr(self.str)


# Exception that indicates a invalid MTI, maybe it is not set
class InvalidMTI(Exception):
    """Exception that indicates a invalid MTI	"""

    def __init__(self, value):
        self.str = value

    def __str__(self):
        return repr(self.str)


# Exception that indicates that bit is not there.
class BitNotSet(Exception):
    """Exception that indicates that you try to access not present a bit in the bitmap.	"""

    def __init__(self, value):
        self.str = value

    def __str__(self):
        return repr(self.str)
