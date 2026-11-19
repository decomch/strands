import json
from strands import Agent, tool
from strands.models import BedrockModel
from dotenv import load_dotenv
load_dotenv()

from customer_service_tools import lookup_customer, get_order_history, process_refund

SYSTEM_PROMPT = """You are a customer service agent for an online electronics store.
Be helpful, professional, and concise. Use the available tools to look up customer
information and process requests.

Important guidelines:
- Always verify the customer using lookup_customer before taking action.
- Use tool data to answer questions — don't ask the customer for info you already have.
- Be warm but efficient."""

model = BedrockModel(model_id="deepseek.v3-v1:0", max_tokens=1000, streaming=False)

def main():
    # One agent instance reused across turns - it keeps conversation history in
    # agent.messages, which is what makes the conversation multi-turn.
    
    # Define a custom handler to tweek how much output you want from the model 

    # def my_handler(**kwargs):
    #     if "data" in kwargs:
    #         print(f"\ndata: {kwargs['data']}", end="")  # a text chunk
            
    #     if "current_tool_use" in kwargs:
    #         print(f"\ntool: {kwargs['current_tool_use']}", end="")  # tool call info



    agent = Agent(
        model=model,
        tools=[lookup_customer, get_order_history, process_refund],
        system_prompt=SYSTEM_PROMPT,
        callback_handler=None,
    )

    print("Customer service agent - type 'quit' to exit.")
    print("Try: \"Hi, I'm customer C-1001. What are my recent orders?\"\n")

    while True:
        try:
            turnIndex = len(agent.messages)
            user_input = input(f"\n[{turnIndex}] 👤 USER: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            break
        if not user_input:
            continue

        turnIndex += 1
        agent(user_input)
        for i, msg in enumerate(agent.messages[turnIndex:], start = turnIndex):
            role = msg["role"]
            if role == "user":
                text = msg["content"][0].get("text", "") if msg["content"] else ""
                if text.strip():
                    print(f"\n[{i}] 👤 USER: {text[:80]}")
            elif role == "assistant":
                for block in msg.get("content", []):
                    if "text" in block:
                        print(f"\n[{i}] 🤖 ASSISTANT: {block['text'][:100]}...")
                    elif "toolUse" in block:
                        tu = block["toolUse"]
                        print(f"\n[{i+1}] 🔧 TOOL CALL: {tu['name']}({json.dumps(tu.get('input', {}))})")
        
    print("\n" + "=" * 60)
    print(f"\n📊 Metrics:")
    summary = agent.event_loop_metrics.get_summary()
    print(f"   Cycles: {summary['total_cycles']}")
    print(f"   Tokens: {summary['accumulated_usage']['totalTokens']}")


if __name__ == "__main__":
    main()
