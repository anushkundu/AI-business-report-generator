# src/utils/llm_client.py

"""
LLM CLIENT — OpenAI + Google Gemini
Works locally (.env) and on Streamlit Cloud (secrets)
"""

import json
import time
import os
from typing import Optional, Dict
from dotenv import load_dotenv
from src.utils.config import config
from src.utils.logger import logger

load_dotenv()

# Load Streamlit Cloud secrets
try:
    import streamlit as st
    if hasattr(st, 'secrets'):
        for key in ['OPENAI_API_KEY', 'GOOGLE_API_KEY']:
            if key in st.secrets:
                os.environ[key] = st.secrets[key]
except Exception:
    pass

# Import providers
try:
    from openai import OpenAI, RateLimitError, APIError, APIConnectionError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


class LLMClient:
    """
    LLM client supporting OpenAI and Google Gemini.

    Priority:
    1. OpenAI (if key exists + has credits)
    2. Gemini 2.5 Flash (FREE)
    """

    GEMINI_MODEL = "gemini-2.5-flash"

    def __init__(self):
        self.provider = None
        self.openai_client = None
        self.gemini_model = None

        self.session_stats = {
            "total_calls": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost_usd": 0.0,
            "calls_detail": [],
            "provider": "none",
        }

        # ── Try OpenAI first ───────────────────────────
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if OPENAI_AVAILABLE and openai_key:
            try:
                self.openai_client = OpenAI(api_key=openai_key)
                self.provider = "openai"
                self.session_stats["provider"] = "openai"
                logger.info("✅ LLM Provider: OpenAI")
            except Exception as e:
                logger.warning(f"OpenAI init failed: {e}")

        # ── Try Gemini as fallback ─────────────────────
        google_key = os.getenv("GOOGLE_API_KEY", "")
        if self.provider is None and GEMINI_AVAILABLE and google_key:
            try:
                genai.configure(api_key=google_key)
                self.gemini_model = genai.GenerativeModel(self.GEMINI_MODEL)
                self.provider = "gemini"
                self.session_stats["provider"] = f"gemini ({self.GEMINI_MODEL}) FREE"
                logger.info(f"✅ LLM Provider: Gemini ({self.GEMINI_MODEL}) FREE")
            except Exception as e:
                logger.warning(f"Gemini init failed: {e}")

        # Also keep Gemini ready as fallback even if OpenAI is primary
        if self.provider == "openai" and GEMINI_AVAILABLE and google_key:
            try:
                genai.configure(api_key=google_key)
                self.gemini_model = genai.GenerativeModel(self.GEMINI_MODEL)
                logger.info("Gemini ready as fallback")
            except Exception:
                pass

        if self.provider is None:
            logger.warning(
                "No LLM provider available. "
                "Set OPENAI_API_KEY or GOOGLE_API_KEY"
            )

        # Token counter
        self._encoder = None
        if TIKTOKEN_AVAILABLE:
            try:
                self._encoder = tiktoken.encoding_for_model("gpt-4o-mini")
            except Exception:
                try:
                    self._encoder = tiktoken.get_encoding("cl100k_base")
                except Exception:
                    pass


    def generate(self,
                 prompt: str,
                 system_prompt: Optional[str] = None,
                 temperature: Optional[float] = None,
                 max_tokens: Optional[int] = None,
                 model: Optional[str] = None,
                 json_mode: bool = False) -> str:
        """Generate text from best available provider."""

        if self.provider == "openai":
            try:
                return self._generate_openai(
                    prompt, system_prompt, temperature,
                    max_tokens, model, json_mode
                )
            except Exception as e:
                error_msg = str(e).lower()
                # If OpenAI fails (quota/billing), try Gemini
                if any(word in error_msg for word in
                       ["quota", "exceeded", "billing", "insufficient"]):
                    logger.warning("OpenAI quota exceeded — switching to Gemini")
                    if self.gemini_model:
                        self.provider = "gemini"
                        self.session_stats["provider"] = f"gemini ({self.GEMINI_MODEL}) FREE"
                        return self._generate_gemini(
                            prompt, system_prompt, temperature,
                            max_tokens, json_mode
                        )
                raise

        elif self.provider == "gemini":
            return self._generate_gemini(
                prompt, system_prompt, temperature,
                max_tokens, json_mode
            )

        else:
            raise Exception(
                "No LLM provider configured. "
                "Add OPENAI_API_KEY or GOOGLE_API_KEY to .env or Streamlit secrets."
            )


    def generate_structured(self,
                            prompt: str,
                            system_prompt: Optional[str] = None,
                            model: Optional[str] = None) -> Dict:
        """Generate JSON output."""

        raw = self.generate(
            prompt=prompt, system_prompt=system_prompt,
            json_mode=True, model=model,
        )

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return self._extract_json(raw)


    # ═══════════════════════════════════════════════════════
    # OPENAI
    # ═══════════════════════════════════════════════════════

    def _generate_openai(self, prompt, system_prompt,
                          temperature, max_tokens,
                          model, json_mode):
        """Generate using OpenAI."""

        model = model or config.MODEL_NAME
        temperature = temperature if temperature is not None else config.TEMPERATURE
        max_tokens = max_tokens or config.MAX_TOKENS

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        last_error = None
        for attempt in range(config.MAX_RETRIES):
            try:
                logger.info(
                    f"OpenAI call #{self.session_stats['total_calls'] + 1} "
                    f"(model={model}, attempt={attempt + 1})"
                )

                response = self.openai_client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                in_tokens = response.usage.prompt_tokens
                out_tokens = response.usage.completion_tokens

                cost = self._calculate_cost(in_tokens, out_tokens, model)
                self._track_call(model, in_tokens, out_tokens, cost)

                logger.info(f"✅ OpenAI: {out_tokens} tokens, ${cost:.4f}")
                return content

            except RateLimitError as e:
                last_error = e
                error_msg = str(e).lower()

                if "insufficient_quota" in error_msg or "exceeded" in error_msg:
                    raise  # Let main generate() handle fallback

                wait = config.RETRY_DELAY * (2 ** attempt)
                logger.warning(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)

            except (APIConnectionError, APIError) as e:
                last_error = e
                wait = config.RETRY_DELAY * (2 ** attempt)
                time.sleep(wait)

            except Exception as e:
                last_error = e
                break

        raise Exception(f"OpenAI failed: {last_error}")


    # ═══════════════════════════════════════════════════════
    # GEMINI (FREE)
    # ═══════════════════════════════════════════════════════

    def _generate_gemini(self, prompt, system_prompt,
                          temperature, max_tokens, json_mode):
        """Generate using Google Gemini (FREE)."""

        temperature = temperature if temperature is not None else config.TEMPERATURE
        max_tokens = max_tokens or config.MAX_TOKENS

        # Combine system + user prompt
        full_prompt = ""
        if system_prompt:
            full_prompt = f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
        full_prompt += f"USER REQUEST:\n{prompt}"

        if json_mode:
            full_prompt += "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no extra text."

        in_tokens = len(full_prompt) // 4

        last_error = None
        for attempt in range(config.MAX_RETRIES):
            try:
                logger.info(
                    f"Gemini call #{self.session_stats['total_calls'] + 1} "
                    f"(attempt={attempt + 1})"
                )

                gen_config = genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )

                response = self.gemini_model.generate_content(
                    full_prompt,
                    generation_config=gen_config,
                )

                content = response.text
                out_tokens = len(content) // 4

                self._track_call(
                    self.GEMINI_MODEL, in_tokens, out_tokens, 0.0
                )

                logger.info(f"✅ Gemini: ~{out_tokens} tokens (FREE)")
                return content

            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                logger.warning(f"Gemini attempt {attempt + 1}: {e}")

                if "429" in error_msg or "quota" in error_msg:
                    wait = 30 * (attempt + 1)
                    logger.info(f"Rate limited. Waiting {wait}s...")
                    time.sleep(wait)
                else:
                    time.sleep(config.RETRY_DELAY * (2 ** attempt))

        raise Exception(f"Gemini failed: {last_error}")


    # ═══════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════

    def _calculate_cost(self, in_tokens, out_tokens, model):
        """Calculate cost (OpenAI only — Gemini is free)."""

        if "gemini" in model.lower():
            return 0.0

        if model == config.MODEL_NAME_ADVANCED:
            return round(
                (in_tokens / 1e6) * config.COST_PER_1M_INPUT_ADVANCED +
                (out_tokens / 1e6) * config.COST_PER_1M_OUTPUT_ADVANCED, 6
            )
        return round(
            (in_tokens / 1e6) * config.COST_PER_1M_INPUT_TOKENS +
            (out_tokens / 1e6) * config.COST_PER_1M_OUTPUT_TOKENS, 6
        )


    def _track_call(self, model, in_tokens, out_tokens, cost):
        """Track API call stats."""

        self.session_stats["total_calls"] += 1
        self.session_stats["total_input_tokens"] += in_tokens
        self.session_stats["total_output_tokens"] += out_tokens
        self.session_stats["total_cost_usd"] += cost
        self.session_stats["calls_detail"].append({
            "model": model,
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
            "cost": cost,
        })


    def _extract_json(self, text):
        """Extract JSON from text."""

        import re
        for pattern in [r'```json\s*(.*?)\s*```', r'\{.*\}']:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    content = match.group(1) if '```' in pattern else match.group()
                    return json.loads(content)
                except json.JSONDecodeError:
                    continue
        return {"raw_text": text, "parse_error": True}


    def get_session_stats(self) -> Dict:
        """Get session statistics."""
        return {
            **self.session_stats,
            "total_cost_formatted": (
                f"${self.session_stats['total_cost_usd']:.4f}"
                if self.session_stats['total_cost_usd'] > 0
                else "FREE (Gemini)"
            ),
        }


    def is_available(self) -> bool:
        """Check if any provider is configured."""
        return self.provider is not None


# Singleton
llm = LLMClient()
