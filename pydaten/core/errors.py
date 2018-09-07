class BlockchainException(Exception):
    def __init__(self, message):
        super().__init__(message)

class BlockNotFound(BlockchainException):
    def __init__(self):
        super().__init__('Block not found.')

class BlockTooLarge(BlockchainException):
    def __init__(self):
        super().__init__('Block too large.')

class InvalidBlock(BlockchainException):
    def __init__(self):
        super().__init__('Block structure invalid.')

class BlockOld(BlockchainException):
    def __init__(self):
        super().__init__('Block is old.')

class InvalidIndex(BlockchainException):
    def __init__(self):
        super().__init__('Block index invalid.')

class InvalidPreviousHash(BlockchainException):
    def __init__(self):
        super().__init__('Block hash invalid.')

class InvalidTimestamp(BlockchainException):
    def __init__(self):
        super().__init__('Block timestamp invalid.')

class InvalidDifficulty(BlockchainException):
    def __init__(self):
        super().__init__('Block difficulty invalid.')

class InvalidTransaction(BlockchainException):
    def __init__(self):
        super().__init__('Transaction structure invalid.')

class NotSupportedTransaction(BlockchainException):
    def __init__(self):
        super().__init__('Transaction not supported in this version of software.')

class InvalidTransactionTarget(BlockchainException):
    def __init__(self):
        super().__init__('Transaction not targeting this block.')

class DuplicatedTransactionsFound(BlockchainException):
    def __init__(self):
        super().__init__('Duplicated transactions found.')

class NameTaken(BlockchainException):
    def __init__(self):
        super().__init__('Name taken.')

class InvalidTransactionSource(BlockchainException):
    def __init__(self):
        super().__init__('Transaction source invalid.')

class InvalidTransactionDestination(BlockchainException):
    def __init__(self):
        super().__init__('Transaction destination invalid.')

class InvalidTransactionSignature(BlockchainException):
    def __init__(self):
        super().__init__('Transaction signature mismatch.')

class InvalidFeeTransaction(BlockchainException):
    def __init__(self):
        super().__init__('Fee transaction invalid.')

class InvalidRewardTransaction(BlockchainException):
    def __init__(self):
        super().__init__('Reward transaction invalid.')

class BalanceNotEnough(BlockchainException):
    def __init__(self):
        super().__init__('Not enough balance.')

class MerkleTreeException(Exception):
    def __init__(self, message):
        super().__init__(message)

class HashNotFound(MerkleTreeException):
    def __init__(self):
        super().__init__('Hash not found in merkle tree leaves.')
