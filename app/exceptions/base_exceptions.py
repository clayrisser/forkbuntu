from exceptions import BaseException

class DefaultException(BaseException):
    known = True
    def __init__(self, message):
        self.message = message
