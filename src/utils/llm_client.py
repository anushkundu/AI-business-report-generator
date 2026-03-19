# src/utils/llm_client.py

"""
LLM CLIENT — Supports OpenAI + Google Gemini (FREE)
"""

import json
import time
from typing import Optional, Dict
from src.utils.config import config
from src.utils.logger import logger

# Try importing both providers
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
    LLM client supporting OpenAI and Google Gemini (free).

    Priority:
    1. If OPENAI_API_KEY exists and has credits → use OpenAI
    2. If GOOGLE_API_KEY exists → use Gemini (FREE)
    3. If neither → LLM features disabled
    """

    def __init__(self):
        self.provider = None
        self.openai_client = None
        self.gemini_model = None

        # Session tracking
        self.session_stats = {
            "total_calls": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost_usd": 0.0,
            "calls_detail": [],
            "provider": "none",
        }

        # Try OpenAI first
        if OPENAI_AVAILABLE and config.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
                self.provider = "openai"
                self.session_stats["provider"] = "openai"
                logger.info("LLM Provider: OpenAI")
            except Exception as e:
                logger.warning(f"OpenAI init failed: {e}")

        # Try Gemini as fallback
        if self.provider is None and GEMINI_AVAILABLE:
            import os
            google_key = os.getenv("GOOGLE_API_KEY", "")
            if google_key:
                try:
                    genai.configure(api_key=google_key)
                    self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                    self.provider = "gemini"
                    self.session_stats["provider"] = "gemini (free)"
                    logger.info("LLM Provider: Google Gemini (FREE)")
                except Exception as e:
                    logger.warning(f"Gemini init failed: {e}")

        if self.provider is None:
            logger.warning(
                "No LLM provider available. "
                "Set OPENAI_API_KEY or GOOGLE_API_KEY in .env"
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
        """Generate text from LLM (OpenAI or Gemini)."""

        if self.provider == "openai":
            return self._generate_openai(
                prompt, system_prompt, temperature,
                max_tokens, model, json_mode
            )
        elif self.provider == "gemini":
            return self._generate_gemini(
                prompt, system_prompt, temperature,
                max_tokens, json_mode
            )
        else:
            raise Exception(
                "No LLM provider configured. "
                "Add OPENAI_API_KEY or GOOGLE_API_KEY to .env"
            )


    def generate_structured(self,
                            prompt: str,
                            system_prompt: Optional[str] = None,
                            model: Optional[str] = None) -> Dict:
        """Generate structured JSON output."""

        raw = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            json_mode=True,
            model=model,
        )

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return self._extract_json(raw)


    # ═══════════════════════════════════════════════════════
    # OPENAI PROVIDER
    # ═══════════════════════════════════════════════════════

    def _generate_openai(self, prompt, system_prompt,
                          temperature, max_tokens,
                          model, json_mode):
        """Generate using OpenAI API."""

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
                output_tokens = response.usage.completion_tokens
                input_tokens = response.usage.prompt_tokens

                cost = self._calculate_cost(input_tokens, output_tokens, model)
                self._track_call(model, input_tokens, output_tokens, cost)

                return content

            except RateLimitError as e:
                last_error = e

                # Check if it's a quota error (no money)
                error_msg = str(e).lower()
                if "insufficient_quota" in error_msg or "exceeded" in error_msg:
                    logger.warning("OpenAI quota exceeded — switching to Gemini if available")

                    # Try Gemini fallback
                    if GEMINI_AVAILABLE:
                        import os
                        google_key = os.getenv("GOOGLE_API_KEY", "")
                        if google_key:
                            genai.configure(api_key=google_key)
                            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                            self.provider = "gemini"
                            self.session_stats["provider"] = "gemini (fallback)"
                            logger.info("Switched to Gemini (free)")
                            return self._generate_gemini(
                                prompt, system_prompt,
                                temperature, max_tokens, False
                            )

                    raise Exception(
                        "OpenAI quota exceeded and no Gemini key available. "
                        "Either add credits at platform.openai.com/settings/organization/billing "
                        "or add GOOGLE_API_KEY to .env for free Gemini access."
                    )

                # Regular rate limit — retry
                wait_time = config.RETRY_DELAY * (2 ** attempt)
                logger.warning(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)

            except APIConnectionError as e:
                last_error = e
                wait_time = config.RETRY_DELAY * (2 ** attempt)
                logger.warning(f"Connection error. Waiting {wait_time}s...")
                time.sleep(wait_time)

            except APIError as e:
                last_error = e
                logger.error(f"API error: {e}")
                if model == config.MODEL_NAME_ADVANCED:
                    kwargs["model"] = config.MODEL_NAME
                    model = config.MODEL_NAME
                else:
                    time.sleep(config.RETRY_DELAY * (2 ** attempt))

            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error: {e}")
                break

        raise Exception(
            f"LLM generation failed after {config.MAX_RETRIES} attempts: {last_error}"
        )


    # ═══════════════════════════════════════════════════════
    # GEMINI PROVIDER (FREE)
    # ═══════════════════════════════════════════════════════

    def _generate_gemini(self, prompt, system_prompt,
                          temperature, max_tokens, json_mode):
        """Generate using Google Gemini API (FREE)."""

        temperature = temperature if temperature is not None else config.TEMPERATURE
        max_tokens = max_tokens or config.MAX_TOKENS

        # Combine system prompt and user prompt
        full_prompt = ""
        if system_prompt:
            full_prompt = f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
        full_prompt += f"USER REQUEST:\n{prompt}"

        if json_mode:
            full_prompt += "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanation."

        # Estimate input tokens
        input_tokens = len(full_prompt) // 4

        last_error = None
        for attempt in range(config.MAX_RETRIES):
            try:
                logger.info(
                    f"Gemini call #{self.session_stats['total_calls'] + 1} "
                    f"(attempt={attempt + 1})"
                )

                generation_config = genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )

                response = self.gemini_model.generate_content(
                    full_prompt,
                    generation_config=generation_config,
                )

                content = response.text

                # Estimate output tokens
                output_tokens = len(content) // 4

                # Gemini is FREE — cost = $0
                self._track_call(
                    "gemini-2.5-flash", input_tokens, output_tokens, 0.0
                )

                logger.info(f"Gemini response: ~{output_tokens} tokens (FREE)")

                return content

            except Exception as e:
                last_error = e
                logger.warning(f"Gemini error (attempt {attempt + 1}): {e}")
                time.sleep(config.RETRY_DELAY * (2 ** attempt))

        raise Exception(
            f"Gemini generation failed after {config.MAX_RETRIES} attempts: {last_error}"
        )


    # ═══════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════

    def _calculate_cost(self, input_tokens, output_tokens, model):
        """Calculate cost (only for OpenAI — Gemini is free)."""

        if "gemini" in model.lower():
            return 0.0

        if model == config.MODEL_NAME_ADVANCED:
            input_cost = (input_tokens / 1_000_000) * config.COST_PER_1M_INPUT_ADVANCED
            output_cost = (output_tokens / 1_000_000) * config.COST_PER_1M_OUTPUT_ADVANCED
        else:
            input_cost = (input_tokens / 1_000_000) * config.COST_PER_1M_INPUT_TOKENS
            output_cost = (output_tokens / 1_000_000) * config.COST_PER_1M_OUTPUT_TOKENS

        return round(input_cost + output_cost, 6)


    def _track_call(self, model, input_tokens, output_tokens, cost):
        """Track API call stats."""

        self.session_stats["total_calls"] += 1
        self.session_stats["total_input_tokens"] += input_tokens
        self.session_stats["total_output_tokens"] += output_tokens
        self.session_stats["total_cost_usd"] += cost
        self.session_stats["calls_detail"].append({
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
        })


    def _extract_json(self, text):
        """Try to extract JSON from text."""

        import re

        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        brace_match = re.search(r'\{.*\}', text, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group())
            except json.JSONDecodeError:
                pass

        return {"raw_text": text, "parse_error": True}


    def get_session_stats(self) -> Dict:
        """Get session statistics."""
        return {
            **self.session_stats,
            "total_cost_formatted": (
                f"${self.session_stats['total_cost_usd']:.4f}"
                if self.session_stats['total_cost_usd'] > 0
                else "FREE"
            ),
        }


    def is_available(self) -> bool:
        """Check if any LLM provider is configured."""
        return self.provider is not None


# Create singleton
llm = LLMClient()