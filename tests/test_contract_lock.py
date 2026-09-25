"""Release contract regressions: never relax published schemas to fit an output."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from student_agent.contracts import ContractError, Contracts

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "contracts" / "schemas"


def test_published_schema_inventory_and_content_are_locked() -> None:
    expected = json.loads((ROOT / "contracts" / "schema-lock.json").read_text("utf-8"))
    actual = {}
    for path in SCHEMAS.glob("*.schema.json"):
        schema = json.loads(path.read_text("utf-8"))
        Draft202012Validator.check_schema(schema)
        canonical = json.dumps(schema, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        actual[path.name] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert actual == expected, "Published schemas changed; use a deliberate versioned release"


@pytest.fixture
def contracts() -> Contracts:
    return Contracts(SCHEMAS)


def test_evidence_envelope_is_closed_but_data_is_open(contracts: Contracts) -> None:
    envelope = {
        "schema_version": "day09-mcp-evidence-v1",
        "evidence_ref": "ev_" + "a" * 20,
        "result_hash": "sha256:" + "0" * 64,
        "domain": "order",
        "data": {"domain_specific_field": [1, 2]},
    }
    contracts.validate_evidence(envelope)
    with pytest.raises(ContractError):
        contracts.validate_evidence({**envelope, "case_id": "CASE_001"})


def test_trace_rejects_new_event_types_and_nested_attributes(contracts: Contracts) -> None:
    event = {
        "schema_version": "day09-trace-event-v1",
        "event_id": "evt_" + "a" * 12,
        "case_id": "CASE_001",
        "event_type": "handoff",
        "occurred_at": "2026-09-25T00:00:00Z",
        "actor": "coordinator",
        "decision_code": "MCP_RETRY",
        "attributes": {"attempt": 1},
    }
    contracts.validate_trace(event, "test")
    for patch in (
        {"event_type": "retry"},
        {"attributes": {"payload": {"secret": "not allowed"}}},
        {"task_id": "task_1"},
        {"occurred_at": "not-a-date"},
    ):
        with pytest.raises(ContractError):
            contracts.validate_trace({**event, **patch}, "test")


def test_l3b_resolves_l3a_defs_and_rejects_extra_nested_fields(contracts: Contracts) -> None:
    # Synthetic contract fixture only, not a solver fallback or competition answer.
    output = {
        "schema_version": "day09-l3b-output-v2",
        "case_id": "CASE_001",
        "assessment": {"primary_issue": "insufficient_evidence", "secondary_issues": [],
                       "case_status": "needs_investigation", "confidence": 0},
        "affected_entities": {key: [] for key in (
            "order_ids", "item_ids", "seller_ids", "payment_references", "shipment_ids")},
        "entity_resolution": {"status": "not_found", "resolved_order_ids": [],
                              "rejected_candidates": [], "confidence": 0},
        "customer_context": {"customer_unique_id": None, "related_order_ids": []},
        "shipment_analysis": {"verdict": "insufficient_evidence", "late_seller_ids": [],
                              "timeline_complete": False},
        "payment_analysis": {"verdict": "insufficient_evidence", "captured_total_brl": None,
                             "refunded_total_brl": None, "refundable_total_brl": None},
        "root_cause_analysis": {"ranked_causes": [], "responsible_parties": []},
        "evidence_refs": [], "data_conflicts": [],
        "financial_resolution": {"currency": "BRL", "recommended_refund_brl": 0,
                                 "refund_lines": []},
        "resolution_actions": [],
    }
    contracts.validate_output(output, "test")
    with pytest.raises(ContractError):
        contracts.validate_output({**output, "debug": True}, "test")
    output["affected_entities"]["extra"] = []
    with pytest.raises(ContractError):
        contracts.validate_output(output, "test")


def test_manifest_variant_must_match_output_version(contracts: Contracts) -> None:
    manifest = {
        "schema_version": "day09-submission-manifest-v2",
        "competition_id": "day09-multiagent-mcp-a2a",
        "variant_id": "l3b", "case_set_version": "test-v1",
        "output_schema_version": "day09-l3b-output-v2",
        "trace_schema_version": "day09-trace-event-v1",
        "generated_at": "2026-09-25T00:00:00Z",
    }
    contracts.validate_manifest(manifest)
    with pytest.raises(ContractError):
        contracts.validate_manifest({**manifest, "output_schema_version": "day09-l3a-output-v2"})
    with pytest.raises(ContractError):
        contracts.validate_manifest({**manifest, "extra": True})
