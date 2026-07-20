from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from users.models import OTP
from users.views import APILoginView, APIVerifyOTPView, PasswordResetRequestView, _FALLBACK_CACHE, _get_lock_state


class PasswordResetRequestViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = PasswordResetRequestView.as_view()
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="Password123!",
        )

    @patch("users.views.task_send_password_reset_email.delay")
    def test_password_reset_accepts_username_without_email(self, mock_delay):
        request = self.factory.post("/api/v1/auth/password-reset/", {"username": "alice"})

        response = self.view(request)

        mock_delay.assert_called_once()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "Password reset link sent to your email.")


class OTPVerificationLockoutTests(TestCase):
    def setUp(self):
        _FALLBACK_CACHE.clear()
        self.factory = APIRequestFactory()
        self.view = APIVerifyOTPView.as_view()
        self.user = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="Password123!",
        )
        self.otp = OTP.objects.create(user=self.user, otp_ref="ref123", otp_code="123456")

    @patch("users.views.task_send_otp_email.delay")
    def test_blocks_after_max_failed_attempts(self, mock_delay):
        self.otp.max_otp_try = 0
        self.otp.save()

        request = self.factory.post(
            "/api/v1/auth/verify-otp/",
            {"username": "bob", "otp_code": "000000"},
            format="json",
        )

        response = self.view(request)

        self.assertEqual(response.status_code, 429)
        self.assertIn("locked", response.data["error"].lower())

    @patch("users.views.task_send_otp_email.delay")
    def test_resets_attempts_after_successful_login(self, mock_delay):
        self.otp.max_otp_try = 1
        self.otp.save()

        request = self.factory.post(
            "/api/v1/auth/verify-otp/",
            {"username": "bob", "otp_code": self.otp.otp_code},
            format="json",
        )

        response = self.view(request)

        self.otp.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.otp.max_otp_try, 3)

    def test_password_attempts_are_counted_towards_lockout(self):
        login_view = APILoginView.as_view()

        for attempt in range(3):
            request = self.factory.post(
                "/api/v1/auth/login/",
                {"username": "bob", "password": "wrong-password"},
                format="json",
            )
            response = login_view(request)
            if attempt < 2:
                self.assertEqual(response.status_code, 401)
            else:
                self.assertEqual(response.status_code, 429)

        self.assertEqual(_get_lock_state("bob", "password")["attempts"], 3)

    def test_password_lockout_response_mentions_retry_time(self):
        login_view = APILoginView.as_view()

        for _ in range(3):
            request = self.factory.post(
                "/api/v1/auth/login/",
                {"username": "bob", "password": "wrong-password"},
                format="json",
            )
            login_view(request)

        request = self.factory.post(
            "/api/v1/auth/login/",
            {"username": "bob", "password": "wrong-password"},
            format="json",
        )
        response = login_view(request)

        self.assertEqual(response.status_code, 429)
        self.assertIn("Please try again at", response.data["error"])

    def test_password_lockout_does_not_block_otp_attempts(self):
        login_view = APILoginView.as_view()
        otp_view = APIVerifyOTPView.as_view()

        for _ in range(3):
            request = self.factory.post(
                "/api/v1/auth/login/",
                {"username": "bob", "password": "wrong-password"},
                format="json",
            )
            login_view(request)

        otp_request = self.factory.post(
            "/api/v1/auth/verify-otp/",
            {"username": "bob", "otp_code": "000000"},
            format="json",
        )
        otp_response = otp_view(otp_request)

        self.assertEqual(otp_response.status_code, 401)
        self.assertIn("Invalid or expired OTP", otp_response.data["error"])

        self.assertEqual(_get_lock_state("bob", "password")["attempts"], 3)
