"""
Agent 2: State & Dependency Grapher Agent
Performs semantic dependency mapping across cataloged tools, establishes execution tiers,
identifies foreign key state harvesting, and defines teardown hooks.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from src.agents.introspector import ToolCatalog, EndpointSignature

class StateHandoff(BaseModel):
    source_tool: str
    source_field: str  # e.g., "$.id"
    target_tool: str
    target_param: str  # e.g., "user_id" or ":user_id"

class DAGNode(BaseModel):
    id: str
    tool_name: str
    tier: int
    dependencies: List[str] = []
    handoffs_received: List[StateHandoff] = []

class ExecutionDAG(BaseModel):
    nodes: List[DAGNode]
    execution_tiers: List[List[str]]  # List of tool_names per tier
    teardown_nodes: List[str] = []
    state_handoffs: List[StateHandoff] = []

class DependencyGrapherAgent:
    """Agent that builds a Directed Acyclic Graph (DAG) for test suite execution ordering."""

    def build_dag(self, catalog: ToolCatalog) -> ExecutionDAG:
        nodes: Dict[str, DAGNode] = {}
        handoffs: List[StateHandoff] = []
        teardown: List[str] = []

        # 1. Categorize tools by operation (Create / Read / Delete)
        create_tools = []
        read_tools = []
        delete_tools = []

        for ep in catalog.endpoints:
            if ep.method == "POST":
                create_tools.append(ep)
            elif ep.method == "GET":
                read_tools.append(ep)
            elif ep.method == "DELETE":
                delete_tools.append(ep)
                teardown.append(ep.tool_name)

        # 2. Assign Tiers
        # Tier 0: Primary entity creations with no FK requirements (e.g. create_user, create_item)
        # Tier 1: Dependent creations (e.g. create_order requiring user_id & item_ids)
        # Tier 2: Read operations on entities
        # Tier 3: Teardown / Deletions

        tier_0_tools = []
        tier_1_tools = []

        for ep in create_tools:
            has_fk = False
            for p in ep.parameters:
                if "user_id" in p.name or "item_id" in p.name or "id" in p.name and p.name != "id":
                    has_fk = True
                    break
            if has_fk:
                tier_1_tools.append(ep)
            else:
                tier_0_tools.append(ep)

        # Build Nodes for Tier 0
        for ep in tier_0_tools:
            nodes[ep.tool_name] = DAGNode(
                id=ep.tool_name,
                tool_name=ep.tool_name,
                tier=0,
                dependencies=[]
            )

        # Build Nodes for Tier 1 and record handoffs
        for ep in tier_1_tools:
            deps = []
            for p in ep.parameters:
                if "user_id" in p.name:
                    deps.append("create_user")
                    ho = StateHandoff(
                        source_tool="create_user",
                        source_field="id",
                        target_tool=ep.tool_name,
                        target_param=p.name
                    )
                    handoffs.append(ho)
                if "item_id" in p.name:
                    deps.append("create_item")
                    ho = StateHandoff(
                        source_tool="create_item",
                        source_field="id",
                        target_tool=ep.tool_name,
                        target_param=p.name
                    )
                    handoffs.append(ho)

            nodes[ep.tool_name] = DAGNode(
                id=ep.tool_name,
                tool_name=ep.tool_name,
                tier=1,
                dependencies=list(set(deps)),
                handoffs_received=[h for h in handoffs if h.target_tool == ep.tool_name]
            )

        # Build Nodes for Tier 2 (Reads)
        for ep in read_tools:
            deps = []
            if "user" in ep.tool_name:
                deps.append("create_user")
                handoffs.append(StateHandoff(
                    source_tool="create_user",
                    source_field="id",
                    target_tool=ep.tool_name,
                    target_param="user_id"
                ))
            elif "item" in ep.tool_name:
                deps.append("create_item")
                handoffs.append(StateHandoff(
                    source_tool="create_item",
                    source_field="id",
                    target_tool=ep.tool_name,
                    target_param="item_id"
                ))
            elif "order" in ep.tool_name:
                deps.append("create_order")
                handoffs.append(StateHandoff(
                    source_tool="create_order",
                    source_field="id",
                    target_tool=ep.tool_name,
                    target_param="order_id"
                ))

            nodes[ep.tool_name] = DAGNode(
                id=ep.tool_name,
                tool_name=ep.tool_name,
                tier=2,
                dependencies=list(set(deps)),
                handoffs_received=[h for h in handoffs if h.target_tool == ep.tool_name]
            )

        # Build Nodes for Tier 3 (Teardown/Deletions)
        for ep in delete_tools:
            deps = []
            if "user" in ep.tool_name:
                deps.append("create_user")
            elif "order" in ep.tool_name:
                deps.append("create_order")

            nodes[ep.tool_name] = DAGNode(
                id=ep.tool_name,
                tool_name=ep.tool_name,
                tier=3,
                dependencies=list(set(deps))
            )

        # Construct execution tiers
        max_tier = max([n.tier for n in nodes.values()]) if nodes else 0
        execution_tiers = []
        for t in range(max_tier + 1):
            tier_nodes = [n.tool_name for n in nodes.values() if n.tier == t]
            if tier_nodes:
                execution_tiers.append(tier_nodes)

        return ExecutionDAG(
            nodes=list(nodes.values()),
            execution_tiers=execution_tiers,
            teardown_nodes=teardown,
            state_handoffs=handoffs
        )
