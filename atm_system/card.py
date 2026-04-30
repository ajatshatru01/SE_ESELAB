"""
ATM Banking System - Card Entity
CRC Role: Store card details, validate PIN, track failed attempts
Collaborators: AuthController
"""

from atm_system.exceptions import CardBlockedError

MAX_PIN_ATTEMPTS = 3


class Card:
    """
    Entity object representing the customer's ATM card.
    Tracks PIN, card number, blocked status, and failed attempt count.
    """

    def __init__(self, card_number: str, pin: str, account_number: str):
        if not card_number or not pin or not account_number:
            raise ValueError("Card number, PIN, and account number are required.")
        self._card_number = card_number
        self._pin = pin                      # Stored as plain string (would be hashed in production)
        self._account_number = account_number
        self._failed_attempts = 0
        self._is_blocked = False

    # ------------------------------------------------------------------ #
    #  Properties                                                          #
    # ------------------------------------------------------------------ #
    @property
    def card_number(self) -> str:
        return self._card_number

    @property
    def account_number(self) -> str:
        return self._account_number

    @property
    def is_blocked(self) -> bool:
        return self._is_blocked

    @property
    def failed_attempts(self) -> int:
        return self._failed_attempts

    # ------------------------------------------------------------------ #
    #  Behaviour                                                           #
    # ------------------------------------------------------------------ #
    def validate_pin(self, entered_pin: str) -> bool:
        """
        Returns True if the entered PIN matches and card is not blocked.
        Raises CardBlockedError if card is already blocked.
        """
        if self._is_blocked:
            raise CardBlockedError(
                f"Card {self._card_number} is blocked. Please contact your bank."
            )
        return self._pin == entered_pin

    def increment_failed_attempts(self) -> None:
        """
        Increments the failed PIN attempt counter.
        Blocks the card automatically after MAX_PIN_ATTEMPTS failures.
        """
        self._failed_attempts += 1
        if self._failed_attempts >= MAX_PIN_ATTEMPTS:
            self._is_blocked = True

    def reset_failed_attempts(self) -> None:
        """Resets the failed attempt counter on successful authentication."""
        self._failed_attempts = 0

    def block(self) -> None:
        """Forcibly block the card (e.g., manual admin action)."""
        self._is_blocked = True

    def attempts_remaining(self) -> int:
        """Returns how many PIN attempts remain before the card is blocked."""
        return max(0, MAX_PIN_ATTEMPTS - self._failed_attempts)

    def __repr__(self) -> str:
        masked = "*" * (len(self._card_number) - 4) + self._card_number[-4:]
        return f"Card({masked}, blocked={self._is_blocked}, attempts={self._failed_attempts})"
