"""
ATM Banking System - Account Entity
CRC Role: Maintain balance, debit amount
Collaborators: WithdrawController
"""

from atm_system.exceptions import InsufficientFundsError


class Account:
    """
    Entity object representing a customer's bank account.
    Maintains the balance and supports debiting for withdrawals.
    """

    def __init__(self, account_number: str, owner_name: str, balance: float):
        if balance < 0:
            raise ValueError("Initial balance cannot be negative.")
        self._account_number = account_number
        self._owner_name = owner_name
        self._balance = balance

    # ------------------------------------------------------------------ #
    #  Properties                                                          #
    # ------------------------------------------------------------------ #
    @property
    def account_number(self) -> str:
        return self._account_number

    @property
    def owner_name(self) -> str:
        return self._owner_name

    @property
    def balance(self) -> float:
        return self._balance

    # ------------------------------------------------------------------ #
    #  Behaviour                                                           #
    # ------------------------------------------------------------------ #
    def get_balance(self) -> float:
        """Returns the current available balance."""
        return self._balance

    def debit(self, amount: float) -> float:
        """
        Deducts the specified amount from the account balance.
        Raises InsufficientFundsError if balance is too low.
        Returns the new balance after deduction.
        """
        if amount <= 0:
            raise ValueError("Debit amount must be positive.")
        if amount > self._balance:
            raise InsufficientFundsError(
                f"Insufficient funds. Available: {self._balance:.2f}, Requested: {amount:.2f}"
            )
        self._balance -= amount
        return self._balance

    def credit(self, amount: float) -> float:
        """Credits amount back to account (e.g., on transaction reversal)."""
        if amount <= 0:
            raise ValueError("Credit amount must be positive.")
        self._balance += amount
        return self._balance

    def __repr__(self) -> str:
        return f"Account({self._account_number}, owner={self._owner_name}, balance={self._balance:.2f})"
