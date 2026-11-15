import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests
from dotenv import load_dotenv
from tenacity import Retrying, retry_if_exception, stop_after_attempt, wait_exponential


def credential(name, url):
    """Lee una credencial de .env o del entorno y orienta sobre su obtención."""
    load_dotenv()
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Falta {name}. Obtén la credencial en {url} y configúrala en .env.")
    return value


def _retryable(error):
    if isinstance(error, requests.HTTPError):
        return error.response.status_code in {408, 429, 500, 502, 503, 504}
    return isinstance(error, (requests.ConnectionError, requests.Timeout))


def _wait(state):
    error = state.outcome.exception()
    if isinstance(error, requests.HTTPError):
        retry_after = error.response.headers.get("Retry-After")
        if retry_after:
            try:
                return max(0, int(retry_after))
            except ValueError:
                try:
                    target = parsedate_to_datetime(retry_after)
                    return max(0, (target - datetime.now(timezone.utc)).total_seconds())
                except (TypeError, ValueError):
                    pass
    return wait_exponential(multiplier=1, max=30)(state)


def request(method, url, *, retry=True, **kwargs):
    """Ejecuta una solicitud HTTP con timeout y reintentos para fallos transitorios."""
    attempts = Retrying(
        retry=retry_if_exception(_retryable),
        wait=_wait,
        stop=stop_after_attempt(4 if retry else 1),
        reraise=True,
    )
    for attempt in attempts:
        with attempt:
            response = requests.request(method, url, timeout=(10, 90), **kwargs)
            response.raise_for_status()
            return response
