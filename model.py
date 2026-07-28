from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(
    model="qwen3.5:2b",
    think=False,
    options={"temperature": 0.4, "max_tokens": 200},
    messages=[
        {
            "role": "system",
            "content": """You are a helpful AI assistant.
                    Rules:
                        - Answer only using the provided context.
                        - If the answer is not in the context, say "I don't know."
                        - Be concise and factual.
                        - Respond in max 1 or 2 sentences
                    """,
        },
        {
            "role": "user",
            "content": "Why is the sky blue?",
        },
    ],
)


print(response.message.content)
