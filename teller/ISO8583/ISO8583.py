"""

(C) Copyright 2009 Igor V. Custodio

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

__author__ = 'Igor Vitorio Custodio <igorvc@vulcanno.com.br>'
__version__ = '1.3.1'
__licence__ = 'GPL V3'

import struct

from ISOErrors import *


class ISO8583:
    """Main Class to work with ISO8583 packages.
    Used to create, change, send, receive, parse or work with ISO8593 Package version 1993.
    It's 100% Python :)
    Enjoy it!
    License: GPL Version 3

    Example:
        from ISO8583.ISO8583 import ISO8583
        from ISO8583.ISOErrors import *

        iso = ISO8583()
        try:
            iso.set_mti('0800')
            iso.set_bit(2,2)
            iso.set_bit(4,4)
            iso.set_bit(12,12)
            iso.set_bit(21,21)
            iso.set_bit(17,17)
            iso.set_bit(49,986)
            iso.set_bit(99,99)
        except ValueToLarge, e:
                print ('Value too large :( %s' % e)
        except InvalidMTI, i:
                print ('This MTI is wrong :( %s' % i)

        Print ('The Message Type Indication is = %s' %iso.get_mti())

        print ('The Bitmap is = %s' %iso.get_bitmap())
        iso.show_iso_bits();
        print ('This is the ISO8583 complete package %s' % iso.get_raw_iso())
        print ('This is the ISO8583 complete package to sent over the TCPIP network %s' % iso.get_network_iso())

"""
    # Attributes
    # Bits to be set 00000000 -> _BIT_POSITION_1 ... _BIT_POSITION_8
    _BIT_POSITION_1 = 128  # 10 00 00 00
    _BIT_POSITION_2 = 64  # 01 00 00 00
    _BIT_POSITION_3 = 32  # 00 10 00 00
    _BIT_POSITION_4 = 16  # 00 01 00 00
    _BIT_POSITION_5 = 8  # 00 00 10 00
    _BIT_POSITION_6 = 4  # 00 00 01 00
    _BIT_POSITION_7 = 2  # 00 00 00 10
    _BIT_POSITION_8 = 1  # 00 00 00 01

    # Array to translate bit to position
    _TMP = [0, _BIT_POSITION_8, _BIT_POSITION_1, _BIT_POSITION_2, _BIT_POSITION_3, _BIT_POSITION_4, _BIT_POSITION_5,
            _BIT_POSITION_6, _BIT_POSITION_7]
    _BIT_DEFAULT_VALUE = 0

    # ISO8583 constants

    # Every _BITS_VALUE_TYPE has:
    # _BITS_VALUE_TYPE[N] = [ X,Y, Z, W,K]
    # N = bitnumber
    # X = small_str representation of the bit meaning
    # Y = large str representation
    # Z = type of the bit (B, N, A, AN, ANS, LL, LLL)
    # W = size of the information that N need to has
    # K = type os values a, an, n, ansb, b
    _BITS_VALUE_TYPE = {1: ['BME', 'Bit Map Extended', 'B', 16, 'b'],
                        2: ['2', 'Primary account number (PAN)', 'LL', 19, 'n'],
                        3: ['3', 'Precessing code', 'N', 6, 'n'], 4: ['4', 'Amount transaction', 'N', 12, 'n'],
                        5: ['5', 'Amount reconciliation', 'N', 12, 'n'],
                        6: ['6', 'Amount cardholder billing', 'N', 12, 'n'],
                        7: ['7', 'Date and time transmission', 'N', 10, 'n'],
                        8: ['8', 'Amount cardholder billing fee', 'N', 8, 'n'],
                        9: ['9', 'Conversion rate reconciliation', 'N', 8, 'n'],
                        10: ['10', 'Conversion rate cardholder billing', 'N', 8, 'n'],
                        11: ['11', 'Systems trace audit number', 'N', 6, 'n'],
                        12: ['12', 'Date and time local transaction', 'N', 6, 'n'],
                        13: ['13', 'Date effective', 'N', 4, 'n'], 14: ['14', 'Date expiration', 'N', 4, 'n'],
                        15: ['15', 'Date settlement', 'N', 4, 'n'], 16: ['16', 'Date conversion', 'N', 4, 'n'],
                        17: ['17', 'Date capture', 'N', 4, 'n'], 18: ['18', 'Message error indicator', 'N', 4, 'n'],
                        19: ['19', 'Country code acquiring institution', 'N', 3, 'n'],
                        20: ['20', 'Country code primary account number (PAN)', 'N', 3, 'n'],
                        21: ['21', 'Transaction life cycle identification data', 'ANS', 3, 'n'],
                        22: ['22', 'Point of service data code', 'N', 3, 'n'],
                        23: ['23', 'Card sequence number', 'N', 3, 'n'], 24: ['24', 'Function code', 'N', 3, 'n'],
                        25: ['25', 'Message reason code', 'N', 2, 'n'],
                        26: ['26', 'Merchant category code', 'N', 2, 'n'],
                        27: ['27', 'Point of service capability', 'N', 1, 'n'],
                        28: ['28', 'Date reconciliation', 'N', 8, 'n'],
                        29: ['29', 'Reconciliation indicator', 'N', 8, 'n'],
                        30: ['30', 'Amounts original', 'N', 8, 'n'],
                        31: ['31', 'Acquirer reference number', 'N', 8, 'n'],
                        32: ['32', 'Acquiring institution identification code', 'LL', 11, 'n'],
                        33: ['33', 'Forwarding institution identification code', 'LL', 11, 'n'],
                        34: ['34', 'Electronic commerce data', 'LL', 28, 'n'],
                        35: ['35', 'Track 2 data', 'LL', 37, 'n'], 36: ['36', 'Track 3 data', 'LLL', 104, 'n'],
                        37: ['37', 'Retrieval reference number', 'N', 12, 'an'],
                        38: ['38', 'Approval code', 'N', 6, 'an'], 39: ['39', 'Action code', 'A', 2, 'an'],
                        40: ['40', 'Service code', 'N', 3, 'an'],
                        41: ['41', 'Card acceptor terminal identification', 'N', 8, 'ans'],
                        42: ['42', 'Card acceptor identification code', 'A', 15, 'ans'],
                        43: ['43', 'Card acceptor name/location', 'A', 40, 'asn'],
                        44: ['44', 'Additional response data', 'LL', 25, 'an'],
                        45: ['45', 'Track 1 data', 'LL', 76, 'an'], 46: ['46', 'Amounts fees', 'LLL', 999, 'an'],
                        47: ['47', 'Additional data national', 'LLL', 999, 'an'],
                        48: ['48', 'Additional data private', 'LLL', 999, 'an'],
                        49: ['49', 'Verification data', 'A', 3, 'a'],
                        50: ['50', 'Currency code, settlement', 'AN', 3, 'an'],
                        51: ['51', 'Currency code, cardholder billing', 'A', 3, 'a'],
                        52: ['52', 'Personal identification number (PIN) data', 'B', 16, 'b'],
                        53: ['53', 'Security related control information', 'LL', 18, 'n'],
                        54: ['54', 'Amounts additional', 'LLL', 120, 'an'],
                        55: ['55', 'Integrated circuit card (ICC) system related data', 'LLL', 999, 'ans'],
                        56: ['56', 'Original data elements', 'LLL', 999, 'ans'],
                        57: ['57', 'Authorisation life cycle code', 'LLL', 999, 'ans'],
                        58: ['58', 'Authorising agent institution identification code', 'LLL', 999, 'ans'],
                        59: ['59', 'Transport data', 'LLL', 999, 'ans'],
                        60: ['60', 'Reserved for national use', 'LL', 7, 'ans'],
                        61: ['61', 'Reserved for national use', 'LLL', 999, 'ans'],
                        62: ['62', 'Reserved for private use', 'LLL', 999, 'ans'],
                        63: ['63', 'Reserved for private use', 'LLL', 999, 'ans'],
                        64: ['64', 'Message authentication code (MAC) field', 'B', 16, 'b'],
                        65: ['65', 'Bitmap tertiary', 'B', 16, 'b'], 66: ['66', 'Settlement code', 'N', 1, 'n'],
                        67: ['67', 'Extended payment data', 'N', 2, 'n'],
                        68: ['68', 'Receiving institution country code', 'N', 3, 'n'],
                        69: ['69', 'Settlement institution county code', 'N', 3, 'n'],
                        70: ['70', 'Network management Information code', 'N', 3, 'n'],
                        71: ['71', 'Message number', 'N', 4, 'n'], 72: ['72', 'Data record', 'LLL', 999, 'ans'],
                        73: ['73', 'Date action', 'N', 6, 'n'], 74: ['74', 'Credits, number', 'N', 10, 'n'],
                        75: ['75', 'Credits, reversal number', 'N', 10, 'n'],
                        76: ['76', 'Debits, number', 'N', 10, 'n'], 77: ['77', 'Debits, reversal number', 'N', 10, 'n'],
                        78: ['78', 'Transfer number', 'N', 10, 'n'],
                        79: ['79', 'Transfer, reversal number', 'N', 10, 'n'],
                        80: ['80', 'Inquiries number', 'N', 10, 'n'],
                        81: ['81', 'Authorizations, number', 'N', 10, 'n'],
                        82: ['82', 'Credits, processing fee amount', 'N', 12, 'n'],
                        83: ['83', 'Credits, transaction fee amount', 'N', 12, 'n'],
                        84: ['84', 'Debits, processing fee amount', 'N', 12, 'n'],
                        85: ['85', 'Debits, transaction fee amount', 'N', 12, 'n'],
                        86: ['86', 'Credits, amount', 'N', 15, 'n'],
                        87: ['87', 'Credits, reversal amount', 'N', 15, 'n'],
                        88: ['88', 'Debits, amount', 'N', 15, 'n'], 89: ['89', 'Debits, reversal amount', 'N', 15, 'n'],
                        90: ['90', 'Original data elements', 'N', 42, 'n'],
                        91: ['91', 'File update code', 'AN', 1, 'an'], 92: ['92', 'File security code', 'N', 2, 'n'],
                        93: ['93', 'Response indicator', 'N', 5, 'n'], 94: ['94', 'Service indicator', 'AN', 7, 'an'],
                        95: ['95', 'Replacement amounts', 'AN', 42, 'an'],
                        96: ['96', 'Message security code', 'AN', 8, 'an'],
                        97: ['97', 'Amount, net settlement', 'N', 16, 'n'], 98: ['98', 'Payee', 'ANS', 25, 'ans'],
                        99: ['99', 'Settlement institution identification code', 'LL', 11, 'n'],
                        100: ['100', 'Receiving institution identification code', 'LL', 11, 'n'],
                        101: ['101', 'File name', 'ANS', 17, 'ans'],
                        102: ['102', 'Account identification 1', 'LL', 28, 'ans'],
                        103: ['103', 'Account identification 2', 'LL', 28, 'ans'],
                        104: ['104', 'Transaction description', 'LLL', 100, 'ans'],
                        105: ['105', 'Reserved for ISO use', 'LLL', 999, 'ans'],
                        106: ['106', 'Reserved for ISO use', 'LLL', 999, 'ans'],
                        107: ['107', 'Reserved for ISO use', 'LLL', 999, 'ans'],
                        108: ['108', 'Reserved for ISO use', 'LLL', 999, 'ans'],
                        109: ['109', 'Reserved for ISO use', 'LLL', 999, 'ans'],
                        110: ['110', 'Reserved for ISO use', 'LLL', 999, 'ans'],
                        111: ['111', 'Reserved for private use', 'LLL', 999, 'ans'],
                        112: ['112', 'Reserved for private use', 'LLL', 999, 'ans'],
                        113: ['113', 'Reserved for private use', 'LL', 11, 'n'],
                        114: ['114', 'Reserved for national use', 'LLL', 999, 'ans'],
                        115: ['115', 'Reserved for national use', 'LLL', 999, 'ans'],
                        116: ['116', 'Reserved for national use', 'LLL', 999, 'ans'],
                        117: ['117', 'Reserved for national use', 'LLL', 999, 'ans'],
                        118: ['118', 'Reserved for national use', 'LLL', 999, 'ans'],
                        119: ['119', 'Reserved for national use', 'LLL', 999, 'ans'],
                        120: ['120', 'Reserved for private use', 'LLL', 999, 'ans'],
                        121: ['121', 'Reserved for private use', 'LLL', 999, 'ans'],
                        122: ['122', 'Reserved for national use', 'LLL', 999, 'ans'],
                        123: ['123', 'Reserved for private use', 'LLL', 999, 'ans'],
                        124: ['124', 'Info Text', 'LLL', 255, 'ans'],
                        125: ['125', 'Network management information', 'LL', 50, 'ans'],
                        126: ['126', 'Issuer trace id', 'LL', 6, 'ans'],
                        127: ['127', 'Reserved for private use', 'LLL', 999, 'ans'],
                        128: ['128', 'Message authentication code (MAC) field', 'B', 16, 'b']}

    # Default constructor of the ISO8583 Object
    def __init__(self, iso="", debug=False):
        """Default Constructor of ISO8583 Package.
        It initializes a "brand new" ISO8583 package
        Example: To Enable debug you can use:
            pack = ISO8583(debug=True)
        @param: iso a String that represents the ASCII of the package. The same that you need to pass to 
            set_iso_content() method.
        @param: Debug (True or False) default False -> Used to print some debug infos. Only use if want that messages!
        """
        # Bitmap internal representation
        self.BITMAP = []
        # Values
        self.BITMAP_VALUES = []
        # Bitmap ASCII representantion
        self.BITMAP_HEX = ''
        # MTI
        self.MESSAGE_TYPE_INDICATION = ''
        # Debug ?
        self.DEBUG = debug

        self.__initialize_bitmap()
        self.__initialize_bitmap_values()

        if iso != "":
            self.set_iso_content(iso)

    # Return bit type
    def get_bit_type(self, bit):
        """Method that return the bit Type
        @param: bit -> Bit that will be searched and whose type will be returned
        @return: str that represents the type of the bit
        """
        return self._BITS_VALUE_TYPE[bit][2]

    # Return bit limit
    def get_bit_limit(self, bit):
        """Method that return the bit limit (Max size)
        @param: bit -> Bit that will be searched and whose limit will be returned
        @return: int that indicate the limit of the bit
        """
        return self._BITS_VALUE_TYPE[bit][3]

    # Return bit value type
    def get_bit_value_type(self, bit):
        """Method that return the bit value type
        @param: bit -> Bit that will be searched and whose value type will be returned
        @return: str that indicate the value type of the bit
        """
        return self._BITS_VALUE_TYPE[bit][4]

    # Return large bit name
    def get_large_bit_name(self, bit):
        """Method that return the large bit name
        @param: bit -> Bit that will be searched and whose name will be returned
        @return: str that represents the name of the bit
        """
        return self._BITS_VALUE_TYPE[bit][1]

    # Set the MTI
    def set_transaction_type(self, tx_type):
        """Method that set Transaction Type (MTI)
        @param: type -> MTI to be setted
        @raise: ValueToLarge Exception
        """

        tx_type = "%s" % tx_type
        if len(tx_type) > 4:
            # tx_type = tx_type[0:3]
            raise ValueToLarge('Error: value up to size! MTI limit size = 4')

        type_t = ""
        if len(tx_type) < 4:
            for cont in range(len(tx_type), 4):
                type_t += "0"

        self.MESSAGE_TYPE_INDICATION = "%s%s" % (type_t, tx_type)

    # set_mti too
    def set_mti(self, tx_type):
        """Method that set Transaction Type (MTI)
        In fact, is an alias to "set_transaction_type" method
        @param: type -> MTI to be setted
        """
        self.set_transaction_type(tx_type)

    # Method that put "zeros" inside bitmap
    def __initialize_bitmap(self):
        """Method that initialize/reset a internal bitmap representation
        It's a internal method, so don't call!
        """

        if self.DEBUG:
            print('Init bitmap')

        if len(self.BITMAP) == 16:
            for cont in range(0, 16):
                self.BITMAP[cont] = self._BIT_DEFAULT_VALUE
        else:
            for cont in range(0, 16):
                self.BITMAP.append(self._BIT_DEFAULT_VALUE)

    # init with "0" the array of values
    def __initialize_bitmap_values(self):
        """Method that initialize/reset a internal array used to save bits and values
        It's a internal method, so don't call!
        """
        if self.DEBUG:
            print('Init bitmap_values')

        if len(self.BITMAP_VALUES) == 128:
            for cont in range(0, 129):
                self.BITMAP_VALUES[cont] = self._BIT_DEFAULT_VALUE
        else:
            for cont in range(0, 129):
                self.BITMAP_VALUES.append(self._BIT_DEFAULT_VALUE)

    # Set a value to a bit
    def set_bit(self, bit, value):
        """Method used to set a bit with a value.
        It's one of the most important method to use when using this library
        @param: bit -> bit number that want to be setted
        @param: value -> the value of the bit
        @return: True/False default True -> To be used in the future!
        @raise: BitInexistent Exception, ValueToLarge Exception
        """
        if self.DEBUG:
            print('Setting bit inside bitmap bit[%s] = %s') % (bit, value)

        if bit < 1 or bit > 128:
            raise BitInexistent("Bit number %s dosen't exist!" % bit)

        # calculate the position inside bitmap
        # pos = 1

        if self.get_bit_type(bit) == 'LL':
            self.__set_bit_type_ll(bit, value)

        if self.get_bit_type(bit) == 'LLL':
            self.__set_bit_type_lll(bit, value)

        if self.get_bit_type(bit) == 'N':
            self.__set_bit_type_n(bit, value)

        if self.get_bit_type(bit) == 'A':
            self.__set_bit_type_a(bit, value)

        if self.get_bit_type(bit) == 'ANS' or self.get_bit_type(bit) == 'B':
            self.__set_bit_type_ans(bit, value)

        if self.get_bit_type(bit) == 'B':
            self.__set_bit_type_b(bit, value)

        # Continuation bit?
        if bit > 64:
            self.BITMAP[0] = self.BITMAP[0] | self._TMP[2]  # need to set bit 1 of first "bit" in bitmap

        if (bit % 8) == 0:
            pos = (bit / 8) - 1
        else:
            pos = (bit / 8)

        # need to check if the value can be there .. AN , N ... etc ... and the size

        self.BITMAP[pos] = self.BITMAP[pos] | self._TMP[(bit % 8) + 1]

        return True

    # print bitmap
    def show_bitmap(self):
        """Method that print the bitmap in ASCII form
        Hint: Try to use get_bitmap method and format your own print :)
        """

        self.__build_bitmap()

        # printing
        print(self.BITMAP_HEX)

    # Build a bitmap
    def __build_bitmap(self):
        """Method that build the bitmap ASCII
        It's a internal method, so don't call!
        """

        self.BITMAP_HEX = ''

        for c in range(0, 16):
            if (self.BITMAP[0] & self._BIT_POSITION_1) != self._BIT_POSITION_1:
                # Only has the first bitmap
                if self.DEBUG:
                    print('%d Bitmap = %d(Decimal) = %s (hexa) ' % (c, self.BITMAP[c], hex(self.BITMAP[c])))

                tm = hex(self.BITMAP[c])[2:]
                if len(tm) != 2:
                    tm = '0' + tm
                self.BITMAP_HEX += tm
                if c == 7:
                    break
            else:  # second bitmap
                if self.DEBUG:
                    print('%d Bitmap = %d(Decimal) = %s (hexa) ' % (c, self.BITMAP[c], hex(self.BITMAP[c])))

                tm = hex(self.BITMAP[c])[2:]
                if len(tm) != 2:
                    tm = '0' + tm
                self.BITMAP_HEX += tm

    # Get a bitmap from str
    def __get_bitmap_from_str(self, bitmap):
        """Method that receive a bitmap str and transform it to ISO8583 object readable.
        @param: Bitmap -> bitmap str to be readable
        It's a internal method, so don't call!
        """
        # Need to check if the size is correct etc...
        cont = 0

        if self.BITMAP_HEX != '':
            self.BITMAP_HEX = ''

        for x in range(0, 32, 2):
            if (int(bitmap[0:2], 16) & self._BIT_POSITION_1) != self._BIT_POSITION_1:  # Only 1 bitmap
                if self.DEBUG:
                    print('Token[%d] %s converted to int is = %s' % (x, bitmap[x:x + 2], int(bitmap[x:x + 2], 16)))

                self.BITMAP_HEX += bitmap[x:x + 2]
                self.BITMAP[cont] = int(bitmap[x:x + 2], 16)
                if x == 14:
                    break
            else:  # Second bitmap
                if self.DEBUG:
                    print('Token[%d] %s converted to int is = %s' % (x, bitmap[x:x + 2], int(bitmap[x:x + 2], 16)))

                self.BITMAP_HEX += bitmap[x:x + 2]
                self.BITMAP[cont] = int(bitmap[x:x + 2], 16)
            cont += 1

    # print bit array that is present in the bitmap
    def show_bits_from_bitmap_str(self, bitmap):
        """Method that receive a bitmap str, process it, and print a array with bits this bitmap string represents.
        Usually is used to debug things.
        @param: Bitmap -> bitmap str to be analized and translated to "bits"
        """
        bits = self.__initialize_bits_from_bitmap_str(bitmap)
        print('Bits inside %s  = %s' % (bitmap, bits))

    # initialize a bitmap using ASCII str
    def __initialize_bits_from_bitmap_str(self, bitmap):
        """Method that receive a bitmap str, process it, and prepare ISO8583 object to understand and "see" the bits 
        and values inside the ISO ASCII package.
        It's a internal method, so don't call!
        @param: Bitmap -> bitmap str to be analyzed and translated to "bits"
        """

        print(bitmap)
        bits = []
        for c in range(0, 16):
            for d in range(1, 9):
                if self.DEBUG:
                    print('Value (%d)-> %s & %s = %s' % (
                        d, self.BITMAP[c], self._TMP[d], (self.BITMAP[c] & self._TMP[d])))
                if (self.BITMAP[c] & self._TMP[d]) == self._TMP[d]:
                    if d == 1:  # e o 8 bit
                        if self.DEBUG:
                            print('Bit %s is present !!!' % ((c + 1) * 8))
                        bits.append((c + 1) * 8)
                        self.BITMAP_VALUES[(c + 1) * 8] = 'X'
                    else:
                        if (c == 0) & (d == 2):  # Continuation bit
                            if self.DEBUG:
                                print('Bit 1 is present !!!')

                            bits.append(1)

                        else:
                            if self.DEBUG:
                                print('Bit %s is present !!!' % (c * 8 + d - 1))

                            bits.append(c * 8 + d - 1)
                            self.BITMAP_VALUES[c * 8 + d - 1] = 'X'
        bits.sort()
        return bits

    # return a array of bits, when processing the bitmap
    def __get_bits_from_bitmap(self):
        """Method that process the bitmap and return a array with the bits presents inside it.
        It's a internal method, so don't call!
        """
        bits = []
        for c in range(0, 16):
            for d in range(1, 9):
                if self.DEBUG:
                    print('Value (%d)-> %s & %s = %s' % (
                        d, self.BITMAP[c], self._TMP[d], (self.BITMAP[c] & self._TMP[d])))
                if (self.BITMAP[c] & self._TMP[d]) == self._TMP[d]:
                    if d == 1:  # e o 8 bit
                        if self.DEBUG:
                            print('Bit %s is present !!!' % ((c + 1) * 8))

                        bits.append((c + 1) * 8)
                    else:
                        if (c == 0) & (d == 2):  # Continuation bit
                            if self.DEBUG:
                                print('Bit 1 is present !!!')

                            bits.append(1)

                        else:
                            if self.DEBUG:
                                print('Bit %s is present !!!' % (c * 8 + d - 1))

                            bits.append(c * 8 + d - 1)

        bits.sort()

        return bits

    # Set of type LL
    def __set_bit_type_ll(self, bit, value):
        """Method that set a bit with value in form LL
        It put the size in front of the value
        Example: pack.set_bit(99,'123') -> Bit 99 is a LL type, so this bit, in ASCII form need to be 03123. 
        To understand, 03 is the size of the information and 123 is the information/value
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueToLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value

        if len(value) > 99:
            # value = value[0:99]
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.get_bit_type(bit), self.get_bit_limit(bit)))
        if len(value) > self.get_bit_limit(bit):
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.get_bit_type(bit), self.get_bit_limit(bit)))

        size = "%s" % len(value)

        self.BITMAP_VALUES[bit] = "%s%s" % (size.zfill(2), value)

    # Set of type LLL
    def __set_bit_type_lll(self, bit, value):
        """Method that set a bit with value in form LLL
        It put the size in front of the value
        Example: pack.set_bit(104,'12345ABCD67890') -> Bit 104 is a LLL type, so this bit, in ASCII form need 
            to be 01412345ABCD67890.
            To understand, 014 is the size of the information and 12345ABCD67890 is the information/value
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueToLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value

        if len(value) > 999:
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.get_bit_type(bit), self.get_bit_limit(bit)))
        if len(value) > self.get_bit_limit(bit):
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.get_bit_type(bit), self.get_bit_limit(bit)))

        size = "%s" % len(value)

        self.BITMAP_VALUES[bit] = "%s%s" % (size.zfill(3), value)

    # Set of type N,
    def __set_bit_type_n(self, bit, value):
        """Method that set a bit with value in form N
        It complete the size of the bit with a default value
        Example: pack.set_bit(3,'30000') -> Bit 3 is a N type, so this bit, in ASCII form need to has size = 6 
            (ISO specification) so the value 30000 size = 5 need to receive more "1" number.
            In this case, will be "0" in the left. In the package, the bit will be sent like '030000'
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueToLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value

        if len(value) > self.get_bit_limit(bit):
            # value = value[0:self.get_bit_limit(bit)]
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.get_bit_type(bit), self.get_bit_limit(bit)))

        self.BITMAP_VALUES[bit] = value.zfill(self.get_bit_limit(bit))

    # Set of type A
    def __set_bit_type_a(self, bit, value):
        """Method that set a bit with value in form A
        It completes the size of the bit with a default value
        Example: pack.set_bit(3,'30000') -> Bit 3 is a A type, so this bit, in ASCII form need to has size = 6 
            (ISO specification) so the value 30000 size = 5 need to receive more "1" number.
            In this case, will be "0" in the left. In the package, the bit will be sent like '030000'
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueToLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value

        if len(value) > self.get_bit_limit(bit):
            # value = value[0:self.get_bit_limit(bit)]
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.get_bit_type(bit), self.get_bit_limit(bit)))

        self.BITMAP_VALUES[bit] = value.zfill(self.get_bit_limit(bit))

    # Set of type B
    def __set_bit_type_b(self, bit, value):
        """Method that set a bit with value in form B
        It complete the size of the bit with a default value
        Example: pack.set_bit(3,'30000') -> Bit 3 is a B type, so this bit, in ASCII form need to has size = 6 
            (ISO specification) so the value 30000 size = 5 need to receive more "1" number.
            In this case, will be "0" in the left. In the package, the bit will be sent like '030000'
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueToLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value

        if len(value) > self.get_bit_limit(bit):
            # value = value[0:self.get_bit_limit(bit)]
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.get_bit_type(bit), self.get_bit_limit(bit)))

        self.BITMAP_VALUES[bit] = value.zfill(self.get_bit_limit(bit))

    # Set of type ANS
    def __set_bit_type_ans(self, bit, value):
        """Method that set a bit with value in form ANS
        It completes the size of the bit with a default value
        Example: pack.set_bit(3,'30000') -> Bit 3 is a ANS type, so this bit, in ASCII form need to has size = 6 
            (ISO specification) so the value 30000 size = 5 need to receive more "1" number.
            In this case, will be "0" in the left. In the package, the bit will be sent like '030000'
        @param: bit -> bit to be setted
        @param: value -> value to be setted
        @raise: ValueToLarge Exception
        It's a internal method, so don't call!
        """

        value = "%s" % value

        if len(value) > self.get_bit_limit(bit):
            # value = value[0:self.get_bit_limit(bit)]
            raise ValueToLarge('Error: value up to size! Bit[%s] of type %s limit size = %s' % (
                bit, self.get_bit_type(bit), self.get_bit_limit(bit)))

        self.BITMAP_VALUES[bit] = value.zfill(self.get_bit_limit(bit))

    # print os bits inside iso
    def show_iso_bits(self):
        """Method that show in detail a list of bits , values and types inside the object
        Example: output to
            (...)
            iso.set_bit(2,2)
            iso.set_bit(4,4)
            (...)
            iso.showIsoBits()
            (...)
            Bit[2] of type LL has limit 19 = 012
            Bit[4] of type N has limit 12 = 000000000004
            (...)
        """

        for cont in range(0, 129):
            if self.BITMAP_VALUES[cont] != self._BIT_DEFAULT_VALUE:
                print("Bit[%s] of type %s has limit %s = %s" % (
                    cont, self.get_bit_type(cont), self.get_bit_limit(cont), self.BITMAP_VALUES[cont]))

    # print Raw iso
    def show_raw_iso(self):
        """Method that print ISO8583 ASCII complete representation
        Example:
        iso = ISO8583()
        iso.set_mti('0800')
        iso.set_bit(2,2)
        iso.set_bit(4,4)
        iso.set_bit(12,12)
        iso.set_bit(17,17)
        iso.set_bit(99,99)
        iso.show_raw_iso()
        output (print) -> 0800d010800000000000000000002000000001200000000000400001200170299
        Hint: Try to use get_raw_iso method and format your own print :)
        """

        resp = self.get_raw_iso()
        print(resp)

    # Return raw iso
    def get_raw_iso(self):
        """Method that return ISO8583 ASCII complete representation
        Example:
        iso = ISO8583()
        iso.set_mti('0800')
        iso.set_bit(2,2)
        iso.set_bit(4,4)
        iso.set_bit(12,12)
        iso.set_bit(17,17)
        iso.set_bit(99,99)
        str = iso.get_raw_iso()
        print ('This is the ASCII package %s' % str)
        output (print) -> This is the ASCII package 0800d010800000000000000000002000000001200000000000400001200170299

        @return: str with complete ASCII ISO8583
        @raise: InvalidMTI Exception
        """

        self.__build_bitmap()

        if self.MESSAGE_TYPE_INDICATION == '':
            raise InvalidMTI('Check MTI! Do you set it?')

        resp = ""

        resp += self.MESSAGE_TYPE_INDICATION
        resp += self.BITMAP_HEX

        for cont in range(0, 129):
            if self.BITMAP_VALUES[cont] != self._BIT_DEFAULT_VALUE:
                resp = "%s%s" % (resp, self.BITMAP_VALUES[cont])

        return resp

    # Redefine a bit
    def redefine_bit(self, bit, small_str, large_str, bit_type, size, value_type):
        """Method that redefine a bit structure in global scope!
        Can be used to personalize ISO8583 structure to another specification (ISO8583 1987 for example!)
        Hint: If you have a lot of "ValueToLarge Exception" maybe the specification that you are using is different 
            of mine. So you will need to use this method :)
        @param: bit -> bit to be redefined
        @param: small_str -> a small String representantion of the bit, used to build "user friendly prints", 
            example "2" for bit 2
        @param: large_str -> a large String representantion of the bit, used to build "user friendly prints" and to be 
            used to inform the "main use of the bit",
            example "Primary account number (PAN)" for bit 2
        @param: bit_type -> type the bit, used to build the values, example "LL" for bit 2. Need to be one 
            of (B, N, AN, ANS, LL, LLL)
        @param: size -> limit size the bit, used to build/complete the values, example "19" for bit 2.
        @param: value_type -> value type the bit, used to "validate" the values, example "n" for bit 2. 
            This mean that in bit 2 we need to have only numeric values.
            Need to be one of (a, an, n, ansb, b)
        @raise: BitInexistent Exception, InvalidValueType Exception

        """

        if self.DEBUG:
            print('Trying to redefine the bit with (self,%s,%s,%s,%s,%s,%s)' % (
                bit, small_str, large_str, bit_type, size, value_type))

        # validating bit position
        if bit == 1 or bit == 64 or bit < 0 or bit > 128:
            raise BitInexistent("Error %d cannot be changed because has a invalid number!" % bit)

        # need to validate if the type and size is compatible! example slimit = 100 and type = LL

        if bit_type == "B" or bit_type == "N" or bit_type == "AN" or bit_type == "ANS" or bit_type == "LL" or bit_type == "LLL":
            if value_type == "a" or value_type == "n" or value_type == "ansb" or value_type == "ans" or value_type == "b" or value_type == "an":
                self._BITS_VALUE_TYPE[bit] = [small_str, large_str, bit_type, size, value_type]
                if self.DEBUG:
                    print('Bit %d redefined!' % bit)

            else:
                raise InvalidValueType(
                    "Error bit %d cannot be changed because %s is not a valid value_type (a, an, n ansb, b)!" % (
                        bit, value_type))
        # return
        else:
            raise InvalidBitType(
                "Error bit %d cannot be changed because %s is not a valid bit_type (Hex, N, AN, ANS, LL, LLL)!" % (
                    bit, bit_type))

    # return

    # a partir de um trem de string, pega o MTI
    def __set_mti_from_str(self, iso):
        """Method that get the first 4 characters to be the MTI.
        It's a internal method, so don't call!
        """

        self.MESSAGE_TYPE_INDICATION = iso[0:4]

        if self.DEBUG:
            print('MTI found was %s' % self.MESSAGE_TYPE_INDICATION)

    # return the MTI
    def get_mti(self):
        """Method that return the MTI of the package
        @return: str -> with the MTI
        """

        # Need to validate if the MTI was setted ...etc ...
        return self.MESSAGE_TYPE_INDICATION

    # Return the bitmap
    def get_bitmap(self):
        """Method that return the ASCII Bitmap of the package
        @return: str -> with the ASCII Bitmap
        """
        if self.BITMAP_HEX == '':
            self.__build_bitmap()

        return self.BITMAP_HEX

    # return the Varray of values
    def get_values_array(self):
        """Method that return an internal array of the package
        @return: array -> with all bits, presents or not in the bitmap
        """
        return self.BITMAP_VALUES

    # Receive a str and interpret it to bits and values
    def __get_bit_from_str(self, str_without_mti_bitmap):
        """Method that receive a string (ASCII) without MTI and Bitmaps (first and second), understand it and remove 
            the bits values
        @param: str -> with all bits presents without MTI and bitmap
        It's a internal method, so don't call!
        """

        if self.DEBUG:
            print('This is the input string <%s>' % str_without_mti_bitmap)

        offset = 0
        # jump bit 1 because it was alread defined in the "__initialize_bits_from_bitmap_str"
        for cont in range(2, 129):
            if self.BITMAP_VALUES[cont] != self._BIT_DEFAULT_VALUE:
                if self.DEBUG:
                    print('String = %s offset = %s bit = %s' % (str_without_mti_bitmap[offset:], offset, cont))

                if self.get_bit_type(cont) == 'LL':
                    value_size = int(str_without_mti_bitmap[offset:offset + 2])
                    if self.DEBUG:
                        print('Size of the message in LL = %s' % value_size)

                    if value_size > self.get_bit_limit(cont):
                        raise ValueToLarge("This bit is larger than the specification!")
                    self.BITMAP_VALUES[cont] = (str_without_mti_bitmap[offset:offset + 2] +
                                                str_without_mti_bitmap[offset + 2:offset + 2 + value_size])

                    if self.DEBUG:
                        print('\tSetting bit %s value %s' % (cont, self.BITMAP_VALUES[cont]))

                    offset += value_size + 2

                if self.get_bit_type(cont) == 'LLL':
                    value_size = int(str_without_mti_bitmap[offset:offset + 3])
                    if self.DEBUG:
                        print('Size of the message in LLL = %s' % value_size)

                    if value_size > self.get_bit_limit(cont):
                        raise ValueToLarge("This bit is larger than the specification!")
                    self.BITMAP_VALUES[cont] = (str_without_mti_bitmap[offset:offset + 3] +
                                                str_without_mti_bitmap[offset + 3:offset + 3 + value_size])

                    if self.DEBUG:
                        print('\tSetting bit %s value %s' % (cont, self.BITMAP_VALUES[cont]))

                    offset += value_size + 3

                # if self.get_bit_type(cont) == 'LLLL':
                # value_size = int(str_without_mti_bitmap[offset:offset +4])
                # if value_size > self.get_bit_limit(cont):
                # raise ValueToLarge("This bit is larger than the specification!")
                # self.BITMAP_VALUES[cont] = '(' + str_without_mti_bitmap[offset:offset+4] + ')' + 
                # str_without_mti_bitmap[offset+4:offset+4+value_size]
                # offset += value_size + 4

                if self.get_bit_type(cont) == 'N' or self.get_bit_type(cont) == 'A' or self.get_bit_type(
                        cont) == 'ANS' or self.get_bit_type(cont) == 'B' or self.get_bit_type(cont) == 'AN':
                    self.BITMAP_VALUES[cont] = str_without_mti_bitmap[offset:self.get_bit_limit(cont) + offset]

                    if self.DEBUG:
                        print('\tSetting bit %s value %s' % (cont, self.BITMAP_VALUES[cont]))

                    offset += self.get_bit_limit(cont)

    # Parse a ASCII iso to object
    def set_iso_content(self, iso):
        """Method that receive a complete ISO8583 string (ASCII) understand it and remove the bits values
        Example:
            iso = '0210B238000102C080040000000000000002100000000000001700010814465469421614465701081100301000000N399915444303500019991544986020   Value not allowed009000095492'
            i2 = ISO8583()
            # in this case, we need to redefine a bit because default bit 42 is LL and in this specification is "N"
            # the rest remain, so we use "get" :)
            i2.redefine_bit(42, '42', i2.get_large_bit_name(42), 'N', i2.get_bit_limit(42), i2.get_bit_value_type(42) )
            i2.set_iso_content(iso2)
            print ('Bitmap = %s' %i2.get_bitmap())
            print ('MTI = %s' %i2.get_mti() )

            print ('This ISO has bits:')
            v3 = i2.get_bits_and_values()
            for v in v3:
                print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))

        @param: str -> complete ISO8583 string
        @raise: InvalidIso8583 Exception
        """
        if len(iso) < 20:
            raise InvalidIso8583('This is not a valid iso!!')
        if self.DEBUG:
            print('ASCII to process <%s>' % iso)

        self.__set_mti_from_str(iso)
        iso_t = iso[4:]
        self.__get_bitmap_from_str(iso_t)
        self.__initialize_bits_from_bitmap_str(self.BITMAP_HEX)
        if self.DEBUG:
            print('This is the array of bits (before) %s ' % self.BITMAP_VALUES)

        self.__get_bit_from_str(iso[4 + len(self.BITMAP_HEX):])
        if self.DEBUG:
            print('This is the array of bits (after) %s ' % self.BITMAP_VALUES)

    # Method that compare 2 iso's
    def __cmp__(self, obj2):
        """Method that compare two objects in "==", "!=" and other things
        Example:
            p1 = ISO8583()
            p1.set_mti('0800')
            p1.set_bit(2,2)
            p1.set_bit(4,4)
            p1.set_bit(12,12)
            p1.set_bit(17,17)
            p1.set_bit(99,99)

            #get the rawIso and save in the iso variable
            iso = p1.get_raw_iso()

            p2 = ISO8583()
            p2.set_iso_content(iso)

            print ('Is equivalent?')
            if p1 == p1:
                print ('Yes :)')
            else:
                print ('Noooooooooo :(')

        @param: obj2 -> object that will be compared
        @return: <0 if is not equal, 0 if is equal
        """
        ret = -1  # By default is different
        if (self.get_mti() == obj2.get_mti()) and (self.get_bitmap() == obj2.get_bitmap()) and (
                self.get_values_array() == obj2.get_values_array()):
            ret = 0

        return ret

    # Method that return a array with bits and values inside the iso package
    def get_bits_and_values(self):
        """Method that return an array of bits, values, types etc.
            Each array value is a dictionary with: {'bit':X ,'type': Y, 'value': Z} Where:
                bit: is the bit number
                type: is the bit type
                value: is the bit value inside this object
            so the Generic array returned is:  [ (...),{'bit':X,'type': Y, 'value': Z}, (...)]

        Example:
            p1 = ISO8583()
            p1.set_mti('0800')
            p1.set_bit(2,2)
            p1.set_bit(4,4)
            p1.set_bit(12,12)
            p1.set_bit(17,17)
            p1.set_bit(99,99)

            v1 = p1.get_bits_and_values()
            for v in v1:
                print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))

        @return: array of values.
        """
        ret = []
        for cont in range(2, 129):
            if self.BITMAP_VALUES[cont] != self._BIT_DEFAULT_VALUE:
                _TMP = {'bit': "%d" % cont, 'type': self.get_bit_type(cont), 'value': self.BITMAP_VALUES[cont]}
                ret.append(_TMP)
        return ret

    # Method that return a array with bits and values inside the iso package
    def get_bit(self, bit):
        """Return the value of the bit
        @param: bit -> the number of the bit that you want the value
        @raise: BitInexistent Exception, BitNotSet Exception
        """

        if bit < 1 or bit > 128:
            raise BitInexistent("Bit number %s doesn't exist!" % bit)

        # Is that bit set?
        is_there = False
        arr = self.__get_bits_from_bitmap()

        if self.DEBUG:
            print('This is the array of bits inside the bitmap %s' % arr)
        value = None
        for v in arr:
            if v == bit:
                value = self.BITMAP_VALUES[bit]
                is_there = True
                break

        if is_there:
            return value
        else:
            raise BitNotSet("Bit number %s was not set!" % bit)

    # Method that return ISO8583 to a TCPIP network form with the size in the beginning.
    def get_network_iso(self, big_endian=True):
        """Method that return ISO8583 ASCII package with the size in the beginning
        By default, it return the package with size represented with big-endian.
        Is the same that:
            import struct
            (...)
            iso = ISO8583()
            iso.set_bit(3,'300000')
            (...)
            ascii = iso.get_raw_iso()
            # Example: big-endian
            # To little-endian, replace '!h' with '<h'
            net_iso = struct.pack('!h',len(iso))
            net_iso += ascii
            # Example: big-endian
            # To little-endian, replace 'iso.get_network_iso()' with 'iso.get_network_iso(False)'
            print ('This <%s> the same that <%s>' % (iso.get_network_iso(),net_iso))

        @param: big_endian (True|False) -> if you want that the size be represented in this way.
        @return: size + ASCII ISO8583 package ready to go to the network!
        @raise: InvalidMTI Exception
        """

        ascii_iso = self.get_raw_iso()

        if big_endian:
            net_iso = struct.pack('!h', len(ascii_iso))
            if self.DEBUG:
                print('Pack Big-endian')
        else:
            net_iso = struct.pack('<h', len(ascii_iso))
            if self.DEBUG:
                print('Pack Little-endian')

        net_iso += ascii_iso

        return net_iso

    # Method that receive a ISO8583 ASCII package in the network form and parse it.
    def set_network_iso(self, iso, big_endian=True):
        """Method that receive sie + ASCII ISO8583 package and transform it in the ISO8583 object.
            By default, it receives the package with size represented with big-endian.
            Is the same that:
            import struct
            (...)
            iso = ISO8583()
            iso.set_bit(3,'300000')
            (...)
            # Example: big-endian
            # To little-endian, replace 'iso.get_network_iso()' with 'iso.get_network_iso(False)'
            net_iso = iso.get_network_iso()
            newIso = ISO8583()
            # Example: big-endian
            # To little-endian, replace 'newIso.set_network_iso()' with 'newIso.set_network_iso(False)'
            newIso.set_network_iso(net_iso)
            #Is the same that:
            #size = net_iso[0:2]
            ## To little-endian, replace '!h' with '<h'
            #size = struct.unpack('!h',size )
            #newIso.set_iso_content(net_iso[2:size])
            arr = newIso.get_bits_and_values()
            for v in arr:
                print ('Bit %s Type %s Value = %s' % (v['bit'],v['type'],v['value']))

            @param: Iso -> str that represents size + ASCII ISO8583 package
            @param: big_endian (True|False) -> Codification of the size.
            @raise: InvalidIso8583 Exception
        """

        if len(iso) < 24:
            raise InvalidIso8583('This is not a valid iso!!Invalid Size')

        size = iso[0:2]
        if big_endian:
            size = struct.unpack('!h', size)
            if self.DEBUG:
                print('Unpack Big-endian')
        else:
            size = struct.unpack('<h', size)
            if self.DEBUG:
                print('Unpack Little-endian')

        if len(iso) != (size[0] + 2):
            raise InvalidIso8583(
                'This is not a valid iso!!The ISO8583 ASCII(%s) is less than the size %s!' % (len(iso[2:]), size[0]))

        self.set_iso_content(iso[2:])
