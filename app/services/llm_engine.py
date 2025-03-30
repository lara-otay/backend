import os
from openai import OpenAI
from app.services.schema_fetch import build_engineered_prompt

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  


def ask_llm_for_endpoint(user_prompt: str, trimmed_schema: dict) -> str:
    system_prompt = build_engineered_prompt(trimmed_schema)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.2,
        max_tokens=300
    )

    return response.choices[0].message.content
