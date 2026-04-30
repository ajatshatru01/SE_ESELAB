"""
ATM Banking System - WithdrawController (Control Object)
CRC Role: Process withdrawal request, coordinate transaction
Collaborators: Account, Bank Server (simulated)
"""

from atm_system.account     import Account
from atm_system.transaction import Transaction, TransactionType
from atm_system.exceptions  import (
    ATMOutOfCashError,
    InvalidAmountError,
    InsufficientFundsError,
    ServerError,
)

# Minimum denomination the ATM dispenses (Rs. 100)
MIN_DENOMINATION = 100


class WithdrawController:
    """
    Control object that orchestrates the full cash withdrawal process.

    Sequence Diagram mapping:
      ATM_UI → WithdrawController.process_withdrawal()
      WithdrawController → BankServer.verifyTransaction()  [simulated]
      BankServer → WithdrawController : approve/deny
      WithdrawController → ATM_UI : allowWithdrawal()
      ATM_UI → Customer : dispenseCash()
    """

    def __init__(self, atm_cash_available: float, bank_server_online: bool = True):
        self._atm_cash          = atm_cash_available
        self._bank_server_online = bank_server_online

    # ------------------------------------------------------------------ #
    #  Properties                                                          #
    # ------------------------------------------------------------------ #
    @property
    def atm_cash(self) -> float:
        return self._atm_cash

    # ------------------------------------------------------------------ #
    #  Behaviour                                                           #
    # ------------------------------------------------------------------ #
    def process_withdrawal(self, account: Account, amount: float) -> Transaction:
        """
        Core use-case method: Withdraw Cash.

        Steps:
          1. Validate amount (positive, multiple of MIN_DENOMINATION)
          2. Check ATM has sufficient cash
          3. Simulate bank server verification
          4. Check account has sufficient balance
          5. Debit account
          6. Dispense cash (decrement ATM cash)
          7. Record and return Transaction

        Returns a Transaction with status SUCCESS.
        Raises appropriate exceptions on failure.
        """
        txn = Transaction(
            account_number=account.account_number,
            txn_type=TransactionType.WITHDRAWAL,
            amount=amount,
        )

        try:
            # Step 1 – Validate amount
            self._validate_amount(amount)

            # Step 2 – Check ATM cash
            if amount > self._atm_cash:
                raise ATMOutOfCashError(
                    f"ATM has insufficient cash. Available: Rs.{self._atm_cash:.2f}, "
                    f"Requested: Rs.{amount:.2f}"
                )

            # Step 3 – Simulate bank server transaction verification
            if not self._bank_server_online:
                raise ServerError("Bank server unavailable. Cannot process transaction.")

            # Step 4 + 5 – Check balance and debit (raises InsufficientFundsError)
            account.debit(amount)

            # Step 6 – Dispense cash
            self._atm_cash -= amount

            # Step 7 – Record success
            txn.mark_success(
                f"Rs. {amount:,.2f} dispensed successfully. "
                f"Remaining balance: Rs. {account.balance:,.2f}"
            )

        except (InvalidAmountError, ATMOutOfCashError, ServerError,
                InsufficientFundsError) as exc:
            txn.mark_failed(str(exc))
            raise  # re-raise so caller/UI can handle

        return txn

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #
    def _validate_amount(self, amount: float) -> None:
        """
        Ensures the requested amount is:
          - greater than zero
          - a whole number (no fractional currency)
          - a multiple of MIN_DENOMINATION (Rs. 100)
        """
        if amount <= 0:
            raise InvalidAmountError(
                f"Withdrawal amount must be greater than zero. Got: {amount}"
            )
        if amount != int(amount):
            raise InvalidAmountError(
                f"Withdrawal amount must be a whole number. Got: {amount}"
            )
        if int(amount) % MIN_DENOMINATION != 0:
            raise InvalidAmountError(
                f"Amount must be a multiple of Rs.{MIN_DENOMINATION}. Got: {amount}"
            )

    def replenish_cash(self, amount: float) -> None:
        """Maintenance operation: add cash to the ATM cassette."""
        if amount <= 0:
            raise ValueError("Replenishment amount must be positive.")
        self._atm_cash += amount

    def __repr__(self) -> str:
        return f"WithdrawController(atm_cash={self._atm_cash}, server_online={self._bank_server_online})"
