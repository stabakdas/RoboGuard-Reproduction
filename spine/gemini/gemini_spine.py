import logging
import os
import traceback
from types import SimpleNamespace
from typing import Dict, List, Tuple

from google import genai
from google.genai import types

from spine.llm_logging import get_logger
from spine.spine import SPINE


class GeminiSPINE(SPINE):
    """
    Gemini-backed SPINE planner.

    The original SPINE planning, parsing, validation, retry,
    and feedback logic is inherited unchanged.

    Only the LLM backend is replaced with Gemini.
    """

    def __init__(
        self,
        graph,
        model: str = "gemini-2.5-pro",
    ) -> None:
        # Initialize the same SPINE state as SPINE.__init__(),
        # but do not initialize the OpenAI client.
        self.graph = graph

        self.model = model
        self.n_attempts = 3
        self.base_request = ""

        self.msg_history = []

        self.logger = get_logger(
            name="LLMPlanner",
            level=logging.INFO,
            stdout=False,
        )

        self.logger.disabled = True

        self.most_recent_query = []

        # Initialize Gemini instead of OpenAI.
        if not os.getenv("GEMINI_API_KEY"):
            raise RuntimeError(
                "GEMINI_API_KEY is not set."
            )

        self.client = genai.Client(
            api_key=os.environ["GEMINI_API_KEY"]
        )

    def query_llm(
        self,
        msg: List[Dict[str, str]],
    ) -> Tuple[SimpleNamespace, bool]:
        """
        Gemini replacement for SPINE.query_llm().

        The original SPINE _generate_plan() method remains
        unchanged and continues to handle:

        - JSON parsing
        - plan validation
        - retry attempts
        - feedback
        - plan extraction
        """

        self.most_recent_query = msg

        try:
            system_instruction = ""
            conversation = []

            # --------------------------------------------------
            # Convert SPINE's OpenAI-style messages to Gemini.
            # --------------------------------------------------
            for message in msg:
                role = message.get("role", "user")
                content = message.get("content", "")

                if role == "system":
                    system_instruction = content
                else:
                    conversation.append(
                        f"{role.upper()}:\n{content}"
                    )

            prompt = "\n\n".join(conversation)

            # --------------------------------------------------
            # DEBUG: Check prompt encoding.
            # --------------------------------------------------
            print("\n--- DEBUG PROMPT ENCODING ---")

            try:
                prompt.encode("ascii")
                print("Prompt ASCII: OK")
            except UnicodeEncodeError as exc:
                bad_char = prompt[exc.start:exc.end]

                print(
                    "Prompt contains non-ASCII characters."
                )
                print(
                    f"Character: {repr(bad_char)}"
                )
                print(
                    f"Code point: U+{ord(bad_char):04X}"
                )
                print(
                    f"Position: {exc.start}"
                )

            # --------------------------------------------------
            # DEBUG: Check system instruction encoding.
            # --------------------------------------------------
            try:
                system_instruction.encode("ascii")
                print(
                    "System instruction ASCII: OK"
                )
            except UnicodeEncodeError as exc:
                bad_char = system_instruction[
                    exc.start:exc.end
                ]

                print(
                    "System instruction contains "
                    "non-ASCII characters."
                )
                print(
                    f"Character: {repr(bad_char)}"
                )
                print(
                    f"Code point: U+{ord(bad_char):04X}"
                )
                print(
                    f"Position: {exc.start}"
                )

            # --------------------------------------------------
            # Call Gemini.
            # --------------------------------------------------
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.05,
                    response_mime_type="application/json",
                ),
            )

            # --------------------------------------------------
            # Make Gemini response compatible with SPINE.
            #
            # Original SPINE expects:
            #
            #     top_msg.content
            # --------------------------------------------------
            top_msg = SimpleNamespace(
                content=response.text
            )

            return top_msg, True

        except Exception as ex:
            print(
                f"\nGemini query failed: "
                f"{type(ex).__name__}: {ex}"
            )

            print("\n--- FULL TRACEBACK ---")
            traceback.print_exc()

            return (
                SimpleNamespace(
                    content="Error: Gemini API failure"
                ),
                False,
            )

