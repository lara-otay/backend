import json
from openai import OpenAI
from app.services.schema_fetch import build_engineered_prompt  
from app.core.config import settings  
from typing import List, Dict, Any, Optional

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_structured_request(
    user_prompt: str, 
    trimmed_schema: dict,
    context: Optional[List[Dict[str, Any]]] = None
) -> dict:
    system_prompt = build_engineered_prompt(trimmed_schema)

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Add conversation context if available
    if context:
        for message in context:
            messages.append({
                "role": message["sender"],
                "content": message["content"]
            })

    # Add the current user prompt
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.2,
        max_tokens=500
    )

    llm_output = response.choices[0].message.content

    try:
        structured_request = json.loads(llm_output)
        return structured_request
    except json.JSONDecodeError:
        print("LLM response was not valid JSON:\n", llm_output)
        raise ValueError("LLM did not return valid JSON. Please refine the prompt.")
