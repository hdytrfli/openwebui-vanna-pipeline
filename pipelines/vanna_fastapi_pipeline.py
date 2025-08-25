"""
title: Vanna Pipeline
author: Rafli
author_url: https://github.com/hdytrfli
description: Generates SQL queries from natural language questions using a Vanna backend, and formats results with Ollama.
required_open_webui_version: 0.4.3
requirements: requests
version: 0.4.3
licence: MIT
"""

import os
import requests
import logging
import json
from urllib.parse import urljoin
from pydantic import BaseModel, Field
from typing import List, Union, Generator, Iterator, Optional, Dict, Any

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class APIError(Exception):
    """Custom exception for API-related errors."""

    pass


def _make_request(
    url: str,
    params: Dict[str, Any],
    verify_ssl: bool,
    required_fields: List[str],
) -> Dict[str, Any]:
    """
    Makes HTTP request and validates response.

    Args:
        url: Request URL
        params: Request parameters
        verify_ssl: Whether to verify SSL certificates
        required_fields: Required fields in response

    Returns:
        Validated JSON response

    Raises:
        APIError: For any request or validation errors
    """
    try:
        resp = requests.get(url, params=params, verify=verify_ssl, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        missing = [f for f in required_fields if f not in data]
        if missing:
            raise APIError(f"Missing fields in response: {missing}")

        return data
    except requests.exceptions.RequestException as e:
        raise APIError(f"Request failed: {e}")
    except json.JSONDecodeError as e:
        raise APIError(f"Invalid JSON response: {e}")


def _generate_sql_from_vanna(
    api_url: str, question: str, verify_ssl: bool
) -> Dict[str, Any]:
    """Generates SQL query from natural language question."""
    url = urljoin(api_url, "/api/generate_sql")
    return _make_request(url, {"question": question}, verify_ssl, ["text", "id"])


def _run_sql_query(api_url: str, cache_id: str, verify_ssl: bool) -> Dict[str, Any]:
    """Executes SQL query using cache ID."""
    url = urljoin(api_url, "/api/run_sql")
    return _make_request(url, {"id": cache_id}, verify_ssl, ["df_markdown"])


def _generate_plotly_figure(
    api_url: str, cache_id: str, verify_ssl: bool
) -> Dict[str, Any]:
    """Generates Plotly figure from query results."""
    url = urljoin(api_url, "/api/generate_plotly_figure")
    return _make_request(url, {"id": cache_id}, verify_ssl, ["chart_url"])


class Pipeline:
    class Valves(BaseModel):
        API_URL: str = Field(
            default="http://host.docker.internal:4321",
            description="The base URL of your Vanna backend",
        )
        VERIFY_SSL: bool = Field(
            default=True, description="Set to False to disable SSL verification"
        )
        DEBUG: bool = Field(
            default=False, description="Enable debug logging for the pipeline"
        )
        OLLAMA_BASE_URL: str = Field(
            default="http://host.docker.internal:11434",
            description="The base URL for the Ollama API",
        )
        OLLAMA_MODEL_NAME: str = Field(
            default="llama3",
            description="The name of the Ollama model to use for formatting",
        )

    def __init__(self):
        self.name = "Vanna Pipeline"
        fields = self.Valves.model_fields.items()
        self.valves = self.Valves(**{k: os.getenv(k, v.default) for k, v in fields})
        logger.setLevel(logging.DEBUG if self.valves.DEBUG else logging.INFO)

    async def on_startup(self):
        logger.info(f"on_startup: {self.name}")

    async def on_shutdown(self):
        logger.info(f"on_shutdown: {self.name}")

    async def inlet(
        self, body: Dict[str, Any], user: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        logger.debug(f"inlet: {self.name}")
        return body

    async def outlet(
        self, body: Dict[str, Any], user: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        logger.debug(f"outlet: {self.name}")
        return body

    def status(self, desc: str, done: bool) -> Dict[str, Any]:
        """Helper function to yield status update."""
        return {
            "event": {
                "type": "status",
                "data": {"description": desc, "done": done},
            }
        }

    def ollama(self, msgs: List[Dict[str, Any]]) -> Generator[str, None, None]:
        """
        Streams completions from Ollama API with robust error handling.

        Args:
            msgs: List of message dictionaries

        Yields:
            Content chunks from Ollama model response

        Raises:
            APIError: For any API-related errors
        """
        payload = {
            "model": self.valves.OLLAMA_MODEL_NAME,
            "messages": msgs,
            "stream": True,
        }

        url = urljoin(self.valves.OLLAMA_BASE_URL, "/v1/chat/completions")

        try:
            with requests.post(url, json=payload, stream=True, timeout=60) as resp:
                resp.raise_for_status()

                for chunk in resp.iter_lines(decode_unicode=True):
                    if not chunk or not chunk.startswith("data: "):
                        continue

                    try:
                        if chunk == "data: [DONE]":
                            break

                        data = json.loads(chunk[6:])

                        choices = data.get("choices", [])
                        if not choices:
                            continue

                        delta = choices[0].get("delta", {})
                        content = delta.get("content")

                        if content:
                            yield content

                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse chunk: {chunk}")
                        continue

        except requests.exceptions.RequestException as e:
            raise APIError(f"Ollama request failed: {e}")

    def pipe(
        self,
        user_message: str,
        model_id: str,
        messages: List[Dict[str, Any]],
        body: Dict[str, Any],
    ) -> Union[str, Generator, Iterator]:
        """Main pipeline processing function."""

        if user_message.strip().startswith("### Task"):
            try:
                yield from self.ollama(messages)
            except APIError as e:
                logger.exception(f"Task processing error: {e}")
                yield f"Error processing task: {e}"
            return

        cache_id = None

        try:
            yield self.status("Generating SQL...", False)

            resp = _generate_sql_from_vanna(
                self.valves.API_URL, user_message, self.valves.VERIFY_SSL
            )
            sql_text = resp["text"]
            cache_id = resp["id"]

            yield f"```sql\n{sql_text}\n```"

        except APIError as e:
            logger.exception(f"SQL generation error: {e}")
            yield self.status("Error during SQL generation", True)
            return

        try:
            yield self.status("Running SQL query and rendering results...", False)

            resp = _run_sql_query(self.valves.API_URL, cache_id, self.valves.VERIFY_SSL)
            df_json = resp.get("df", {})
            df_md = resp["df_markdown"]

            yield "\n### Data result\n\n"

            prompt_msgs = [
                {
                    "role": "user",
                    "content": (
                        f"Carefully analyze the following JSON data: {json.dumps(df_json)}\n\n"
                        "**Task:**\n"
                        "Based on the processed and focused data, provide a concise, insightful summary of the key information. "
                        f"Following the summary, accurately render the data into a Markdown table using the provided structure: {df_md}\n\n"
                        "**Output Format:** Your response must be **plain text**, beginning with the summary and immediately followed by the Markdown table."
                        "All currency values must be in Rupiah or IDR (the data already saved in IDR), and all numbers must be rounded to two decimal places."
                        "**Absolutely do not wrap any part of your output in a code block**.\n"
                    ),
                }
            ]

            yield from self.ollama(prompt_msgs)

        except APIError as e:
            logger.exception(f"Summary generation error: {e}")
            yield self.status("Error during summary generation", True)
            return

        try:
            yield self.status("Generating Plotly chart...", False)

            resp = _generate_plotly_figure(
                self.valves.API_URL, cache_id, self.valves.VERIFY_SSL
            )
            chart_url = resp["chart_url"]

            yield "\n### Visualization\n\n"
            yield f"\n![{chart_url}]({chart_url})\n\n"

        except APIError as e:
            logger.warning(f"Could not generate Plotly chart: {e}")
            yield self.status("Plotly chart generation skipped", True)

        yield self.status("Formatting results complete", True)
