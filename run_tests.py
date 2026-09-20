"""
Run all 6 test scenarios cleanly on Windows / Python 3.14.
Usage:  uv run python run_tests.py
"""
import asyncio
import sys
import os

# Suppress nest_asyncio cleanup noise on Windows
os.environ["PYTHONIOENCODING"] = "utf-8"

from main import invoke


TESTS = [
    {
        "label": "Test 1 — Order Tracking",
        "payload": {
            "prompt": "Can you track order ORD-001?",
            "customer_id": "CUST-123",
            "session_id": "t1",
        },
    },
    {
        "label": "Test 2 — Refund Processing",
        "payload": {
            "prompt": "I want to return my Kindle Paperwhite (ORD-002). Please initiate a refund.",
            "customer_id": "CUST-123",
            "session_id": "t2",
        },
    },
    {
        "label": "Test 3 — Knowledge Base (RAG)",
        "payload": {
            "prompt": "What are the benefits of the Platinum loyalty tier?",
            "customer_id": "CUST-123",
            "session_id": "t3",
        },
    },
    {
        "label": "Test 4a — Memory Session A (introduce yourself)",
        "payload": {
            "prompt": "Hi, I am Jane. I prefer concise responses.",
            "customer_id": "CUST-123",
            "session_id": "s-A",
        },
        "wait_after": 45,   # seconds to wait for memory extraction
    },
    {
        "label": "Test 4b — Memory Session B (recall)",
        "payload": {
            "prompt": "Do you remember my name and communication preference?",
            "customer_id": "CUST-123",
            "session_id": "s-B",
        },
    },
    {
        "label": "Test 5 — Loyalty Discount Calculation",
        "payload": {
            "prompt": "I am a Gold member with 4250 points. Calculate my discount on a $150 standard order.",
            "customer_id": "CUST-123",
            "session_id": "t5",
        },
    },
    {
        "label": "Test 6 — Browser Tool",
        "payload": {
            "prompt": "Go to https://www.udacity.com and tell me the page title.",
            "customer_id": "CUST-123",
            "session_id": "t6",
        },
    },
]


async def main():
    # Run specific test if index passed as argument (1-based), else run all
    indices = [int(x) - 1 for x in sys.argv[1:]] if len(sys.argv) > 1 else range(len(TESTS))

    for i in indices:
        test = TESTS[i]
        print(f"\n{'='*60}")
        print(f"  {test['label']}")
        print(f"{'='*60}")
        print(f"  Prompt: {test['payload']['prompt']}")
        print()

        response = await invoke(test["payload"])

        print(f"RESPONSE:\n{response}")

        wait = test.get("wait_after", 0)
        if wait:
            print(f"\n  ... waiting {wait}s for memory extraction ...")
            await asyncio.sleep(wait)

    print("\n\nAll selected tests complete.")


if __name__ == "__main__":
    # Python 3.14 + nest_asyncio + Windows ProactorEventLoop causes a
    # harmless-but-noisy RuntimeError during shutdown. SelectorEventLoop avoids it.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
