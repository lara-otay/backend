import json
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import HTTPException

def get_active_schema_paths(db: Session) :
     #fetch the path of active  schemas
    query = text("SELECT file_path FROM SCHEMSYS WHERE active = True")
    results = db.execute(query).fetchall()

    if not results:
        raise HTTPException(status_code=404, detail="No active schemas found.")

    schema_paths = []
    for row in results:
        path = Path(row[0])
        if path.exists():
            schema_paths.append(path)
        else:
            print("No active schemas to fetch ")

    return schema_paths


def trim_schema_file(file_path: Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as file:
        schema_data = json.load(file)

    paths_section = schema_data.get("paths", {})
    trimmed = {}

    for path in paths_section:
        methods = paths_section[path]
        for method in methods:
            endpoint_info = methods[method]
            if isinstance(endpoint_info, dict):
                description = endpoint_info.get("description", "No description")
                method_and_path = f"{method.upper()} {path}"
                trimmed[method_and_path] = description

    return trimmed



def get_trimmed_active_schemas(db: Session) -> dict:
    """
    Loops through all active schema files, trims each one, 
    and returns a dictionary grouped by service name.
    """
    schema_paths = get_active_schema_paths(db)
    all_trimmed = {}

    for path in schema_paths:
        trimmed = trim_schema_file(path)
        service_name = path.parent.name.lower()
        all_trimmed[service_name] = trimmed

    return all_trimmed





def build_engineered_prompt(trimmed_schema: dict) -> str:
    prompt = "You are an API assistant.\n"
    prompt += "Your job is to return a complete structured API request based on the user's goal.\n"
    prompt += "Only respond with a JSON object like this:\n\n"
    prompt += """{
  "method": "GET",
  "url": "/products/123",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "name": "Product A",
    "price": 25.99
  }
}\n\n"""
    prompt += "Here are the available API endpoints:\n\n"

    for service, endpoints in trimmed_schema.items():
        prompt += f"Service: {service}\n"
        for method_path, desc in endpoints.items():
            prompt += f"- {method_path}: {desc}\n"
        prompt += "\n"

    prompt += "Now based on the user's prompt, return ONLY the full request as JSON. No extra text, no explanation."

    return prompt


