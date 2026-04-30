"""
ATM Banking System - ATM_UI (Boundary Object)
CRC Role: Accept user input, display messages
Collaborators: WithdrawController, AuthController
"""

import time
import getpass

from atm_system.card               import Card
from atm_system.account            import Account
from atm_system.auth_controller    import AuthController
from atm_system.withdraw_controller import WithdrawController
from atm_system.exceptions         import (
    AuthenticationError,
    CardBlockedError,
    ATMOutOfCashError,
    InsufficientFundsError,
    InvalidAmountError,
    ServerError,
    SessionTimeoutError,
)

SESSION_TIMEOUT_SECONDS = 60   # 60-second idle timeout


class ATM_UI:
    """
    Boundary object providing the command-line interface for the ATM.
    Drives the full Withdraw Cash flow as defined in the Sequence Diagram.
    """

    def __init__(
        self,
        auth_controller: AuthController,
        withdraw_controller: WithdrawController,
    ):
        self._auth     = auth_controller
        self._withdraw = withdraw_controller
        self._last_activity = time.time()

    # ------------------------------------------------------------------ #
    #  Display helpers                                                     #
    # ------------------------------------------------------------------ #
    def _banner(self) -> None:
        print("\n" + "=" * 44)
        print("        NATIONAL BANK ATM SYSTEM")
        print("=" * 44)

    def _display(self, msg: str) -> None:
        print(f"  {msg}")

    def _check_timeout(self) -> None:
        if time.time() - self._last_activity > SESSION_TIMEOUT_SECONDS:
            self._auth.end_session()
            raise SessionTimeoutError("Session timed out due to inactivity. Please re-insert your card.")

    def _touch(self) -> None:
        """Reset inactivity timer on every user interaction."""
        self._last_activity = time.time()

    # ------------------------------------------------------------------ #
    #  Step 1 – Card Insertion (simulated)                                 #
    # ------------------------------------------------------------------ #
    def insert_card(self, card: Card) -> bool:
        """Simulates card insertion and reads card details."""
        self._banner()
        self._display(f"Card inserted: ****{card.card_number[-4:]}")
        self._display("Reading card details...")
        self._touch()
        return True

    # ------------------------------------------------------------------ #
    #  Step 2 – PIN Entry                                                  #
    # ------------------------------------------------------------------ #
    def enter_pin(self, card: Card, pin_override: str = None) -> bool:
        """
        Prompts the customer for their PIN (masked input).
        pin_override is used by automated tests to bypass getpass.
        Returns True on successful authentication.
        """
        self._display("")
        while True:
            self._check_timeout()
            try:
                if pin_override is not None:
                    entered = pin_override
                    self._display("PIN: [hidden]")
                else:
                    entered = getpass.getpass("  Enter PIN: ")
                self._touch()
                self._auth.authenticate(card, entered)
                self._display("✔  Authentication successful.")
                return True
            except AuthenticationError as e:
                self._display(f"✘  {e}")
                if pin_override is not None:
                    raise   # don't loop in automated mode
            except CardBlockedError as e:
                self._display(f"✘  {e}")
                raise
            except ServerError as e:
                self._display(f"✘  {e}")
                raise

    # ------------------------------------------------------------------ #
    #  Step 3 – Transaction Menu                                           #
    # ------------------------------------------------------------------ #
    def show_menu(self) -> str:
        """Displays the transaction options and returns customer's choice."""
        self._check_timeout()
        self._display("")
        self._display("Select Transaction:")
        self._display("  1. Cash Withdrawal")
        self._display("  2. Balance Enquiry")
        self._display("  3. Exit")
        choice = input("  Enter choice (1/2/3): ").strip()
        self._touch()
        return choice

    # ------------------------------------------------------------------ #
    #  Step 4 – Amount Entry                                               #
    # ------------------------------------------------------------------ #
    def select_amount(self, amount_override: float = None) -> float:
        """
        Prompts the customer for the withdrawal amount.
        amount_override is used by automated tests.
        """
        self._check_timeout()
        if amount_override is not None:
            self._display(f"Withdrawal amount entered: Rs. {amount_override:,.2f}")
            self._touch()
            return amount_override
        try:
            raw = input("  Enter withdrawal amount (Rs.): ").strip()
            self._touch()
            return float(raw)
        except ValueError:
            raise InvalidAmountError("Non-numeric amount entered.")

    # ------------------------------------------------------------------ #
    #  Step 5 – Process Withdrawal                                         #
    # ------------------------------------------------------------------ #
    def process_withdrawal(self, account: Account, amount: float) -> None:
        """
        Calls WithdrawController, displays result, and prints receipt.
        Mirrors Sequence Diagram steps 7–11.
        """
        self._display(f"\n  Processing withdrawal of Rs. {amount:,.2f}...")
        try:
            txn = self._withdraw.process_withdrawal(account, amount)
            self._display("✔  Cash dispensed. Please collect your cash.")
            print(txn.get_receipt())
        except InvalidAmountError as e:
            self._display(f"✘  Invalid amount: {e}")
        except ATMOutOfCashError as e:
            self._display(f"✘  ATM error: {e}")
        except InsufficientFundsError as e:
            self._display(f"✘  {e}")
        except ServerError as e:
            self._display(f"✘  Server error: {e}")

    # ------------------------------------------------------------------ #
    #  Step 6 – Logout                                                     #
    # ------------------------------------------------------------------ #
    def logout(self) -> None:
        """Ends the session and ejects the card."""
        self._auth.end_session()
        self._display("\n  Session ended. Please collect your card.")
        self._display("  Thank you for banking with National Bank!\n")
        print("=" * 44 + "\n")
