from clients import async_openai_client

async def generate_response(query_text, context):
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
                        "text": query_text
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

    async for chunk in response:
        if chunk.choices[0].delta.content != None:
            yield chunk.choices[0].delta.content
