from pathlib import Path
import re
import sys

patterns = (r"payment\.execute\s*\(", r"wire\.send\s*\(", r"ach\.dispatch\s*\(", r"vendor\.bank_account\s*=", r"vendor\.update_banking\s*\(", r"erp\.update_vendor\s*\(")
root = Path(__file__).resolve().parents[1]
scan_roots = [root / name for name in ("src", "bec", "email", "risk", "quarantine", "proposal_creation")]
violations = []
for directory in scan_roots:
    if not directory.exists():
        continue
    for path in directory.rglob("*.py"):
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if any(re.search(pattern, line) for pattern in patterns):
                violations.append(f"{path}:{line_no}")
if violations:
    print("Forbidden patterns found:\n" + "\n".join(violations))
    sys.exit(1)
print("FORBIDDEN_PATTERN_SCAN=PASS")
