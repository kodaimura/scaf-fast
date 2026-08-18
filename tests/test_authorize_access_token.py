from datetime import datetime, timezone
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from app.core.error import AppError, ErrorCode
from app.usecase.auth.authorize import AuthorizeAccessTokenUsecase


class AuthorizeAccessTokenUsecaseTest(unittest.TestCase):
    def setUp(self):
        self.usecase = AuthorizeAccessTokenUsecase(Mock())
        self.usecase.accounts = Mock()

    def test_returns_account_id_for_active_matching_account(self):
        self.usecase.accounts.get_by_id.return_value = SimpleNamespace(
            id=123,
            disabled_at=None,
            token_version=4,
        )

        account_id = self.usecase.execute({"sub": "123", "token_version": 4})

        self.assertEqual(account_id, 123)
        self.usecase.accounts.get_by_id.assert_called_once_with(123)

    def test_rejects_missing_token_claims(self):
        for payload in ({}, {"sub": "123"}, {"token_version": 1}):
            with self.subTest(payload=payload):
                self._assert_error(
                    payload,
                    ErrorCode.AUTH_INVALID_PAYLOAD,
                )
        self.usecase.accounts.get_by_id.assert_not_called()

    def test_rejects_non_numeric_subject(self):
        self._assert_error(
            {"sub": "invalid", "token_version": 1},
            ErrorCode.AUTH_INVALID_SUBJECT,
        )
        self.usecase.accounts.get_by_id.assert_not_called()

    def test_rejects_missing_account(self):
        self.usecase.accounts.get_by_id.return_value = None

        self._assert_error(
            {"sub": "123", "token_version": 1},
            ErrorCode.AUTH_NOT_FOUND,
        )

    def test_rejects_disabled_account(self):
        self.usecase.accounts.get_by_id.return_value = SimpleNamespace(
            id=123,
            disabled_at=datetime.now(timezone.utc),
            token_version=1,
        )

        self._assert_error(
            {"sub": "123", "token_version": 1},
            ErrorCode.ACCOUNT_DISABLED,
        )

    def test_rejects_revoked_token(self):
        self.usecase.accounts.get_by_id.return_value = SimpleNamespace(
            id=123,
            disabled_at=None,
            token_version=2,
        )

        self._assert_error(
            {"sub": "123", "token_version": 1},
            ErrorCode.AUTH_TOKEN_REVOKED,
        )

    def _assert_error(self, payload: dict, error_code: ErrorCode):
        with self.assertRaises(AppError) as context:
            self.usecase.execute(payload)

        self.assertEqual(context.exception.code, error_code.value)


if __name__ == "__main__":
    unittest.main()
