"""Ollama provider - Run LLMs locally using Ollama.

Ollama allows running open-source LLMs (LLaMA, Mistral, etc.) on local hardware.
Perfect for privacy-conscious deployments and for development.
"""

import os
import logging
from typing import Any, Dict, List, Optional, Generator

from .enhanced import EnhancedProvider
from .error_handler import ErrorTranslator
from .rate_limiter import get_rate_limit_coordinator

logger = logging.getLogger(__name__)


class OllamaProvider(EnhancedProvider):
    """Provider adapter for Ollama (local LLM inference)."""

    def __init__(self, api_key: str = "", model: str = "", base_url: str = ""):
        """Initialize Ollama provider.
        
        Args:
            api_key: Not used for Ollama (local), keeping for interface compatibility
            model: Model name (e.g., 'llama2', 'mistral', 'neural-chat')
            base_url: Ollama server URL (default: http://localhost:11434)
        """
        super().__init__(api_key, model)
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.translator = ErrorTranslator()
        self.rate_limiter = None

    @staticmethod
    def get_provider_name() -> str:
        """Return provider identifier."""
        return "ollama"

    def validate_credentials(self) -> tuple[bool, str]:
        """Validate Ollama is accessible on localhost.
        
        Ollama doesn't require API keys, but needs to be running locally.
        """
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                return True, ""
            return False, "Ollama server not responding correctly"
        except Exception as e:
            return False, f"Ollama not accessible at {self.base_url}: {e}"

    def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        intent_info: Optional[Dict[str, Any]] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Stream chat completion using Ollama.
        
        Ollama provides a REST API with streaming support (Server-Sent Events).
        """
        # Rate limiting check
        if not self.rate_limiter:
            self.rate_limiter = get_rate_limit_coordinator().get_limiter(self.name)
        
        can_request, wait_time = self.rate_limiter.can_request()
        if not can_request:
            raise RuntimeError(f"Rate limited. Wait {wait_time:.0f}s")
        
        self.rate_limiter.record_request()
        
        # Use enhanced caching and retry
        yield from self.stream_chat_with_caching(messages, intent_info, max_retries=2)

    # -- Ollama-specific lightweight system prompt -------------------------
    _OLLAMA_SYSTEM_PROMPT = (
        "Sei Amira, un'assistente domestica intelligente e amichevole.\n"
        "Rispondi in modo conciso e naturale nella lingua dell'utente.\n"
        "Se l'utente chiede di controllare dispositivi o sensori, descrivi "
        "l'azione richiesta; non hai accesso diretto ai dispositivi.\n"
        "Sii gentile, utile e vai dritto al punto."
    )

    def _prepare_messages(
        self,
        messages: List[Dict[str, Any]],
        intent_info: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Override: use a lightweight system prompt for Ollama.

        Local models running on weak CPUs (e.g. Celeron J4025) can't handle
        the full system prompt with 40+ tool descriptions (~7000 tokens).
        We replace it with a concise Italian persona prompt to stay well
        within the model's context window and speed up prefill.
        """
        # Build message list: lightweight system + conversation (no tool blocks)
        out: List[Dict[str, Any]] = [{"role": "system", "content": self._OLLAMA_SYSTEM_PROMPT}]
        for msg in messages:
            role = msg.get("role", "")
            # Skip tool-call / tool-result messages (Ollama can't use HA tools)
            if role == "tool":
                continue
            if role == "assistant" and msg.get("tool_calls"):
                continue
            content = msg.get("content", "")
            if content:
                out.append({"role": role, "content": content})
        # Keep last 6 turns to avoid overflowing small context windows
        if len(out) > 7:  # 1 system + 6 turns
            out = [out[0]] + out[-6:]
        return out

    def _do_stream(
        self,
        messages: List[Dict[str, Any]],
        intent_info: Optional[Dict[str, Any]] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """Actual Ollama local API call via httpx with tool calling support.

        Ollama applies the model's chat template (Go text/template or Jinja2)
        to message content.  Literal ``{`` / ``}`` inside text — common in
        smart-context JSON, tool descriptions, code examples — can trigger:
            Ollama HTTP 400: "Value looks like object, but can't find closing '}' symbol"
        We sanitise all string content to neutralise these patterns.
        """
        import json
        import httpx
        model = self.model or "llama2"
        base_url = getattr(self, "base_url", "http://localhost:11434")
        # Generous timeout for CPU-only inference on low-end hardware
        _timeout = httpx.Timeout(connect=15.0, read=300.0, write=10.0, pool=5.0)

        # ── Build lightweight message list directly (bypass _prepare_messages) ──
        # Local models on weak CPUs can't handle the full HA system prompt
        # (~7000 tokens with 48 tool descriptions). We replace it entirely.
        msgs: List[Dict[str, Any]] = [
            {"role": "system", "content": self._OLLAMA_SYSTEM_PROMPT}
        ]
        for msg in messages:
            role = msg.get("role", "")
            # Skip system messages (the big HA prompt), tool calls and tool results
            if role in ("system", "tool"):
                continue
            if role == "assistant" and msg.get("tool_calls"):
                continue
            content = msg.get("content", "")
            if content:
                # Truncate very long user messages (smart-context can be huge)
                if len(content) > 1000:
                    content = content[:1000] + "\n[...troncato per Ollama]"
                msgs.append({"role": role, "content": content})
        # Keep last 6 turns max to stay within small context window
        if len(msgs) > 7:  # 1 system + 6 turns
            msgs = [msgs[0]] + msgs[-6:]

        # ---- Sanitise messages for Ollama's template engine ----
        msgs = self._sanitize_messages(msgs)

        # Log what we're sending for debugging
        total_chars = sum(len(m.get("content", "")) for m in msgs)
        logger.info("Ollama request: model=%s, messages=%d, ~%d chars, url=%s",
                    model, len(msgs), total_chars, base_url)

        # No tool schemas for Ollama on weak hardware — tools cause template errors
        # and bloat the prompt. Ollama acts as a conversational-only assistant.
        body: Dict[str, Any] = {
            "model": model,
            "messages": msgs,
            "stream": True,
            # Reduce context window for faster prefill on weak CPUs
            "options": {"num_ctx": 2048},
        }

        accumulated_tool_calls: Dict[int, Dict] = {}

        try:
            yield from self._ollama_stream(base_url, body, _timeout, accumulated_tool_calls)
        except RuntimeError as exc:
            raise

    # ---- Ollama-specific helpers ------------------------------------------------

    @staticmethod
    def _escape_braces(text: str) -> str:
        """Neutralise ``{`` / ``}`` so Go/Jinja2 template engines don't
        interpret them as template actions.

        Strategy: insert a zero-width space (U+200B) right after every ``{``
        and right before every ``}``.  This is invisible when rendered but
        breaks the ``{{ }}`` / ``{% %}`` patterns the template engine looks for.
        Human-readable content is unaffected.
        """
        if not text or ('{' not in text and '}' not in text):
            return text
        return text.replace('{', '{\u200b').replace('}', '\u200b}')

    @classmethod
    def _sanitize_messages(cls, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deep-sanitise message content so brace-heavy text doesn't break
        Ollama's template engine."""
        sanitized = []
        for msg in messages:
            msg = dict(msg)  # shallow copy
            content = msg.get("content")
            if isinstance(content, str):
                msg["content"] = cls._escape_braces(content)
            elif isinstance(content, list):
                # Multi-modal content blocks
                new_parts = []
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        part = dict(part)
                        part["text"] = cls._escape_braces(part.get("text", ""))
                    new_parts.append(part)
                msg["content"] = new_parts
            sanitized.append(msg)
        return sanitized

    @classmethod
    def _sanitize_tool_schemas(cls, schemas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sanitise tool schema descriptions (which often contain JSON examples
        with ``{`` chars) so Ollama doesn't choke."""
        import copy
        clean = copy.deepcopy(schemas)
        for tool in clean:
            fn = tool.get("function") or tool
            if isinstance(fn.get("description"), str):
                fn["description"] = cls._escape_braces(fn["description"])
            params = fn.get("parameters") or {}
            for _pname, pdef in (params.get("properties") or {}).items():
                if isinstance(pdef.get("description"), str):
                    pdef["description"] = cls._escape_braces(pdef["description"])
        return clean

    def _ollama_stream(
        self,
        base_url: str,
        body: Dict[str, Any],
        _timeout: Any,
        accumulated_tool_calls: Dict[int, Dict],
    ) -> Generator[Dict[str, Any], None, None]:
        """Low-level httpx streaming call to Ollama /api/chat."""
        import json
        import httpx

        with httpx.stream(
            "POST", f"{base_url}/api/chat",
            json=body,
            timeout=_timeout,
        ) as response:
            if response.status_code != 200:
                error_text = response.read().decode("utf-8", errors="ignore")
                raise RuntimeError(f"Ollama HTTP {response.status_code}: {error_text[:300]}")
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    msg = event.get("message") or {}

                    # Text content
                    content = msg.get("content", "")
                    if content:
                        yield {"type": "text", "text": content}

                    # Tool calls (Ollama returns them in message.tool_calls)
                    for tc in msg.get("tool_calls") or []:
                        fn = tc.get("function") or {}
                        name = fn.get("name", "")
                        args = fn.get("arguments") or {}
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except Exception:
                                args = {}
                        if name:
                            idx = len(accumulated_tool_calls)
                            accumulated_tool_calls[idx] = {
                                "id": f"ollama_{idx}",
                                "name": name,
                                "arguments": json.dumps(args, ensure_ascii=False),
                            }

                    if event.get("done"):
                        done_event: Dict[str, Any] = {"type": "done", "finish_reason": "stop"}
                        if accumulated_tool_calls:
                            done_event["finish_reason"] = "tool_calls"
                            done_event["tool_calls"] = self._normalize_tool_calls(
                                list(accumulated_tool_calls.values())
                            )
                        yield done_event

                except json.JSONDecodeError:
                    continue

    def get_available_models(self) -> List[str]:
        """
        Fetches live list from Ollama API if available, otherwise returns defaults.
        """
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if "models" in data:
                    return [m.get("name", "") for m in data["models"]]
        except Exception:
            pass

        # No fake fallback — return empty so the UI only shows installed models
        return []

    def get_error_translations(self) -> Dict[str, Dict[str, str]]:
        """Get Ollama-specific error translations."""
        return {
            "connection_error": {
                "en": f"Ollama: Not accessible at {self.base_url}. Make sure Ollama is running locally.",
                "it": f"Ollama: Non accessibile su {self.base_url}. Assicurati che Ollama sia in esecuzione localmente.",
                "es": f"Ollama: No accesible en {self.base_url}. Asegúrate de que Ollama se está ejecutando localmente.",
                "fr": f"Ollama: Non accessible sur {self.base_url}. Assurez-vous qu'Ollama s'exécute localement.",
            },
            "timeout": {
                "en": "Ollama: Request timeout. Ollama might be busy or non-responsive.",
                "it": "Ollama: Timeout della richiesta. Ollama potrebbe essere occupato o non reattivo.",
                "es": "Ollama: Timeout de la solicitud. Ollama podría estar ocupado o no responder.",
                "fr": "Ollama: Délai d'attente de la demande. Ollama peut être occupé ou ne pas répondre.",
            },
            "model_not_found": {
                "en": "Ollama: Model not found. Make sure it's installed with 'ollama pull <model>'.",
                "it": "Ollama: Modello non trovato. Assicurati che sia installato con 'ollama pull <model>'.",
                "es": "Ollama: Modelo no encontrado. Asegúrate de que esté instalado con 'ollama pull <model>'.",
                "fr": "Ollama: Modèle non trouvé. Assurez-vous qu'il est installé avec 'ollama pull <model>'.",
            },
            "server_error": {
                "en": "Ollama: Server error. Check the Ollama logs for details.",
                "it": "Ollama: Errore del server. Controlla i log di Ollama per i dettagli.",
                "es": "Ollama: Error del servidor. Comprueba los registros de Ollama para obtener detalles.",
                "fr": "Ollama: Erreur serveur. Vérifiez les journaux Ollama pour plus de détails.",
            },
        }

    def normalize_error_message(self, error: Exception) -> str:
        """Convert Ollama error to user-friendly message."""
        error_msg = str(error).lower()

        if "connection" in error_msg or "refused" in error_msg:
            return f"Ollama: Not accessible at {self.base_url}. Make sure Ollama is running locally."
        if "timeout" in error_msg:
            return "Ollama: Request timeout. Ollama might be busy or non-responsive."
        if "model" in error_msg:
            return "Ollama: Model not found. Make sure it's installed with 'ollama pull <model>'."

        return f"Ollama error: {error}"
