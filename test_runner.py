
import asyncio
import json
from main import invoke

tests = [
    {"prompt": "Hi, I am Jane. I prefer concise responses.", "customer_id": "CUST-123", "session_id": "s-A"},
    {"prompt": "Do you remember my name and communication preference?", "customer_id": "CUST-123", "session_id": "s-B"},
    {"prompt": "I am a Gold member with 4250 points. Calculate my discount on a $150 standard order.", "customer_id": "CUST-123", "session_id": "t5"},
]

async def run_tests():
    for i, t in enumerate(tests, 1):
        print(f"\n--- Running Test {i} ---", flush=True)
        res = await invoke(t)
        print(f"Response: {res}", flush=True)
        if i == 1:
            print("Waiting 45s for memory extraction...", flush=True)
            await asyncio.sleep(45)

if __name__ == "__main__":
    asyncio.run(run_tests())

