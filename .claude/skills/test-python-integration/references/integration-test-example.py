"""Integration test for bank transaction import with automatic template matching.

Tests that when a bank transaction is imported and matches a posting template's
auto_apply_keyword and auto_apply_counterparty, postings are automatically created.

This is an example of a well-structured integration test that:
1. Uses TestClient for real HTTP requests
2. Uses accounting_prerequisites fixture for common setup
3. Creates test-specific data via API calls
4. Tests a complete end-to-end workflow
5. Verifies results through API responses
"""

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.integration.conftest import AccountingPrerequisites

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_import_creates_postings_from_auto_apply_template(
    test_client: "TestClient",
    auth_headers: dict[str, str],
    accounting_prerequisites: AccountingPrerequisites,
    csv_file_path: Path,
) -> None:
    """Bank transaction import should auto-apply matching template and create postings.

    Setup:
    1. Create posting template with auto_apply_keyword="PALVELUMAKSU"
       and auto_apply_counterparty="OSUUSPANKKI"
    2. Template has 2 rows: debit to 3973 (Pankkikulut), credit to 1910 (Pankkitili)

    Test:
    1. Import CSV with transaction matching the template criteria
    2. Verify import response shows postings were created
    3. Query postings for the transaction
    4. Assert 2 postings exist with correct accounts and amounts
    """
    bank_account_id = accounting_prerequisites.bank_account_id

    # 1. Create posting template with auto-apply settings
    template_response = test_client.post(
        "/api/private/posting-templates",
        json={
            "name": "OP Palvelumaksu",
            "is_primary": True,
            "auto_apply_keyword": "PALVELUMAKSU",
            "auto_apply_counterparty": "OSUUSPANKKI",
            "rows": [
                {
                    "side": {"type": "fixed", "value": "debit"},
                    "amount": {"type": "equation", "value": "=abs([bt.amount])"},
                    "comment": {"type": "fixed", "value": "OP Palvelumaksu"},
                    "dim1_code": "3973",
                },
                {
                    "side": {"type": "fixed", "value": "credit"},
                    "amount": {"type": "equation", "value": "=abs([bt.amount])"},
                    "comment": {"type": "fixed", "value": "OP Palvelumaksu"},
                    "dim1_code": "1910",
                },
            ],
        },
        headers=auth_headers,
    )
    assert template_response.status_code == 201, f"Failed to create template: {template_response.json()}"

    # 2. Import CSV file
    with open(csv_file_path, "rb") as f:
        import_response = test_client.post(
            f"/api/private/bank-transactions/import/{bank_account_id}",
            files={"file": ("op_palvelumaksu.csv", f, "text/csv")},
            headers=auth_headers,
        )

    assert import_response.status_code == 200, f"Import failed: {import_response.json()}"
    import_result = import_response.json()

    # 3. Verify import response (response uses camelCase)
    assert import_result["imported"] == 1, "Expected 1 transaction to be imported"
    assert import_result["autoAppliedTemplates"] == 1, f"Expected 1 template auto-applied"
    assert import_result["autoAppliedPostings"] == 2, "Expected 2 postings to be created"

    # 4. Get the imported transaction
    transactions_response = test_client.get(
        "/api/private/bank-transactions",
        params={"bank_account_id": bank_account_id},
        headers=auth_headers,
    )
    assert transactions_response.status_code == 200
    transactions = transactions_response.json()["items"]
    assert len(transactions) == 1, "Expected 1 transaction"
    transaction_id = transactions[0]["id"]

    # 5. Query postings for the transaction
    postings_response = test_client.get(
        f"/api/private/postings/transaction/{transaction_id}",
        headers=auth_headers,
    )
    assert postings_response.status_code == 200
    postings = postings_response.json()["items"]

    # 6. Assert postings were created correctly
    assert len(postings) == 2, f"Expected 2 postings, got {len(postings)}"

    # Find debit and credit postings
    debit_posting = next((p for p in postings if p["side"] == "debit"), None)
    credit_posting = next((p for p in postings if p["side"] == "credit"), None)

    assert debit_posting is not None, "Expected a debit posting"
    assert credit_posting is not None, "Expected a credit posting"

    # Verify debit posting (to Pankkikulut account 3973)
    assert debit_posting["dim1"]["code"] == "3973"
    assert debit_posting["amount"] == "9.4"
    assert debit_posting["comment"] == "OP Palvelumaksu"

    # Verify credit posting (to Pankkitili account 1910)
    assert credit_posting["dim1"]["code"] == "1910"
    assert credit_posting["amount"] == "9.4"
    assert credit_posting["comment"] == "OP Palvelumaksu"

    # Verify both postings are linked to the transaction
    assert debit_posting["bankTransactionId"] == transaction_id
    assert credit_posting["bankTransactionId"] == transaction_id
