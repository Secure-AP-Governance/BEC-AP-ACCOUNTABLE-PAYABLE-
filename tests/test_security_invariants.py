import unittest

from config.security_invariants import INVARIANTS, validate_invariants


class SecurityInvariantTests(unittest.TestCase):
    def test_all_locked_invariants_are_false(self):
        self.assertEqual(
            INVARIANTS,
            {
                "PAYMENT_EXECUTION_ENABLED": False,
                "AUTOMATIC_PAYMENT_DISPATCH": False,
                "AUTOMATIC_BANK_CHANGE": False,
            },
        )

    def test_validation_passes(self):
        validate_invariants()


if __name__ == "__main__":
    unittest.main()
