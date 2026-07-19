from django.test import TestCase

from payment.models import PVNumberingConfig


class PVNumberingConfigTests(TestCase):
    def test_sequence_increments_within_same_period(self):
        config = PVNumberingConfig.objects.create(reset_period='NEVER')

        code1 = config.generate_next()
        code2 = config.generate_next()
        code3 = config.generate_next()

        config.refresh_from_db()
        self.assertEqual(config.current_running, 3)
        self.assertNotEqual(code1, code2)
        self.assertNotEqual(code2, code3)
        self.assertIn('001', code1)
        self.assertIn('002', code2)
        self.assertIn('003', code3)

    def test_generate_next_is_concurrent_safe_and_monotonic(self):
        config = PVNumberingConfig.objects.create(reset_period='NEVER')

        code1 = config.generate_next()
        code2 = config.generate_next()

        config.refresh_from_db()
        self.assertEqual(config.current_running, 2)
        self.assertNotEqual(code1, code2)

    def test_yearly_reset_bumps_seq_and_resets_running(self):
        config = PVNumberingConfig.objects.create(
            reset_period='YEARLY', current_seq=5, current_running=10, last_reset_period_key='2020',
        )

        code = config.generate_next()

        config.refresh_from_db()
        self.assertEqual(config.current_seq, 6)
        self.assertEqual(config.current_running, 1)
        self.assertNotEqual(config.last_reset_period_key, '2020')
        self.assertIn('06', code)
        self.assertIn('001', code)

    def test_monthly_reset_bumps_seq_and_resets_running(self):
        config = PVNumberingConfig.objects.create(
            reset_period='MONTHLY', current_seq=2, current_running=5, last_reset_period_key='2000-01',
        )

        config.generate_next()

        config.refresh_from_db()
        self.assertEqual(config.current_seq, 3)
        self.assertEqual(config.current_running, 1)
        self.assertNotEqual(config.last_reset_period_key, '2000-01')

    def test_no_reset_within_same_period_does_not_bump_seq(self):
        config = PVNumberingConfig.objects.create(reset_period='YEARLY')

        config.generate_next()
        config.refresh_from_db()
        seq_after_first = config.current_seq

        config.generate_next()
        config.refresh_from_db()

        self.assertEqual(config.current_seq, seq_after_first)
        self.assertEqual(config.current_running, 2)
