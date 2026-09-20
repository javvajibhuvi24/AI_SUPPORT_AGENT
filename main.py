"""
Customer Support AI Agent
"""

from strands import Agent, tool
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamable_http_client

import argparse
import json
import os
import asyncio
import boto3
import logging
import uuid

from strands.hooks import (
    HookProvider,
    AfterInvocationEvent,
    HookRegistry,
    MessageAddedEvent,
)

from typing import Dict

from bedrock_agentcore.tools.code_interpreter_client import code_session
from strands_tools.browser import AgentCoreBrowser


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("CSAI_Agent")


# ─────────────────────────────────────────────────────────────────────────────
# TODO 1 — App Initialisation
# ─────────────────────────────────────────────────────────────────────────────

app = BedrockAgentCoreApp()

os.environ["BYPASS_TOOL_CONSENT"] = "true"


# ─────────────────────────────────────────────────────────────────────────────
# TODO 2 — Configuration
# ─────────────────────────────────────────────────────────────────────────────

GATEWAY_URL = (
    "https://customersupport-customersupportgateway-w9wvdzaotc.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
)

KB_ID = "MOXMKT9YKJ"

REGION = "us-east-1"

MEMORY_ID = "CustomerSupportMemory-gZ6M3DE5OO"


# ─────────────────────────────────────────────────────────────────────────────
# TODO 3 — Model and Clients
# ─────────────────────────────────────────────────────────────────────────────

model_id = "global.amazon.nova-2-lite-v1:0"

model = BedrockModel(model_id=model_id)

memory_client = MemoryClient(region_name=REGION)

_bedrock_runtime = boto3.client(
    "bedrock-agent-runtime",
    region_name=REGION,
)


# ─────────────────────────────────────────────────────────────────────────────
# TODO 4 — Namespace Helper
# ─────────────────────────────────────────────────────────────────────────────

def get_namespaces(mem_client: MemoryClient, memory_id: str) -> Dict:
    """Return a dict mapping strategy type → namespace template string."""
    try:
        strategies = mem_client.get_memory_strategies(memory_id)
        namespaces = {}
        for strategy in strategies:
            strategy_type = strategy["type"]
            namespace = strategy["namespaces"][0]
            namespaces[strategy_type] = namespace
        return namespaces
    except Exception as e:
        logger.warning("Failed to get memory strategies for %s: %s", memory_id, e)
        return {}


# ─────────────────────────────────────────────────────────────────────────────
# TODO 5 — Memory Hook
# ─────────────────────────────────────────────────────────────────────────────

class MemoryHook(HookProvider):
    """Long-term memory hook for the customer support agent."""

    def __init__(
        self,
        actor_id: str,
        session_id: str,
        memory_client: MemoryClient,
        memory_id: str,
    ):
        self.actor_id = actor_id
        self.session_id = session_id
        self.memory_client = memory_client
        self.memory_id = memory_id

        self.namespaces = get_namespaces(
            memory_client,
            memory_id,
        )

    def retrieve_customer_context(
        self,
        event: MessageAddedEvent,
    ):
        """Retrieve relevant memories and prepend them to the user message."""

        messages = event.agent.messages

        if not messages:
            return

        last_message = messages[-1]

        if last_message.get("role") != "user":
            return

        content = last_message.get("content", [])

        user_query = ""

        for block in content:
            if isinstance(block, dict) and "text" in block:
                user_query += block["text"]

        if not user_query:
            return

        memories = []

        for strategy_type, namespace_template in self.namespaces.items():

            namespace = namespace_template.replace(
                "{actorId}",
                self.actor_id,
            )

            try:
                results = self.memory_client.retrieve_memories(
                    memory_id=self.memory_id,
                    namespace=namespace,
                    query=user_query,
                    top_k=5,
                )

                for result in results:

                    memory_text = (
                        result
                        .get("content", {})
                        .get("text")
                    )

                    if memory_text:
                        memories.append(
                            f"[{strategy_type}] {memory_text}"
                        )

            except Exception as e:
                logger.warning(
                    "Memory retrieval failed for %s: %s",
                    strategy_type,
                    e,
                )

        if memories:

            context = (
                "Customer Context:\n"
                + "\n".join(memories)
                + "\n\n"
                + user_query
            )

            last_message["content"] = [
                {
                    "text": context
                }
            ]

    def save_support_interaction(
        self,
        event: AfterInvocationEvent,
    ):
        """Save the completed turn to memory after the agent responds."""

        messages = event.agent.messages

        customer_query = None
        agent_response = None

        # Walk backwards through messages
        for message in reversed(messages):

            role = message.get("role")
            content = message.get("content", [])

            text_parts = []

            for block in content:

                if isinstance(block, dict) and "text" in block:
                    text_parts.append(block["text"])

            text = "\n".join(text_parts).strip()

            if not text:
                continue

            if role == "assistant" and agent_response is None:
                agent_response = text

            elif role == "user" and customer_query is None:
                customer_query = text

            if customer_query and agent_response:
                break

        if not customer_query or not agent_response:
            return

        try:

            self.memory_client.create_event(
                memory_id=self.memory_id,
                actor_id=self.actor_id,
                session_id=self.session_id,
                messages=[
                    (customer_query, "USER"),
                    (agent_response, "ASSISTANT"),
                ],
            )

        except Exception as e:

            logger.warning(
                "Failed to save support interaction: %s",
                e,
            )

    def register_hooks(
        self,
        registry: HookRegistry,
    ) -> None:
        """Register both memory callbacks."""

        registry.add_callback(
            MessageAddedEvent,
            self.retrieve_customer_context,
        )

        registry.add_callback(
            AfterInvocationEvent,
            self.save_support_interaction,
        )


# ─────────────────────────────────────────────────────────────────────────────
# TODO 6 — Knowledge Base Tool
# ─────────────────────────────────────────────────────────────────────────────

@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the Amazon product catalog and support knowledge base.

    Use this for product specifications, return policies, warranty
    information, loyalty program details, and order status definitions.

    Args:
        query: The question or topic to search for.

    Returns:
        Relevant information retrieved from the knowledge base.
    """

    if not KB_ID or not KB_ID.strip():
        return (
            "Knowledge Base is not configured: KB_ID is empty or missing. "
            "Please configure KB_ID before attempting a knowledge-base search."
        )

    try:

        response = _bedrock_runtime.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalQuery={
                "text": query
            },
        )

        results = response.get(
            "retrievalResults",
            [],
        )

        if not results:
            return "No relevant information was found in the knowledge base."

        chunks = []

        for result in results:

            content = result.get(
                "content",
                {},
            )

            text = content.get(
                "text",
                "",
            )

            if text:
                chunks.append(text)

        if not chunks:
            return "No relevant information was found in the knowledge base."

        return "\n---\n".join(chunks)

    except Exception as e:

        logger.exception(
            "Knowledge Base retrieval failed"
        )

        return (
            "Unable to search the knowledge base right now. "
            f"Error: {e}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# TODO 7 — Loyalty Discount Tool
# ─────────────────────────────────────────────────────────────────────────────

@tool
def calculate_loyalty_discount(
    loyalty_points: int,
    tier: str,
    order_total: float,
    product_category: str = "standard",
) -> str:
    """
    Calculate the loyalty discount for a customer order using the
    AgentCore Code Interpreter.

    Args:
        loyalty_points:
            Customer's current points balance.

        tier:
            Customer tier — Silver, Gold, or Platinum.

        order_total:
            Order total in USD.

        product_category:
            standard, device, or fresh.

    Returns:
        Full discount breakdown and final price.
    """

    code = f"""
import json
import math

loyalty_points = {loyalty_points}
tier = {tier!r}
order_total = {order_total}
product_category = {product_category!r}

earn_rates = {{
    "standard": 1,
    "device": 2,
    "fresh": 5
}}

tier_rates = {{
    "Silver": 0.00,
    "Gold": 0.10,
    "Platinum": 0.15
}}

# Redeem points in blocks of 500.
points_redeemed = min(
    (loyalty_points // 500) * 500,
    int(order_total * 0.50 * 100)
)

# Convert points to dollar value.
# 500 points = $5.
points_discount = points_redeemed / 100.0

points_discount = min(
    points_discount,
    order_total * 0.50
)

subtotal_after_points = order_total - points_discount

tier_discount_pct = tier_rates.get(
    tier,
    0.00
)

tier_discount = (
    subtotal_after_points
    * tier_discount_pct
)

final_total = (
    subtotal_after_points
    - tier_discount
)

total_savings = (
    order_total
    - final_total
)

points_earned = int(
    math.floor(
        final_total
        * earn_rates.get(
            product_category,
            1
        )
    )
)

remaining_points = (
    loyalty_points
    - points_redeemed
)

result = {{
    "points_redeemed": points_redeemed,
    "tier_discount_pct": tier_discount_pct,
    "final_total": round(final_total, 2),
    "total_savings": round(total_savings, 2),
    "points_earned": points_earned,
    "remaining_points": remaining_points
}}

print(json.dumps(result))
"""

    try:

        with code_session(REGION) as session:
            try:
                result = session.invoke(
                    "executeCode",
                    {
                        "language": "python",
                        "code": code,
                        "clearContext": True,
                    },
                )
            except AttributeError:
                result = session.execute_code(
                    code=code,
                    language="python",
                )

        output_lines = []
        try:
            for event in result:
                if isinstance(event, dict):
                    text = event.get("stdout") or event.get("text") or ""
                    if text:
                        output_lines.append(text.strip())
        except TypeError:
            output_lines = [str(result)]

        return "\n".join(output_lines) if output_lines else json.dumps({"status": "ok"})

    except Exception as e:

        logger.warning(
            "Code Interpreter unavailable: %s",
            e,
        )

        tier_rates = {
            "Silver": 0.00,
            "Gold": 0.10,
            "Platinum": 0.15,
        }

        tier_discount_pct = tier_rates.get(
            tier,
            0.00,
        )

        tier_discount = (
            order_total
            * tier_discount_pct
        )

        final_total = (
            order_total
            - tier_discount
        )

        return json.dumps(
            {
                "points_redeemed": 0,
                "tier_discount_pct": tier_discount_pct,
                "final_total": round(
                    final_total,
                    2,
                ),
                "remaining_points": loyalty_points,
                "error": str(e),
            }
        )


# ─────────────────────────────────────────────────────────────────────────────
# TODO 8 — Agent Entrypoint
# ─────────────────────────────────────────────────────────────────────────────

@app.entrypoint
async def invoke(
    payload,
    context=None,
):
    """
    Main handler called by AgentCore for every incoming request.
    """

    try:

        user_input = payload.get(
            "prompt",
            "",
        )

        actor_id = payload.get(
            "customer_id",
            "anonymous",
        )

        session_id = payload.get(
            "session_id"
        )

        if not session_id:
            session_id = str(
                uuid.uuid4()
            )

        if not user_input:
            return "Please provide a customer support question."

        # Memory hook
        memory_hook = MemoryHook(
            actor_id=actor_id,
            session_id=session_id,
            memory_client=memory_client,
            memory_id=MEMORY_ID,
        )

        # Browser
        agent_core_browser = AgentCoreBrowser(
            region=REGION
        )

        tools = [
            search_knowledge_base,
            calculate_loyalty_discount,
            agent_core_browser.browser,
        ]

        # Gateway MCP connection
        gateway_client = MCPClient(
            lambda: streamable_http_client(
                GATEWAY_URL
            )
        )

        try:
            gateway_tools = await gateway_client.load_tools()
            tools.extend(gateway_tools)
            logger.info(
                "Gateway connected successfully. Loaded %d tools.",
                len(gateway_tools),
            )
        except TimeoutError:
            logger.exception("Gateway tool loading timed out")
        except ConnectionError:
            logger.exception("Gateway connection failed")
        except Exception as exc:
            logger.exception(
                "Gateway tool loading failed: %s", exc
            )

        system_prompt = """
You are a helpful customer support AI agent.

You help customers with:
- Product information
- Orders
- Customer information
- Returns and refunds
- Loyalty discounts
- Product support

Use the available tools whenever they provide authoritative information.

Use the knowledge base for product catalog and support-policy questions.

Use Gateway tools for customer and order operations.

Use the loyalty discount tool when calculating discounts.

Use the browser when live webpage information is required.

Use customer memory to personalize responses when relevant.

Never invent order information, customer information,
product specifications, refund status, or policy details.

Give concise and helpful answers.
"""

        agent = Agent(
            model=model,
            tools=tools,
            hooks=[memory_hook],
            system_prompt=system_prompt,
        )

        response = await agent.invoke_async(
            user_input
        )

        # Extract first text content block
        if hasattr(response, "content"):

            for block in response.content:

                if isinstance(block, dict):

                    if "text" in block:
                        return block["text"]

        return str(response)

    except Exception as e:

        logger.exception(
            "Agent invocation failed"
        )

        return (
            "I’m sorry, but I encountered an error "
            "while processing your request."
        )


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=str)
    args = parser.parse_args()

    response = asyncio.run(invoke(json.loads(args.payload)))
    print(response)


if __name__ == "__main__":
    app.run()
    
