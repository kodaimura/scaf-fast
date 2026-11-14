import unittest
from unittest.mock import Mock, patch

from app.core.error import AppError, ErrorCode
from app.usecase.auth.signup import SignupInput, SignupUsecase


class SignupUsecaseTest(unittest.TestCase):
    def test_disabled_signup_rejects_before_database_access(self):
        db = Mock()
        usecase = SignupUsecase(db)
        signup = SignupInput(
            login_id=None,
            email="new-account@example.com",
            password="test-password",
            first_name="New",
            last_name="Account",
        )

        with patch("app.usecase.auth.signup.config.ENABLE_SIGNUP", False):
            with self.assertRaises(AppError) as context:
                usecase.execute(signup)

        self.assertEqual(context.exception.code, ErrorCode.FORBIDDEN.value)
        self.assertEqual(db.mock_calls, [])
