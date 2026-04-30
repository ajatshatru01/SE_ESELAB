"""
ATM Banking System - White Box Test Cases (15)
Tests the Withdraw Cash use case from the INTERNAL perspective.
Exercises specific branches, conditions, loops, and paths in the code.

Run:
    python -m pytest test_white_box.py -v
"""

import unittest
from atm_system.card                import Card, MAX_PIN_ATTEMPTS
from atm_system.account             import Account
from atm_system.auth_controller     import AuthController
from atm_system.withdraw_controller import WithdrawController, MIN_DENOMINATION
from atm_system.transaction         import Transaction, TransactionStatus, TransactionType
from atm_system.exceptions          import (
    AuthenticationError,
    CardBlockedError,
    InsufficientFundsError,
    ATMOutOfCashError,
    InvalidAmountError,
    ServerError,
)


def make_card(pin="1234"):
    return Card("4111111111111111", pin, "ACC001")

def make_account(balance=10000.0):
    return Account("ACC001", "Alice Johnson", balance)

def make_wc(atm_cash=50000.0, server=True):
    return WithdrawController(atm_cash, server)


class TestWhiteBox(unittest.TestCase):

    # ------------------------------------------------------------------ #
    #  WB-TC-01: Card._failed_attempts increments correctly (Card logic)  #
    # ------------------------------------------------------------------ #
    def test_wb_01_failed_attempts_counter(self):
        """
        Branch: Card.increment_failed_attempts()
        Each wrong attempt increments _failed_attempts by exactly 1.
        """
        card = make_card()
        self.assertEqual(card.failed_attempts, 0)
        card.increment_failed_attempts()
        self.assertEqual(card.failed_attempts, 1)
        card.increment_failed_attempts()
        self.assertEqual(card.failed_attempts, 2)

    # ------------------------------------------------------------------ #
    #  WB-TC-02: Card blocks exactly at MAX_PIN_ATTEMPTS (boundary)       #
    # ------------------------------------------------------------------ #
    def test_wb_02_block_at_max_attempts(self):
        """
        Branch: MAX_PIN_ATTEMPTS threshold in increment_failed_attempts().
        Card must be blocked at attempt == MAX_PIN_ATTEMPTS (3), not before.
        """
        card = make_card()
        for i in range(MAX_PIN_ATTEMPTS - 1):
            card.increment_failed_attempts()
            self.assertFalse(card.is_blocked, f"Should not be blocked after {i+1} attempts")

        card.increment_failed_attempts()
        self.assertTrue(card.is_blocked)

    # ------------------------------------------------------------------ #
    #  WB-TC-03: Card.reset_failed_attempts() zeroes the counter          #
    # ------------------------------------------------------------------ #
    def test_wb_03_reset_failed_attempts(self):
        """
        Branch: successful auth resets _failed_attempts via reset_failed_attempts().
        """
        card = make_card()
        card.increment_failed_attempts()
        card.increment_failed_attempts()
        self.assertEqual(card.failed_attempts, 2)

        card.reset_failed_attempts()
        self.assertEqual(card.failed_attempts, 0)

    # ------------------------------------------------------------------ #
    #  WB-TC-04: Card.validate_pin() returns False for wrong PIN          #
    # ------------------------------------------------------------------ #
    def test_wb_04_validate_pin_false(self):
        """
        Branch: PIN comparison → False path in Card.validate_pin().
        """
        card = make_card("1234")
        self.assertFalse(card.validate_pin("0000"))

    # ------------------------------------------------------------------ #
    #  WB-TC-05: Card.validate_pin() raises on blocked card               #
    # ------------------------------------------------------------------ #
    def test_wb_05_validate_pin_raises_when_blocked(self):
        """
        Branch: is_blocked guard at top of Card.validate_pin().
        """
        card = make_card("1234")
        card.block()
        with self.assertRaises(CardBlockedError):
            card.validate_pin("1234")

    # ------------------------------------------------------------------ #
    #  WB-TC-06: Account.debit() reduces balance exactly                  #
    # ------------------------------------------------------------------ #
    def test_wb_06_account_debit_reduces_balance(self):
        """
        Path: Account.debit() success path – balance decremented by exact amount.
        """
        account = make_account(10000)
        new_bal = account.debit(3000)
        self.assertAlmostEqual(new_bal, 7000.0)
        self.assertAlmostEqual(account.balance, 7000.0)

    # ------------------------------------------------------------------ #
    #  WB-TC-07: Account.debit() raises when amount > balance             #
    # ------------------------------------------------------------------ #
    def test_wb_07_account_debit_raises_insufficient(self):
        """
        Branch: amount > self._balance guard in Account.debit().
        """
        account = make_account(100)
        with self.assertRaises(InsufficientFundsError):
            account.debit(200)

    # ------------------------------------------------------------------ #
    #  WB-TC-08: Account.debit() raises on zero or negative amount        #
    # ------------------------------------------------------------------ #
    def test_wb_08_account_debit_non_positive(self):
        """
        Branch: amount <= 0 guard in Account.debit().
        """
        account = make_account(10000)
        with self.assertRaises(ValueError):
            account.debit(0)
        with self.assertRaises(ValueError):
            account.debit(-100)

    # ------------------------------------------------------------------ #
    #  WB-TC-09: _validate_amount – zero fails first condition            #
    # ------------------------------------------------------------------ #
    def test_wb_09_validate_amount_zero(self):
        """
        Branch: amount <= 0 path in WithdrawController._validate_amount().
        """
        wc = make_wc()
        with self.assertRaises(InvalidAmountError) as ctx:
            wc._validate_amount(0)
        self.assertIn("greater than zero", str(ctx.exception))

    # ------------------------------------------------------------------ #
    #  WB-TC-10: _validate_amount – fractional fails second condition     #
    # ------------------------------------------------------------------ #
    def test_wb_10_validate_amount_fractional(self):
        """
        Branch: amount != int(amount) path in _validate_amount().
        """
        wc = make_wc()
        with self.assertRaises(InvalidAmountError) as ctx:
            wc._validate_amount(200.75)
        self.assertIn("whole number", str(ctx.exception))

    # ------------------------------------------------------------------ #
    #  WB-TC-11: _validate_amount – non-multiple fails third condition    #
    # ------------------------------------------------------------------ #
    def test_wb_11_validate_amount_non_multiple(self):
        """
        Branch: int(amount) % MIN_DENOMINATION != 0 in _validate_amount().
        """
        wc = make_wc()
        with self.assertRaises(InvalidAmountError) as ctx:
            wc._validate_amount(250)
        self.assertIn(f"multiple of Rs.{MIN_DENOMINATION}", str(ctx.exception))

    # ------------------------------------------------------------------ #
    #  WB-TC-12: ATM cash decrements by exact withdrawal amount           #
    # ------------------------------------------------------------------ #
    def test_wb_12_atm_cash_decremented(self):
        """
        Path: self._atm_cash -= amount after successful withdrawal.
        Verifies internal ATM cash register updates correctly.
        """
        account = make_account(10000)
        wc      = make_wc(atm_cash=5000)

        wc.process_withdrawal(account, 2000)
        self.assertAlmostEqual(wc.atm_cash, 3000.0)

    # ------------------------------------------------------------------ #
    #  WB-TC-13: Transaction.mark_success() sets status and message       #
    # ------------------------------------------------------------------ #
    def test_wb_13_transaction_mark_success(self):
        """
        Internal path: Transaction.mark_success() sets _status = SUCCESS.
        """
        txn = Transaction("ACC001", TransactionType.WITHDRAWAL, 500)
        self.assertEqual(txn.status, TransactionStatus.PENDING)

        txn.mark_success("All good")
        self.assertEqual(txn.status, TransactionStatus.SUCCESS)
        self.assertEqual(txn.message, "All good")

    # ------------------------------------------------------------------ #
    #  WB-TC-14: Transaction.mark_failed() sets status and reason         #
    # ------------------------------------------------------------------ #
    def test_wb_14_transaction_mark_failed(self):
        """
        Internal path: Transaction.mark_failed() sets _status = FAILED.
        Triggered when WithdrawController re-raises on error.
        """
        account = make_account(100)
        wc      = make_wc()

        try:
            wc.process_withdrawal(account, 500)
        except InsufficientFundsError:
            pass

        # Verify by constructing a transaction manually
        txn = Transaction("ACC001", TransactionType.WITHDRAWAL, 500)
        txn.mark_failed("Insufficient funds")
        self.assertEqual(txn.status, TransactionStatus.FAILED)
        self.assertIn("Insufficient", txn.message)

    # ------------------------------------------------------------------ #
    #  WB-TC-15: AuthController.end_session() clears session state        #
    # ------------------------------------------------------------------ #
    def test_wb_15_end_session_clears_state(self):
        """
        Branch: end_session() sets session_active = False and
        authenticated_card = None (logout / timeout path).
        """
        card = make_card("1234")
        auth = AuthController()
        auth.authenticate(card, "1234")

        self.assertTrue(auth.session_active)
        self.assertIsNotNone(auth.authenticated_card)

        auth.end_session()

        self.assertFalse(auth.session_active)
        self.assertIsNone(auth.authenticated_card)


if __name__ == "__main__":
    unittest.main(verbosity=2)
