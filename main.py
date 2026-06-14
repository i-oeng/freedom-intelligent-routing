import base64
import difflib
import mimetypes
import time
from functools import lru_cache
from pathlib import Path
from typing import Literal

from anthropic import APIConnectionError, APIStatusError, APITimeoutError, Anthropic, RateLimitError
from pydantic import BaseModel, Field, field_validator

from config import DATA_DIR, PROJECT_ROOT, get_anthropic_model


@lru_cache(maxsize=1)
def get_client():
    return Anthropic()


TICKET_TYPES = [
    "Жалоба",
    "Смена данных",
    "Консультация",
    "Претензия",
    "Неработоспособность приложения",
    "Мошеннические действия",
    "Спам",
]

SENTIMENTS = ["Позитивный", "Нейтральный", "Негативный"]
LANGUAGES = ["KZ", "ENG", "RU"]


def normalize_choice(value, allowed_values, default):
    if value is None:
        return default

    cleaned = str(value).strip()
    if cleaned in allowed_values:
        return cleaned

    lowered = cleaned.lower()
    for allowed in allowed_values:
        if lowered == allowed.lower():
            return allowed

    match = difflib.get_close_matches(cleaned, allowed_values, n=1, cutoff=0.62)
    return match[0] if match else default


def create_message_with_retries(**kwargs):
    last_error = None
    for attempt in range(3):
        try:
            return get_client().messages.create(**kwargs)
        except (APIConnectionError, APITimeoutError, RateLimitError, APIStatusError) as exc:
            last_error = exc
            if attempt == 2:
                break
            time.sleep(1.5 * (attempt + 1))
    raise last_error


class TicketAnalysis(BaseModel):
    ticket_type: Literal[
        "Жалоба",
        "Смена данных",
        "Консультация",
        "Претензия",
        "Неработоспособность приложения",
        "Мошеннические действия",
        "Спам",
    ] = Field(
        description="Строго одно из: Жалоба, Смена данных, Консультация, Претензия, Неработоспособность приложения, Мошеннические действия, Спам"
    )
    sentiment: Literal["Позитивный", "Нейтральный", "Негативный"] = Field(
        description="Строго одно из: Позитивный, Нейтральный, Негативный"
    )
    priority: int = Field(
        ge=1,
        le=10,
        description="Срочность от 1 до 10. 10 = максимальная."
    )
    language: Literal["KZ", "ENG", "RU"] = Field(
        description="Строго: KZ, ENG, RU. По умолчанию RU."
    )
    summary: str = Field(
        description="Краткая суть (1 предложение) + рекомендация."
    )

    @field_validator("ticket_type", mode="before")
    @classmethod
    def normalize_ticket_type(cls, value):
        return normalize_choice(value, TICKET_TYPES, "Консультация")

    @field_validator("sentiment", mode="before")
    @classmethod
    def normalize_sentiment(cls, value):
        return normalize_choice(value, SENTIMENTS, "Нейтральный")

    @field_validator("language", mode="before")
    @classmethod
    def normalize_language(cls, value):
        return normalize_choice(str(value).upper() if value is not None else value, LANGUAGES, "RU")

    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, value):
        try:
            priority = int(value)
        except (TypeError, ValueError):
            return 1
        return min(max(priority, 1), 10)


def resolve_image_path(image_path):
    if not image_path or str(image_path).strip().lower() in {"nan", "none", ""}:
        return None

    candidate = Path(str(image_path).strip())
    if candidate.is_file():
        return candidate

    for base_dir in (DATA_DIR, PROJECT_ROOT / "eval"):
        resolved = base_dir / candidate.name
        if resolved.is_file():
            return resolved

    return None


def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception:
        return None


def analyze_ticket_text(description_text: str, image_path: str = None) -> dict:

    system_prompt = "Ты ИИ-ассистент. Выяви проблему по тексту и/или скриншоту."

    content = []
    
    if description_text and str(description_text).strip() != "" and str(description_text).lower() != "nan":
        content.append({"type": "text", "text": str(description_text)})
    else:
        content.append({"type": "text", "text": "Анализируй только по скриншоту."})

    resolved_image_path = resolve_image_path(image_path)
    if resolved_image_path:
        base64_image = encode_image(resolved_image_path)
        if base64_image:
            mime_type = mimetypes.guess_type(str(resolved_image_path))[0] or "image/jpeg"
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": base64_image,
                }
            })

    try:
        response = create_message_with_retries(
            model=get_anthropic_model(),
            max_tokens=500,
            temperature=0,
            system=system_prompt,
            messages=[
                {"role": "user", "content": content}
            ],
            tools=[{
                "name": "classify_ticket",
                "description": "Classify and summarize a CRM support ticket.",
                "input_schema": TicketAnalysis.model_json_schema(),
            }],
            tool_choice={"type": "tool", "name": "classify_ticket"},
        )

        for block in response.content:
            if block.type == "tool_use" and block.name == "classify_ticket":
                return TicketAnalysis.model_validate(block.input).model_dump()

        raise ValueError("Anthropic response did not include classify_ticket tool output.")
        
    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "ticket_type": "Консультация",
            "sentiment": "Нейтральный",
            "priority": 1,
            "language": "RU",
            "summary": "Ошибка ИИ."
        }


def answer_results_question(question: str, df_final_results) -> str:
    analysis_sample = df_final_results.head(200).to_csv(index=False)
    prompt = (
        f"Всего строк в таблице: {len(df_final_results)}.\n"
        f"Ниже максимум 200 строк CSV:\n{analysis_sample}\n\n"
        f"Вопрос: {question}"
    )

    response = create_message_with_retries(
        model=get_anthropic_model(),
        max_tokens=700,
        temperature=0,
        system=(
            "Ты CRM-аналитик. Отвечай только по предоставленному CSV. "
            "Не выполняй код и не выдумывай отсутствующие данные."
        ),
        messages=[{"role": "user", "content": prompt}],
    )

    return "".join(block.text for block in response.content if block.type == "text").strip()
