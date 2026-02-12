from __future__ import annotations

from enum import Enum
from json import loads
from sys import stderr
from typing import Optional

import requests
from flask import abort
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound

from app.config.llm_config import settings


class LLMService:
    model: str
    api_url: str
    api_key: str
    client: str

    def __init__(self) -> None:
        self.model = settings.model
        self.api_url = settings.api_url
        self.api_key = settings.api_key
        self.client = settings.client

    def ollama(self, message, max_tokens=600):
        try:
            payload = {"messages": message, "model": self.model, "stream": False, "response_format": {"type": "json_object"}, "max_tokens": max_tokens}
            headers = {"Authorization": f"Bearer {self.api_key}"}

            response = requests.post(url=f"{self.api_url}/openai/chat/completions", headers=headers, json=payload)

            response.raise_for_status()
            response_data = response.json()
            response_message = response_data['choices'][0]['message']['content']

            response_message_parsed = loads(response_message)
            return response_message_parsed

        except Exception as e:
            abort(InternalServerError.code, f"LLM call error: {e}")
            return None

    def open_ai(self, message, max_tokens=600):
        try:
            payload = {"messages": message, "model": self.model, "stream": False, "response_format": {"type": "json_object"}, "max_tokens": max_tokens}
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(url=self.api_url, headers=headers, json=payload)
            response.raise_for_status()

            response_data = response.json()
            response_message = response_data['choices'][0]['message']['content']

            response_message_parsed = loads(response_message)
            return response_message_parsed

        except Exception as e:
            abort(InternalServerError.code, f"LLM call error: {e}")
            return None

    def call_llm(self, message, max_tokens=600):
        if self.client == 'ollama':
            return self.ollama(message, max_tokens)
        elif self.client == 'open_ai':
            return self.open_ai(message, max_tokens)
        else:
            abort(BadRequest.code, "Invalid client specified")

    def diarize_transcription(self, agent: dict, client: dict, combined: dict):

        message = [
            {
                "role": "system",
                "content": """
                    You are a conversation diarization assistant.  

                    I will provide you with multiple speaker transcripts in JSON format.  
                    Each transcript includes:
                    - `speaker` name or ID
                    - `segments`: list of utterances with `text`, `start`, and `end` timestamps.

                    Your task is to:
                    1. Analyze the segments in all transcripts.
                    2. Arrange them into a natural, coherent conversation flow, ignoring the strict timestamps but using them as a guide for the logical sequence.
                    3. Merge related sentences and remove redundant or repeated phrases if necessary.
                    4. We have two speakers in the conversation, agent and client.
                    5. I want you to refer to the conversation in combined format, so you can better produce the order of the conversation speech.
                    6. Output the final diarized conversation in **JSON** with this structure:

                    {{
                    "conversation": [
                       
                        {{
                        "speaker": "agent",
                        "text": "Meetdown Computer Solutions, Helen speaking, how can I help you?"
                        }},
                        {{
                        "speaker": "client,
                        "text": "Hello, this is Ryan Bardos. May I speak with Natalie Jones, please?"
                        }},
                        ...
                    ]
                    }}

                    Keep the conversation realistic, polite, and natural. Do not change any words, phrases, punctuation, or any other details.
                    ```
                """,
            },
            {
                "role": "user",
                "content": f"""
                Please analyze the following conversation.
                agent : {agent}
                client : {client}

                combined_transcript: {combined}
                """,
            },
        ]
        try:
            result = self.call_llm(message)

            return result
        except Exception as e:
            abort(InternalServerError.code, f"Error during diarization: {e}")
