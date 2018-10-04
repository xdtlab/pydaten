class CommonException(Exception):
    def __init__(self, message):
        super().__init__(message)

class TransactionCorrupted(CommonException):
    def __init__(self):
        super().__init__('Transaction is corrupted!')

class BlockCorrupted(CommonException):
    def __init__(self):
        super().__init__('Block is corrupted!')
