import unittest
from dataclasses import replace

from src.application import Application
from src.bec_intelligence import AuthenticationSignals, EmailMessage, VendorProfile
from src.domain import Actor, Proposal, ProposalState, Role
from src.repositories import ConflictError


class ReleaseValidationTests(unittest.TestCase):
    def setUp(self):
        self.app = Application()
        self.requester = Actor("requester", Role.REQUESTER)
        self.verifier = Actor("verifier", Role.VERIFIER)
        self.approver = Actor("approver", Role.APPROVER)
        self.vendor = VendorProfile(
            "v1",
            "Known Vendor",
            frozenset({"vendor.example"}),
            frozenset({"ap@vendor.example"}),
        )

    def email(self, subject="Invoice", body="Please confirm receipt.", **changes):
        values = {
            "message_id": "m1",
            "sender": "ap@vendor.example",
            "reply_to": "ap@vendor.example",
            "subject": subject,
            "body": body,
        }
        values.update(changes)
        return EmailMessage(**values)

    def create_proposal(self, proposal_id="p1"):
        self.app.create(Proposal(proposal_id, "v1", "requester", 1, ["invoice:1"]))
        self.app.proposal.submit(proposal_id, self.requester, 1)

    def test_legitimate_vendor_change_preserves_workflow(self):
        self.create_proposal()
        self.app.worklists.verify("p1", self.verifier, 2)
        self.app.worklists.approve("p1", self.approver, 3)
        result = self.app.erp.request("p1", self.approver, 4, "uat-1")
        self.assertEqual(result["status"], "REQUESTED")
        self.assertTrue(self.app.audit_valid("p1"))

    def test_spoofed_sender_is_quarantined(self):
        result = self.app.bec.ingest(
            self.email(sender="attacker@evil.example", reply_to="attacker@evil.example"),
            AuthenticationSignals("FAIL", "FAIL", "FAIL"),
            self.vendor,
            "requester",
        )
        self.assertEqual(result.status, "QUARANTINED")

    def test_failed_dmarc_is_detected(self):
        analysis = self.app.bec.analyze(
            self.email(), AuthenticationSignals("PASS", "PASS", "FAIL"), self.vendor
        )
        self.assertIn("failed_dmarc", analysis.factors)

    def test_reply_to_mismatch_is_detected(self):
        analysis = self.app.bec.analyze(
            self.email(reply_to="attacker@evil.example"),
            AuthenticationSignals("PASS", "PASS", "PASS"),
            self.vendor,
        )
        self.assertIn("reply_to_mismatch", analysis.factors)

    def test_evidence_request_is_audited(self):
        self.create_proposal()
        result = self.app.worklists.request_evidence("p1", self.verifier, 2)
        self.assertEqual(result.state, ProposalState.EVIDENCE_REQUESTED)
        self.assertEqual(self.app.operations.audit_explorer()[-1]["action"], "REQUEST_EVIDENCE")

    def test_escalation_is_audited(self):
        self.create_proposal()
        self.app.worklists.verify("p1", self.verifier, 2)
        result = self.app.worklists.escalate("p1", self.approver, 3)
        self.assertEqual(result.state, ProposalState.ESCALATED)
        self.assertEqual(self.app.operations.audit_explorer()[-1]["action"], "ESCALATE")

    def test_concurrent_approval_is_rejected(self):
        self.create_proposal()
        self.app.worklists.verify("p1", self.verifier, 2)
        with self.assertRaises(ConflictError):
            self.app.worklists.approve("p1", self.approver, 2)

    def test_audit_tampering_is_detected(self):
        self.create_proposal()
        event = self.app.audit_repo.events["p1"][0]
        self.app.audit_repo.events["p1"][0] = replace(event, action="TAMPERED")
        self.assertFalse(self.app.audit_valid("p1"))
        self.assertEqual(self.app.health_status()["audit_chain"], "FAIL")

    def test_immutable_controls_remain_disabled(self):
        status = self.app.security_status()
        self.assertEqual(
            status,
            {
                "PAYMENT_EXECUTION_ENABLED": False,
                "AUTOMATIC_PAYMENT_DISPATCH": False,
                "AUTOMATIC_BANK_CHANGE": False,
            },
        )


if __name__ == "__main__":
    unittest.main()