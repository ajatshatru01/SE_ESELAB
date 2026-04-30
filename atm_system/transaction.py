"""
ATM Banking System - Transaction Entity
CRC Role: Record transaction details, maintain transaction status
Collaborators: Account, WithdrawController
"""

import uuid
from datetime import datetime
from enum import Enum


class TransactionStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED  = "FAILED"
    PENDING = "PENDING"


class TransactionType(Enum):
    WITHDRAWAL = "WITHDRAWAL"
    BALANCE_ENQUIRY = "BALANCE_ENQUIRY"
    FUND_TRANSFER  = "FUND_TRANSFER"


class Transaction:
    """
    Entity object representing a single ATM transaction.
    Records all relevant details and maintains final status.
    """

    def __init__(
        self,
        account_number: str,
        txn_type: TransactionType,
        amount: float = 0.0,
    ):
        self._txn_id        = str(uuid.uuid4())[:8].upper()
        self._account_number = account_number
        self._txn_type      = txn_type
        self._amount        = amount
        self._timestamp     = datetime.now()
        self._status        = TransactionStatus.PENDING
        self._message       = ""

    # ------------------------------------------------------------------ #
    #  Properties                                                          #
    # ------------------------------------------------------------------ #
    @property
    def txn_id(self) -> str:
        return self._txn_id

    @property
    def status(self) -> TransactionStatus:
        return self._status

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def txn_type(self) -> TransactionType:
        return self._txn_type

    @property
    def message(self) -> str:
        return self._message

    # ------------------------------------------------------------------ #
    #  Behaviour                                                           #
    # ------------------------------------------------------------------ #
    def mark_success(self, message: str = "Transaction successful") -> None:
        """Marks the transaction as successful."""
        self._status  = TransactionStatus.SUCCESS
        self._message = message

    def mark_failed(self, reason: str = "Transaction failed") -> None:
        """Marks the transaction as failed with a reason."""
        self._status  = TransactionStatus.FAILED
        self._message = reason

    def get_receipt(self) -> str:
        """Generates a formatted receipt string for the transaction."""
        line = "-" * 40
        receipt = (
            f"\n{line}\n"
            f"       NATIONAL BANK ATM RECEIPT\n"
            f"{line}\n"
            f"  Transaction ID : {self._txn_id}\n"
            f"  Account        : {'*' * 8}{self._account_number[-4:]}\n"
            f"  Type           : {self._txn_type.value}\n"
            f"  Amount         : Rs. {self._amount:,.2f}\n"
            f"  Date & Time    : {self._timestamp.strftime('%d-%m-%Y %H:%M:%S')}\n"
            f"  Status         : {self._status.value}\n"
            f"  Message        : {self._message}\n"
            f"{line}\n"
            f"     Thank you for banking with us!\n"
            f"{line}\n"
        )
        return receipt

    def __repr__(self) -> str:
        return (
            f"Transaction(id={self._txn_id}, type={self._txn_type.value}, "
            f"amount={self._amount}, status={self._status.value})"
        )
