"""
ATM Banking System - Custom Exceptions
Aligned with Use Case Specification (Alternate Flows & Exceptions)
"""


class InsufficientFundsError(Exception):
    """Raised when account balance is less than withdrawal amount."""
    pass


class CardBlockedError(Exception):
    """Raised when card is blocked due to consecutive PIN failures."""
    pass


class AuthenticationError(Exception):
    """Raised when PIN verification fails (but card not yet blocked)."""
    def __init__(self, message="Invalid PIN", attempts_remaining=None):
        self.attempts_remaining = attempts_remaining
        super().__init__(message)


class ATMOutOfCashError(Exception):
    """Raised when ATM does not have sufficient cash to dispense."""
    pass


class ServerError(Exception):
    """Raised when bank server is not responding."""
    pass


class SessionTimeoutError(Exception):
    """Raised when the customer session expires due to inactivity."""
    pass


class InvalidAmountError(Exception):
    """Raised when the withdrawal amount is invalid (zero, negative, non-multiple)."""
    pass


class ATMOfflineError(Exception):
    """Raised when the ATM is not operational or disconnected."""
    pass
