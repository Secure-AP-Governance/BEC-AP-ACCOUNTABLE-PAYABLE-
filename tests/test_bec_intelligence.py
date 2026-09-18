import unittest

from src.application import Application
from src.bec_intelligence import AuthenticationSignals, EmailMessage, VendorProfile
from src.domain import ProposalState


class BECIntelligenceTests(unittest.TestCase):
    def setUp(self):
        self.app = Application()
        self.vendor = VendorProfile(
            vendor_id="v1",
            name="Known Vendor",
            domains=frozenset({"vendor.example"}),
            sender_addresses=frozenset({"ap@vendor.example"}),
            vendor_snapshot=1,
        )
        self.safe_auth = AuthenticationSignals("PASS", "PASS", "PASS")

    def email(self, **changes):
        values = {
            "message_id": "m1",
            "sender": "ap@vendor.example",
            "reply_to": "ap@vendor.example",
            "subject": "Invoice status",
            "body": "Please confirm receipt.",
        }
        values.update(changes)
        return EmailMessage(**values)

    def test_spoofed_sender_quarantined(self):
        result = self.app.bec.ingest(
            self.email(sender="attacker@evil.example", reply_to="attacker@evil.example"),
            AuthenticationSignals("FAIL", "FAIL", "FAIL"),
            self.vendor,
            "requester",
        )
        self.assertEqual(result.status, "QUARANTINED")
        self.assertIn("unknown_sender", result.analysis.factors)

    def test_failed_dmarc_detected(self):
        analysis = self.app.bec.analyze(self.email(), AuthenticationSignals("PASS", "PASS", "FAIL"), self.vendor)
        self.assertIn("failed_dmarc", analysis.factors)

    def test_reply_to_mismatch_detected(self):
        analysis = self.app.bec.analyze(self.email(reply_to="attacker@evil.example"), self.safe_auth, self.vendor)
        self.assertTrue(analysis.reply_to_mismatch)
        self.assertIn("reply_to_mismatch", analysis.factors)

    def test_bank_change_request_scored(self):
        analysis = self.app.bec.analyze(
            self.email(subject="Update banking account", body="Please confirm the new routing number."),
            self.safe_auth,
            self.vendor,
        )
        self.assertTrue(analysis.bank_change_request)
        self.assertIn("bank_change_request", analysis.factors)
        self.assertGreaterEqual(analysis.risk_score, 30)

    def test_known_vendor_low_risk(self):
        analysis = self.app.bec.analyze(self.email(), self.safe_auth, self.vendor)
        self.assertEqual(analysis.risk_score, 0)
        self.assertEqual(analysis.factors, ())

    def test_proposal_created_from_email(self):
        result = self.app.bec.ingest(self.email(), self.safe_auth, self.vendor, "requester")
        self.assertEqual(result.state, ProposalState.DRAFT)
        self.assertEqual(result.id, "email:m1")
        self.assertTrue(self.app.audit_valid(result.id))

    def test_quarantine_created_from_high_risk_email(self):
        result = self.app.bec.ingest(
            self.email(subject="Urgent bank account change", body="Please update the new wire account."),
            AuthenticationSignals("FAIL", "FAIL", "FAIL"),
            self.vendor,
            "requester",
        )
        self.assertIn(result.quarantine_id, self.app.quarantine.items)
        self.assertNotIn("email:m1", self.app.proposals.items)

    def test_bec_cannot_update_vendor_data(self):
        self.assertFalse(hasattr(self.app.bec, "update_vendor"))
        self.assertEqual(self.app.vendors.version("v1"), 1)

    def test_bec_cannot_execute_payment(self):
        self.assertFalse(hasattr(self.app.bec, "execute_payment"))
        self.assertFalse(self.app.security_status()["PAYMENT_EXECUTION_ENABLED"])


if __name__ == "__main__":
    unittest.main()