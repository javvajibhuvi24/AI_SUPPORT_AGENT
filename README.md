# 🤖 Customer Support AI Agent

An AI-powered customer support agent built using **Amazon Bedrock AgentCore, Strands Agents, Amazon Bedrock, MCP Gateway, AWS Lambda, Knowledge Base, Memory, Code Interpreter, and AgentCore Browser**.

The agent can understand customer queries, retrieve product information, access customer and order data, provide personalized responses using memory, calculate loyalty discounts, and perform backend customer-support operations through AgentCore Gateway tools.

---

## 🚀 Features

- 🤖 AI Customer Support Agent powered by Amazon Bedrock and Strands Agents
- 🔎 Knowledge Base Retrieval for product and support information
- 🧠 Long-term Customer Memory using Amazon Bedrock AgentCore Memory
- 🔌 MCP Gateway Integration for backend customer-support tools
- 📦 Order Tracking through API Gateway and AWS Lambda
- 💳 Refund Processing through Lambda-backed Gateway tools
- 🎁 Loyalty Discount Calculation using Code Interpreter
- 🌐 Live Web Browsing using AgentCore Browser
- 👤 Customer Personalization using stored customer context
- 🔄 Cross-session Memory using customer IDs
- ☁️ AgentCore Runtime Deployment

---

## 🏗️ Architecture

```text
                         Customer
                            │
                            ▼
                  ┌──────────────────┐
                  │  AgentCore       │
                  │     Runtime      │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  Strands AI      │
                  │     Agent        │
                  └────────┬─────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
   Knowledge Base       Memory          MCP Gateway
          │                │                │
          ▼                ▼        ┌───────┴────────┐
   Product / Support   Customer     │                │
      Information      Context      ▼                ▼
                               API Gateway        Lambda
                                   │          ┌──────┴──────┐
                                   ▼          │             │
                              Order APIs   Order Tracker  Refund

🛠️ Technologies Used

AI & Agent

* Python
* Strands Agents
* Amazon Bedrock
* Amazon Nova Lite
* Amazon Bedrock AgentCore

AgentCore Capabilities

* AgentCore Runtime
* AgentCore Gateway
* AgentCore Memory
* AgentCore Browser
* Code Interpreter

AWS Services

* AWS Lambda
* Amazon API Gateway
* Amazon S3
* Amazon Bedrock Knowledge Bases
* AWS IAM

Development Tools

* VS Code
* AWS CLI
* uv
* Git & GitHub
* MCP

⸻

🔌 Gateway Tools

The agent connects to an AgentCore Gateway using MCP.

Order Management

The Gateway provides access to:

* get_order
* get_customer_orders
* get_customer

Refund Management

The Gateway also provides:

* initiate_refund
* check_refund_status
* get_return_label

This allows the AI agent to select the appropriate backend operation based on the customer’s request.

⸻

🧠 Agent Intelligence

Knowledge Base

The search_knowledge_base tool uses the Amazon Bedrock Retrieve API to search the customer-support knowledge base and return relevant product or support information.

Customer Memory

The agent uses Amazon Bedrock AgentCore Memory to maintain customer context across interactions.

Memory strategies include:

* Customer facts
* Customer preferences

The memory hook retrieves relevant customer information before an agent response and stores important interactions afterward.

Loyalty Discounts

The calculate_loyalty_discount tool uses customer loyalty points and membership tier information to calculate the applicable discount and final order total.

The calculation is executed using the AgentCore Code Interpreter.

Browser

The agent can use AgentCore Browser to retrieve information from live webpages when required.

⸻

📁 Project Structure

AI_SUPPORT_AGENT/
│
├── starter/
│   ├── main.py
│   ├── pyproject.toml
│   └── ...
│
├── CustomerSupportRuntime/
│   ├── app/
│   │   └── CustomerSupportAgent/
│   │       ├── main.py
│   │       ├── pyproject.toml
│   │       └── README.md
│   │
│   └── agentcore/
│       └── AgentCore configuration
│
└── README.md

⚙️ Prerequisites

Before running the project, make sure you have:

* Python 3.13+
* AWS CLI
* AWS credentials configured
* uv
* Node.js
* AgentCore CLI
* Access to Amazon Bedrock models
* Required AWS resources configured

⸻

🚀 Local Setup

Clone the repository:
git clone https://github.com/javvajibhuvi24/AI_SUPPORT_AGENT.git

Navigate into the project:
cd AI_SUPPORT_AGENT

Navigate to the AgentCore runtime:
cd starter/CustomerSupportRuntime/app/CustomerSupportAgent

Install dependencies:
uv sync

Run the agent locally:
uv run python main.py

☁️ AgentCore Deployment

The project is structured for deployment using the Amazon Bedrock AgentCore CLI.

From the AgentCore runtime project directory:
agentcore status

Deploy using:
agentcore deploy

After deployment, the AgentCore Runtime can be invoked using the generated runtime configuration.

⸻

🧪 Testing

The project tests the following capabilities:

1. Agent invocation
2. Knowledge Base retrieval
3. Customer memory retrieval
4. Gateway API-based tool invocation
5. Gateway Lambda-based tool invocation
6. Loyalty discount calculation
7. Cross-session customer memory
8. Browser-based retrieval

⸻

💡 Design Decision

I integrated the AgentCore Gateway tools directly into the agent’s tool list before creating the Strands agent. This keeps the Gateway integration simple while allowing the agent to combine Gateway operations with memory, Knowledge Base retrieval, Code Interpreter, and browser capabilities.

This hybrid approach allows the agent to use the appropriate capability depending on the customer’s request. Backend operations such as order tracking and refund processing are delegated through the Gateway, while knowledge retrieval, personalization, and loyalty calculations are handled by dedicated agent tools.

⸻

🛠️ Challenge Encountered

One of the main challenges was the context-management behavior of the Strands MCPClient, which varied with the SDK version being used.

Initially, I used an async with block, but this resulted in a TypeError because the MCPClient did not support the asynchronous context-manager protocol in my environment.

I then tried a standard with block, but calling load_tools() inside it caused an MCPClientInitializationError because the client session was initialized more than once.

I resolved the issue by removing the explicit context-manager wrapper and calling:

await gateway_client.load_tools()

directly. This allowed the MCP client to manage its own connection lifecycle and successfully load the Gateway tools.

⸻

🔐 Production Considerations

The current development configuration uses a Gateway with a NONE authorizer for testing.

For production deployment, the Gateway should use appropriate authentication and authorization mechanisms such as:

* JWT/OAuth authentication
* AWS SigV4
* IAM-based access control

Customer-specific authorization should also ensure that users can access only the orders, refunds, and customer information associated with their authenticated identity.

Additional production improvements could include:

* Secure secret management
* Request validation
* Audit logging
* Rate limiting
* Monitoring and alerting
* Error handling and retries

⸻

🔮 Future Improvements

Potential improvements include:

* Stronger Gateway authentication
* Customer identity verification
* Structured tool outputs using Pydantic
* Improved response summarization
* More personalized customer recommendations
* Additional order and refund operations
* Production monitoring and logging
* Automated testing
* CI/CD integration

⸻

📜 License

This project was developed as part of an AWS Bedrock AgentCore / Udacity learning project for educational purposes.