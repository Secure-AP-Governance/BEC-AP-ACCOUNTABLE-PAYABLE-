import unittest

from src.application import Application
from src.bec_intelligence import AuthenticationSignals, EmailMessage, VendorProfile
from src.domain import Proposal


class OperationsViewTests(unittest.TestCase):
    def setUp(self):
        self.app = Application()
        self.app.create(Proposal("p1", "v1", "requester", 1, ["invoice:1"]))
        self.vendor = VendorProfile(
            vendor_id="v1",
            name="Known Vendor",
            domains=frozenset({"vendor.example"}),
            sender_addresses=frozenset({"ap@vendor.example"}),
        )

    def test_proposal_queue_visible(self):
        queue = self.app.operations.proposal_queue()
        self.assertEqual(queue[0]["proposal_id"], "p1")
        self.assertEqual(queue[0]["state"], "DRAFT")

    def test_quarantine_queue_visible(self):
        result = self.app.bec.ingest(
            EmailMessage(
                "m1",
                "attacker@evil.example",
                "attacker@evil.example",
                "Urgent bank account change",
                body="Please update the new wire account.",
            ),
            AuthenticationSignals("FAIL", "FAIL", "FAIL"),
            self.vendor,
            "requester",
        )
        queue = self.app.operations.quarantine_queue()
        self.assertEqual(queue[0]["quarantine_id"], result.quarantine_id)
        self.assertEqual(queue[0]["status"], "QUARANTINED")

    def test_audit_explorer_loads(self):
        self.app.bec.ingest(
            EmailMessage("m1", "ap@vendor.example", "ap@vendor.example", "Invoice"),
            AuthenticationSignals("PASS", "PASS", "PASS"),
            self.vendor,
            "requester",
        )
        events = self.app.operations.audit_explorer()
        self.assertEqual(events[0]["action"], "EMAIL_INGESTED")
        self.assertTrue(events[0]["event_hash"])

    def test_security_dashboard_reports_invariants(self):
        dashboard = self.app.operations.security_dashboard()
        self.assertEqual(dashboard["status"], "PASS")
        self.assertFalse(dashboard["payment_execution_enabled"])
        self.assertFalse(dashboard["automatic_payment_dispatch"])
        self.assertFalse(dashboard["automatic_bank_change"])


if __name__ == "__main__":
    unittest.main()