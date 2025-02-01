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
        """Get response from the target model."""
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

    def format_prompt(self, prompt: str, candidate: FormatCandidate) -> str:
        reformatter = PromptReformatter(
            separator_rules=[candidate.separator_rule],
            casing_rules=[candidate.casing_rule],
            item_formatting_rules=[candidate.item_formatting_rule],
            enumeration_rules=[candidate.enumeration_rule],
        )
        return reformatter.format(prompt)

    # use random search to improve prompt format
    def improve(
        self,
        prompt: str,
        num_candidates: int = 10,
        num_iterations: int = 3,
        temperature: float = 0.1,
    ) -> Dict[str, Any]:
        original_response = self.get_model_response(prompt)

        best_result: Optional[FormatResult] = None
        best_score = float("-inf")
        all_results: List[FormatResult] = []

        for iteration in range(num_iterations):
            logger.info(f"Starting iteration {iteration + 1}/{num_iterations}")

            for _ in range(num_candidates):
                candidate = self.sample_candidate()

                # format the prompt
                formatted_prompt = self.format_prompt(prompt, candidate)

                # get model response
                model_response = self.get_model_response(formatted_prompt)

                # evaluate the response quality
                score = self.evaluate_format(prompt, original_response, model_response)
                candidate.score = score

                # create result object
                result = FormatResult(
                    format=candidate,
                    formatted_prompt=formatted_prompt,
                    model_response=model_response,
                    score=score,
                )
                all_results.append(result)

                if score > best_score:
                    best_score = score
                    best_result = result
                    logger.info(f"New best score: {best_score:.3f}")

        return {
            "original_prompt": prompt,
            "original_response": original_response,
            "improved_prompt": best_result.formatted_prompt,
            "improved_response": best_result.model_response,
            "improvement_score": best_score,
            "best_format": best_result.format.to_dict(),
            "num_candidates_evaluated": len(all_results),
            "all_scores": [r.score for r in all_results],
        }
