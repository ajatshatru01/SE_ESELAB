"""
ATM Banking System - AuthController (Control Object)
CRC Role: Verify PIN, handle authentication, manage card blocking
Collaborators: Card, Bank Server (simulated)
"""

from typing import Optional
from atm_system.card       import Card
from atm_system.exceptions import AuthenticationError, CardBlockedError


class AuthController:
    """
    Control object responsible for authenticating a customer's card and PIN.
    Simulates communication with the Bank Server for PIN verification.
    Enforces card-blocking policy on consecutive failures.
    """

    def __init__(self, bank_server_online: bool = True):
        self._bank_server_online = bank_server_online
        self._session_active     = False
        self._authenticated_card: Card | None = None

    # ------------------------------------------------------------------ #
    #  Properties                                                          #
    # ------------------------------------------------------------------ #
    @property
    def session_active(self) -> bool:
        return self._session_active

    @property
    def authenticated_card(self) -> Optional[Card]:
        return self._authenticated_card

    # ------------------------------------------------------------------ #
    #  Behaviour                                                           #
    # ------------------------------------------------------------------ #
    def authenticate(self, card: Card, entered_pin: str) -> bool:
        """
        Verifies the entered PIN against the card's stored PIN.

        Flow (mirrors Sequence Diagram):
          ATM_UI → AuthController.authenticate()
          AuthController → BankServer.verifyPIN()   [simulated]
          BankServer → AuthController : valid/invalid

        Returns True on success.
        Raises:
          CardBlockedError     – card is already blocked
          AuthenticationError  – PIN is wrong (includes attempts_remaining)
        """
        if not self._bank_server_online:
            from atm_system.exceptions import ServerError
            raise ServerError("Bank server is not responding. Please try again later.")

        # Delegates validation to the Card entity
        is_valid = card.validate_pin(entered_pin)      # raises CardBlockedError if blocked

        if is_valid:
            card.reset_failed_attempts()
            self._session_active     = True
            self._authenticated_card = card
            return True
        else:
            card.increment_failed_attempts()           # may block the card
            if card.is_blocked:
                raise CardBlockedError(
                    f"Card blocked after {card.failed_attempts} failed attempts. "
                    "Please contact your bank."
                )
            raise AuthenticationError(
                f"Invalid PIN. {card.attempts_remaining()} attempt(s) remaining.",
                attempts_remaining=card.attempts_remaining(),
            )

    def end_session(self) -> None:
        """Terminates the current authenticated session (logout / timeout)."""
        self._session_active     = False
        self._authenticated_card = None

    def __repr__(self) -> str:
        return f"AuthController(session_active={self._session_active}, server_online={self._bank_server_online})"
