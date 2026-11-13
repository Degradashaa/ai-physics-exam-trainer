import json
from groq import Groq
from app import config

_client = None


def get_client() -> Groq:
    global _client
    if _client is None:
        if not config.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY не задан в .env")
        _client = Groq(api_key=config.GROQ_API_KEY)
    return _client


def chat_json(system: str, user: str, retries: int = 2) -> dict:
    client = get_client()
    last_err = None
    for _ in range(retries + 1):
        try:
            resp = client.chat.completions.create(
                model=config.MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS,
                response_format={"type": "json_object"},
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Groq API error: {last_err}")