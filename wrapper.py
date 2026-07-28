from ollama import AsyncClient


class OllamaClient:

    def __init__(self):
        self.client = AsyncClient(host="http://localhost:11434")

    async def chat(self, prompt: str):

        response = await self.client.chat(
            model="qwen3.5:2b",
            think=False,
            options={"temperature": 0.2, "max_tokens": 200},
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
                {"role": "user", "content": prompt},
            ],
        )

        return response['message']['content']

    async def embed(self, text: str):

        response = await self.client.embed(model="nomic-embed-text", input=text)

        return response["embeddings"][0]


if __name__ == "__main__":
    import asyncio

    async def main():

        client = OllamaClient()

        embed_response = await client.embed("queen")
        print("Embedding Response:", embed_response)

    asyncio.run(main())
