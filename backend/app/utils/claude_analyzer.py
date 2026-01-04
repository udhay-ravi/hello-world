import os
from anthropic import Anthropic
from typing import Dict, List, Optional
import json

class ClaudeAnalyzer:
    """Use Claude API for intelligent text analysis"""

    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-5-sonnet-20241022"

    def analyze_customer_feedback(self, text: str, source: str) -> Dict:
        """
        Analyze customer feedback to extract structured information
        Returns: {
            'problem_summary': str,
            'problem_description': str,
            'product': str,
            'severity_score': float,
            'is_valid_issue': bool
        }
        """

        prompt = f"""Analyze this customer feedback about DigitalOcean networking products.

Source: {source}
Feedback: {text}

Extract the following information:
1. problem_summary: A concise 1-sentence summary of the main problem (max 100 chars)
2. problem_description: A detailed description of the issue (2-3 sentences)
3. product: Which product is mentioned? Choose from: VPC, Load Balancer, NAT Gateway, Floating IP, Firewall, Networking (general)
4. severity_score: Rate severity from 1-10 based on:
   - Language intensity (urgent, critical, broken = higher score)
   - Impact described (data loss, downtime = higher score)
   - Frequency mentions (always, constantly = higher score)
5. is_valid_issue: Is this a real technical issue/complaint? (not praise, not question)

Respond ONLY with valid JSON in this exact format:
{{
    "problem_summary": "brief summary here",
    "problem_description": "detailed description here",
    "product": "Product Name",
    "severity_score": 7.5,
    "is_valid_issue": true
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text

            # Extract JSON from response
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                result = json.loads(result_text[json_start:json_end])
                return result
            else:
                return self._get_fallback_analysis(text)

        except Exception as e:
            print(f"Claude API error: {e}")
            return self._get_fallback_analysis(text)

    def categorize_similar_problems(self, problems: List[str]) -> Dict[str, List[int]]:
        """
        Group similar problems together using semantic similarity
        Returns: {category_name: [problem_indices]}
        """

        if len(problems) <= 1:
            return {"general": list(range(len(problems)))}

        prompt = f"""Group these customer problems into similar categories.

Problems:
{chr(10).join([f"{i+1}. {p}" for i, p in enumerate(problems)])}

Respond with JSON grouping similar problems:
{{
    "category_name_1": [1, 3, 5],
    "category_name_2": [2, 4],
    ...
}}

Make category names descriptive (e.g., "VPC Peering Issues", "Load Balancer Timeout Problems")."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            result_text = response.content[0].text
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                result = json.loads(result_text[json_start:json_end])
                return result
            else:
                return {"general": list(range(len(problems)))}

        except Exception as e:
            print(f"Claude API error in categorization: {e}")
            return {"general": list(range(len(problems)))}

    def _get_fallback_analysis(self, text: str) -> Dict:
        """Fallback analysis when Claude API fails"""
        from .text_processing import detect_product, get_sentiment_score

        return {
            "problem_summary": text[:100] if len(text) > 100 else text,
            "problem_description": text[:300] if len(text) > 300 else text,
            "product": detect_product(text),
            "severity_score": 5.0,
            "is_valid_issue": True
        }
