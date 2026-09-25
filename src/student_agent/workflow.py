from __future__ import annotations

from typing import Any

from .mcp_gateway import EvidenceGateway
from .trace import TraceWriter


async def solve_case(
    case: dict[str, Any], gateway: EvidenceGateway, trace: TraceWriter
) -> dict[str, Any]:
    """Integration point for the A2A design in ARCHITECTURE.md (not implemented yet).

    Planned stages:
      1. Coordinator creates case-local scope, tool grants, budgets and evidence ledger.
      2. Entity/customer agent resolves candidates from MCP evidence.
      3. Order/item, payment and shipment agents investigate the resolved scope.
      4. Policy agent reconciles findings/conflicts and proposes a resolution.
      5. Verifier validates the L3B schema, evidence linkage and business invariants.

    Public schemas in contracts/schemas/ take precedence over agent findings.
    All tool calls must use EvidenceGateway through the planned permission-aware
    collector; observable events must use TraceWriter's existing schema fields.
    Return only a validated output object. The CLI owns case_received,
    case_finalized and output file persistence. Missing adapters must fail explicitly,
    never produce invented fallback answers. See ARCHITECTURE.md for retry limits.
    """
    del case, gateway, trace
    raise NotImplementedError("Implement the L3B multi-agent workflow in solve_case()")
