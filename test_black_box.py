"""
ATM Banking System - Black Box Test Cases (15)
Tests the Withdraw Cash use case from the EXTERNAL perspective only.
No knowledge of internal implementation; only inputs and expected outputs.

Run:
    python -m pytest test_black_box.py -v
"""

import unittest
from atm_system.card                import Card
from atm_system.account             import Account
from atm_system.auth_controller     import AuthController
from atm_system.withdraw_controller import WithdrawController
from atm_system.transaction         import TransactionStatus
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

def make_withdraw_ctrl(atm_cash=50000.0, server_online=True):
    return WithdrawController(atm_cash, server_online)


class TestBlackBox(unittest.TestCase):

    # ------------------------------------------------------------------ #
    #  BB-TC-01: Valid withdrawal – correct PIN and sufficient balance     #
    # ------------------------------------------------------------------ #
    def test_bb_01_valid_withdrawal(self):
        """Valid card, correct PIN, sufficient balance → cash dispensed."""
        card    = make_card("1234")
        account = make_account(10000)
        auth    = AuthController()
        wc      = make_withdraw_ctrl(50000)

        auth.authenticate(card, "1234")
        txn = wc.process_withdrawal(account, 500)

        self.assertEqual(txn.status, TransactionStatus.SUCCESS)
        self.assertAlmostEqual(account.balance, 9500.0)

    # ------------------------------------------------------------------ #
    #  BB-TC-02: Wrong PIN – single failure                               #
    # ------------------------------------------------------------------ #
    def test_bb_02_wrong_pin_once(self):
        """Wrong PIN entered once → AuthenticationError, card NOT blocked."""
        card = make_card("1234")
        auth = AuthController()

        with self.assertRaises(AuthenticationError):
            auth.authenticate(card, "0000")

        self.assertFalse(card.is_blocked)
        self.assertEqual(card.failed_attempts, 1)

    # ------------------------------------------------------------------ #
    #  BB-TC-03: Card blocked after 3 consecutive wrong PINs              #
    # ------------------------------------------------------------------ #
    def test_bb_03_card_blocked_after_3_failures(self):
        """Three consecutive wrong PINs → CardBlockedError, card blocked."""
        card = make_card("1234")
        auth = AuthController()

        for _ in range(2):
            with self.assertRaises(AuthenticationError):
                auth.authenticate(card, "9999")

        with self.assertRaises(CardBlockedError):
            auth.authenticate(card, "9999")

        self.assertTrue(card.is_blocked)

    # ------------------------------------------------------------------ #
    #  BB-TC-04: Attempt to use a blocked card                            #
    # ------------------------------------------------------------------ #
    def test_bb_04_use_blocked_card(self):
        """Blocked card inserted → CardBlockedError immediately."""
        card = make_card("1234")
        card.block()
        auth = AuthController()

        with self.assertRaises(CardBlockedError):
            auth.authenticate(card, "1234")

    # ------------------------------------------------------------------ #
    #  BB-TC-05: Insufficient balance                                     #
    # ------------------------------------------------------------------ #
    def test_bb_05_insufficient_balance(self):
        """Withdrawal amount exceeds account balance → InsufficientFundsError."""
        card    = make_card("1234")
        account = make_account(200)
        auth    = AuthController()
        wc      = make_withdraw_ctrl()

        auth.authenticate(card, "1234")
        with self.assertRaises(InsufficientFundsError):
            wc.process_withdrawal(account, 500)

        self.assertAlmostEqual(account.balance, 200.0)   # balance unchanged

    # ------------------------------------------------------------------ #
    #  BB-TC-06: ATM out of cash                                          #
    # ------------------------------------------------------------------ #
    def test_bb_06_atm_out_of_cash(self):
        """ATM has less cash than requested → ATMOutOfCashError."""
        account = make_account(10000)
        wc      = make_withdraw_ctrl(atm_cash=300)

        with self.assertRaises(ATMOutOfCashError):
            wc.process_withdrawal(account, 500)

        self.assertAlmostEqual(account.balance, 10000.0)  # balance unchanged

    # ------------------------------------------------------------------ #
    #  BB-TC-07: Zero amount entered                                      #
    # ------------------------------------------------------------------ #
    def test_bb_07_zero_amount(self):
        """Withdrawal amount = 0 → InvalidAmountError."""
        account = make_account(10000)
        wc      = make_withdraw_ctrl()

        with self.assertRaises(InvalidAmountError):
            wc.process_withdrawal(account, 0)

    # ------------------------------------------------------------------ #
    #  BB-TC-08: Negative amount entered                                  #
    # ------------------------------------------------------------------ #
    def test_bb_08_negative_amount(self):
        """Withdrawal amount < 0 → InvalidAmountError."""
        account = make_account(10000)
        wc      = make_withdraw_ctrl()

        with self.assertRaises(InvalidAmountError):
            wc.process_withdrawal(account, -500)

    # ------------------------------------------------------------------ #
    #  BB-TC-09: Amount not a multiple of Rs.100                          #
    # ------------------------------------------------------------------ #
    def test_bb_09_non_multiple_amount(self):
        """Amount Rs.150 is not a multiple of Rs.100 → InvalidAmountError."""
        account = make_account(10000)
        wc      = make_withdraw_ctrl()

        with self.assertRaises(InvalidAmountError):
            wc.process_withdrawal(account, 150)

    # ------------------------------------------------------------------ #
    #  BB-TC-10: Exact balance withdrawal                                  #
    # ------------------------------------------------------------------ #
    def test_bb_10_exact_balance_withdrawal(self):
        """Withdraw exactly the account balance → success, balance becomes 0."""
        account = make_account(1000)
        wc      = make_withdraw_ctrl()

        txn = wc.process_withdrawal(account, 1000)

        self.assertEqual(txn.status, TransactionStatus.SUCCESS)
        self.assertAlmostEqual(account.balance, 0.0)

    # ------------------------------------------------------------------ #
    #  BB-TC-11: Bank server offline                                      #
    # ------------------------------------------------------------------ #
    def test_bb_11_server_offline(self):
        """Bank server not reachable → ServerError."""
        account = make_account(10000)
        wc      = make_withdraw_ctrl(server_online=False)

        with self.assertRaises(ServerError):
            wc.process_withdrawal(account, 500)

    # ------------------------------------------------------------------ #
    #  BB-TC-12: Receipt generated after successful withdrawal            #
    # ------------------------------------------------------------------ #
    def test_bb_12_receipt_generated(self):
        """Successful withdrawal produces a non-empty receipt string."""
        account = make_account(10000)
        wc      = make_withdraw_ctrl()

        txn     = wc.process_withdrawal(account, 500)
        receipt = txn.get_receipt()

        self.assertIn("NATIONAL BANK ATM RECEIPT", receipt)
        self.assertIn("SUCCESS", receipt)
        self.assertIn("500", receipt)

    # ------------------------------------------------------------------ #
    #  BB-TC-13: Multiple successive valid withdrawals                    #
    # ------------------------------------------------------------------ #
    def test_bb_13_multiple_withdrawals(self):
        """Two consecutive valid withdrawals both succeed, balance reduces correctly."""
        account = make_account(5000)
        wc      = make_withdraw_ctrl()

        txn1 = wc.process_withdrawal(account, 1000)
        txn2 = wc.process_withdrawal(account, 2000)

        self.assertEqual(txn1.status, TransactionStatus.SUCCESS)
        self.assertEqual(txn2.status, TransactionStatus.SUCCESS)
        self.assertAlmostEqual(account.balance, 2000.0)

    # ------------------------------------------------------------------ #
    #  BB-TC-14: Successful auth after one wrong PIN attempt              #
    # ------------------------------------------------------------------ #
    def test_bb_14_success_after_one_wrong_pin(self):
        """One wrong PIN then correct PIN → authentication succeeds."""
        card = make_card("1234")
        auth = AuthController()

        with self.assertRaises(AuthenticationError):
            auth.authenticate(card, "0000")

        result = auth.authenticate(card, "1234")
        self.assertTrue(result)
        self.assertTrue(auth.session_active)
        self.assertEqual(card.failed_attempts, 0)   # reset on success

    # ------------------------------------------------------------------ #
    #  BB-TC-15: Fractional (float) amount entry                          #
    # ------------------------------------------------------------------ #
    def test_bb_15_fractional_amount(self):
        """Amount Rs.100.50 (non-integer) → InvalidAmountError."""
        account = make_account(10000)
        wc      = make_withdraw_ctrl()

        with self.assertRaises(InvalidAmountError):
            wc.process_withdrawal(account, 100.50)


if __name__ == "__main__":
    unittest.main(verbosity=2)
