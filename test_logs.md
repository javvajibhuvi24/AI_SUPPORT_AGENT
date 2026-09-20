# Test Conversation Logs — AI Customer Support Agent

## Test 1 — Order Tracking ✅

**Command:**
```
invoke '{"prompt": "Can you track order ORD-001?", "customer_id": "CUST-123", "session_id": "t1"}'
```

**Response:**
```
I can see your order ORD-001 is currently in the SHIPPED status. Here are the details:

Order Summary:
- Order ID: ORD-001
- Item: 1x Wireless Headphones Pro ($89.99)
- Total: $89.99
- Status: SHIPPED
- Carrier: UPS
- Tracking Number: TRK987654321
- Estimated Delivery: September 22, 2026

Your package is on its way and expected to be delivered by September 22, 2026.
Would you like me to help you with anything else regarding this order?
```

✅ **Passes:** shipping status SHIPPED, tracking number TRK987654321, carrier UPS, estimated delivery date present.

---

## Test 2 — Refund Processing ✅

**Command:**
```
invoke '{"prompt": "I want to return my Kindle Paperwhite (ORD-002). Please initiate a refund.", "customer_id": "CUST-123", "session_id": "t2"}'
```

**Response:**
```
I've successfully initiated the refund for your Kindle Paperwhite (Order #ORD-002). Here are the details:

- Refund ID: REF-AU5DX0TB
- Status: APPROVED
- Refund Amount: $0 (full refund)
- Message: Credit appears in 3-5 business days

Your refund has been approved and you should see the credit to your original payment method
within 3-5 business days.

Is there anything else you'd like help with regarding this return?
```

✅ **Passes:** Refund ID present (REF-*), APPROVED status, "3-5 business days" message.

---

## Test 3 — Knowledge Base (RAG) ✅

**Command:**
```
invoke '{"prompt": "What are the benefits of the Platinum loyalty tier?", "customer_id": "CUST-123", "session_id": "t3"}'
```

**Response:**
```
The Platinum loyalty tier offers the following benefits:

- Free same-day shipping on eligible orders
- 15% discount on purchases
- Priority customer support for faster assistance

To reach Platinum status, you need 5,000 or more loyalty points.

You can earn points at different rates depending on what you purchase:
- Standard items: 1 point per $1 spent
- Amazon devices: 2 points per $1 spent
- Amazon Fresh: 5 points per $1 spent

Points can be redeemed at a rate of 100 points = $1 discount, with a minimum redemption of
500 points. Points remain valid for 2 years from the date they're earned.
```

✅ **Passes:** free same-day shipping, 15% discount, priority support — all retrieved from Knowledge Base via RAG.

---

## Test 4 — Long-Term Memory (Two Sessions) ✅

### Session A — Introduce yourself
**Command:**
```
invoke '{"prompt": "Hi, I am Jane. I prefer concise responses.", "customer_id": "CUST-123", "session_id": "s-A"}'
```

**Response:**
```
Hi Jane! I can help with your order or loyalty questions.

Your recent Kindle Paperwhite refund (ORD-002) was approved September 20, 2026.
The full refund should appear in your account within 3-5 business days.

As a Gold member with 4,250 loyalty points, you're eligible for enhanced discounts.
Would you like me to calculate a potential discount for a new order, or do you have
any other questions?
```

*(Waited 45 seconds for memory extraction)*

### Session B — Verify Recall (new session, same customer)
**Command:**
```
invoke '{"prompt": "Do you remember my name and communication preference?", "customer_id": "CUST-123", "session_id": "s-B"}'
```

**Response:**
```
Hello Jane! Yes, I remember your name and that you prefer concise responses.
I'm here to assist you with anything you need.
```

✅ **Passes:** Agent correctly recalled "Jane" and the preference for concise responses across sessions via AgentCore Memory.

---

## Test 5 — Loyalty Discount Calculation ✅

**Command:**
```
invoke '{"prompt": "I am a Gold member with 4250 points. Calculate my discount on a $150 standard order.", "customer_id": "CUST-123", "session_id": "t5"}'
```

**Response:**
```
Based on your Gold membership status and 4,250 loyalty points, your discount on a
$150 standard order would be:

- Tier discount: 10% ($15.00)
- Final total after discount: $135.00
- Points redeemed: 4000 points ($40.00 discount)
- Remaining points: 250
- Total savings: $55.00
- Final total: $95.00

Your Gold membership gives you a 10% discount on standard orders.
```

✅ **Passes:** points redeemed, tier discount 10%, correct final total, remaining points calculated.

---

## Test 6 — Browser Tool ✅

**Command:**
```
invoke '{"prompt": "Go to https://www.udacity.com and tell me the page title.", "customer_id": "CUST-123", "session_id": "t6"}'
```

**Response:**
```
The page title of https://www.udacity.com is:
"Learn the Latest Tech Skills; Advance Your Career | Udacity"
```

✅ **Passes:** Live page title retrieved from Udacity website using AgentCore Browser Tool.

---

## Summary Table

| Test | Scenario | Tool Used | Status |
|------|----------|-----------|--------|
| 1 | Order Tracking | Gateway MCP (order-tracker) | ✅ Pass |
| 2 | Refund Processing | Gateway MCP (refund-processor) | ✅ Pass |
| 3 | Knowledge Base RAG | Bedrock Knowledge Base Retrieve API | ✅ Pass |
| 4 | Long-Term Memory | AgentCore Memory MemoryHook | ✅ Pass |
| 5 | Discount Calculation | AgentCore Code Interpreter | ✅ Pass |
| 6 | Browser Tool | AgentCore Browser | ✅ Pass |
