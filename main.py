"""
ATM Banking System - Main Entry Point
Drives the complete Withdraw Cash flow interactively via ATM_UI.

Run:
    python main.py
"""

from typing import Optional
from atm_system.card                import Card
from atm_system.account             import Account
from atm_system.auth_controller     import AuthController
from atm_system.withdraw_controller import WithdrawController
from atm_system.atm_ui              import ATM_UI
from atm_system.exceptions          import (
    CardBlockedError, SessionTimeoutError, ServerError
)

# ------------------------------------------------------------------ #
#  Simulated Bank Database                                             #
# ------------------------------------------------------------------ #
CARDS_DB = {
    "4111111111111111": Card(
        card_number="4111111111111111",
        pin="1234",
        account_number="ACC001",
    ),
    "4222222222222222": Card(
        card_number="4222222222222222",
        pin="5678",
        account_number="ACC002",
    ),
}

ACCOUNTS_DB = {
    "ACC001": Account("ACC001", "Alice Johnson", balance=25000.00),
    "ACC002": Account("ACC002", "Bob Smith",     balance=5000.00),
}


def get_card_by_number(card_number: str) -> Optional[Card]:
    return CARDS_DB.get(card_number)


def get_account_by_card(card: Card) -> Optional[Account]:
    return ACCOUNTS_DB.get(card.account_number)


# ------------------------------------------------------------------ #
#  Main ATM Session                                                    #
# ------------------------------------------------------------------ #
def run_atm_session() -> None:
    print("\nWelcome to National Bank ATM")
    print("=" * 44)

    # Customer inserts card number
    card_number = input("  Insert your card (enter card number): ").strip()
    card = get_card_by_number(card_number)
    if not card:
        print("  ✘  Card not recognised. Ejecting card.")
        return

    account = get_account_by_card(card)
    if not account:
        print("  ✘  No linked account found. Ejecting card.")
        return

    # Initialise controllers
    auth_ctrl     = AuthController(bank_server_online=True)
    withdraw_ctrl = WithdrawController(atm_cash_available=100000.00)
    ui            = ATM_UI(auth_ctrl, withdraw_ctrl)

    # Card insertion (boundary step)
    ui.insert_card(card)

    # PIN authentication
    try:
        ui.enter_pin(card)
    except (CardBlockedError, ServerError) as e:
        print(f"\n  ✘  {e}")
        return

    # Transaction loop
    while True:
        try:
            choice = ui.show_menu()
        except SessionTimeoutError as e:
            print(f"\n  ✘  {e}")
            break

        if choice == "1":
            try:
                amount = ui.select_amount()
                ui.process_withdrawal(account, amount)
            except SessionTimeoutError as e:
                print(f"\n  ✘  {e}")
                break
        elif choice == "2":
            print(f"\n  Current Balance: Rs. {account.get_balance():,.2f}\n")
        elif choice == "3":
            break
        else:
            print("  Invalid choice. Please try again.")

    ui.logout()


if __name__ == "__main__":
    run_atm_session()
