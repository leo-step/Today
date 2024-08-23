from clients import async_openai_client
from memory import Memory, MessageType, ToolInvocation

async def generate_response(memory: Memory, tool_use: ToolInvocation):
    query = tool_use["input"]
    context = tool_use["output"]
    response = await async_openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"Answer the user's question using the following documents as context:\n\n{context}"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    }
                ]
            },
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stream=True
    )

    full_response = []
    async for chunk in response:
        chunk_content = chunk.choices[0].delta.content
        if chunk_content != None:
            full_response.append(chunk_content)
            yield chunk_content

    content = ''.join(full_response)
    memory.add_message(MessageType.AI, content, tool_use=tool_use)
