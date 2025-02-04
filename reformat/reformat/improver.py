import random
import logging
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import aisuite as ai
from dotenv import load_dotenv

from .rules import (
    SeparatorRule,
    CasingRule,
    ItemFormattingRule,
    EnumerationRule,
)
from .reformatter import PromptReformatter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv()


@dataclass
class FormatResult:
    format: "FormatCandidate"
    formatted_prompt: str
    model_response: str
    score: float


@dataclass
class FormatCandidate:
    separator_rule: SeparatorRule
    casing_rule: CasingRule
    item_formatting_rule: ItemFormattingRule
    enumeration_rule: EnumerationRule
    score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "separator_rule": self.separator_rule.name,
            "casing_rule": self.casing_rule.name,
            "item_formatting_rule": self.item_formatting_rule.name,
            "enumeration_rule": self.enumeration_rule.name,
            "score": self.score,
        }


class PromptImprover:
    def __init__(
        self, model: str = "llama-3.3-70b-versatile", api_key: Optional[str] = None
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided or set as GROQ_API_KEY environment variable"
            )

        self.client = ai.Client({"groq": {"api_key": self.api_key}})
        self.target_model = f"groq:{model}"
        self.judge_model = "groq:llama-3.3-70b-versatile"

    def get_model_response(self, formatted_prompt: str) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": formatted_prompt},
        ]

        response = self.client.chat.completions.create(
            model=self.target_model, messages=messages, temperature=0.0
        )
        return response.choices[0].message.content.strip()

    def evaluate_format(
        self,
        prompt: str,
        original_response: str,
        formatted_response: str,
    ) -> float:
        evaluation_prompt = f"""Compare and evaluate these two responses to determine if the second response is better than the first.

Prompt:
{prompt}

Response 1:
{original_response}

Response 2:
{formatted_response}

Consider the following criteria:
1. Accuracy and correctness of information
2. Completeness of the answer
3. Relevance to the query
4. Clarity and coherence of the response

Rate how much better Response 2 is compared to Response 1 on a scale from 0 to 1, where:
0 = Response 2 is worse or equal to Response 1
1 = Response 2 is significantly better than Response 1

Provide only the numerical score (e.g., 0.85) without any explanation."""

        messages = [
            {
                "role": "system",
                "content": "You are an expert evaluating response quality.",
            },
            {"role": "user", "content": evaluation_prompt},
        ]

        response = self.client.chat.completions.create(
            model=self.judge_model, messages=messages, temperature=0.0
        )

        try:
            score = float(response.choices[0].message.content.strip())
            return max(0.0, min(1.0, score))
        except ValueError:
            logger.error("Judge provided invalid score format")
            return 0.0

    def sample_candidate(self) -> FormatCandidate:
        return FormatCandidate(
            separator_rule=random.choice(SeparatorRule.get_default_rules()),
            casing_rule=random.choice(CasingRule.get_default_rules()),
            item_formatting_rule=random.choice(ItemFormattingRule.get_default_rules()),
            enumeration_rule=random.choice(EnumerationRule.get_default_rules()),
        )

    def format_prompt(
        self, field_values: Dict[str, Any], candidate: FormatCandidate
    ) -> str:
        reformatter = PromptReformatter(
            separator_rules=[candidate.separator_rule],
            casing_rules=[candidate.casing_rule],
            item_formatting_rules=[candidate.item_formatting_rule],
            enumeration_rules=[candidate.enumeration_rule],
        )
        _, formatted_prompt, _ = reformatter.format(field_values)
        return formatted_prompt

    def improve(
        self,
        field_values: Dict[str, Any],
        num_candidates: int = 10,
        num_iterations: int = 3,
    ) -> Dict[str, Any]:
        reformatter = PromptReformatter()
        if "Question" in field_values and "Options" in field_values:
            reformatter.set_template("multiple_choice")
            if "Input" not in field_values:
                field_values["Input"] = ""
        else:
            reformatter.set_template("general")

        original_prompt, _, _ = reformatter.format(field_values)
        original_response = self.get_model_response(original_prompt)

        best_candidate: Optional[FormatCandidate] = None
        best_score = float("-inf")
        best_response = original_response
        all_candidates: List[FormatCandidate] = []

        for iteration in range(num_iterations):
            logger.info(f"Starting iteration {iteration + 1}/{num_iterations}")

            for _ in range(num_candidates):
                candidate = self.sample_candidate()
                formatted_prompt = self.format_prompt(field_values, candidate)
                model_response = self.get_model_response(formatted_prompt)
                score = self.evaluate_format(
                    original_prompt, original_response, model_response
                )
                candidate.score = score
                all_candidates.append(candidate)

                if score > best_score:
                    best_score = score
                    best_candidate = candidate
                    best_response = model_response
                    logger.info(f"New best score: {best_score:.3f}")

        best_formatted_prompt = (
            self.format_prompt(field_values, best_candidate)
            if best_candidate
            else original_prompt
        )

        return {
            "original_prompt": original_prompt,
            "improved_prompt": best_formatted_prompt,
            "original_response": original_response,
            "improved_response": best_response,
            "improvement_score": best_score,
            "best_format": best_candidate.to_dict() if best_candidate else None,
            "num_candidates_evaluated": len(all_candidates),
            "all_scores": [c.score for c in all_candidates],
        }
