#!/usr/bin/env python

class SequenceNumber(object):
    """
    Sequence numbers are a form of comparable wrapping numbers.
    See http://tools.ietf.org/html/rfc1982
    """
    SERIAL_BITS = 16

    def __init__(self, val=0):
        self.val = val

    def increment(self):
        "Increment the value by one with wrap around"
        self.val = (self.val + 1) % (2**SequenceNumber.SERIAL_BITS)

    def _compare(self, oth):
        if (self.val < oth.val and oth.val - self.val < 2^(SequenceNumber.SERIAL_BITS - 1)) \
                or (self.val > oth.val and self.val - oth.val > 2^(SequenceNumber.SERIAL_BITS - 1)):
            return -1
        elif (self.val < oth.val and oth.val - self.val > 2^(SequenceNumber.SERIAL_BITS - 1)) \
                or (self.val > oth.val and self.val - oth.val < 2^(SequenceNumber.SERIAL_BITS - 1)):
            return 1
        else:
            return 0 # TODO: Check if this is completely right

    def __lt__(self, other):
        "Override < comparison"
        return self._compare(other) < 0
    def __le__(self, other):
        "Override <= comparison"
        return self._compare(other) <= 0

    def __gt__(self, other):
        "Override > comparison"
        return self._compare(other) > 0
    def __ge__(self, other):
        "Override >= comparison"
        return self._compare(other) >= 0
    
