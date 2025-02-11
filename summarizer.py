import openai
import logging
from typing import Optional
from config import OPENAI_API_KEY, SUMMARY_SYSTEM_PROMPT

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

async def generate_personalized_summary(
    report_text: str,
    user_description: str,
    industry: str
) -> Optional[str]:
    """
    Generate a personalized summary of a report based on user's business profile.

    Args:
        report_text: The text content of the report
        user_description: Description of user's business/product
        industry: User's industry category

    Returns:
        str: Personalized summary or None if generation fails
    """
    try:
        response = await openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                {"role": "user", "content": f"""
                Industry: {industry}
                Business Description: {user_description}

                Report Content:
                {report_text}

                Create a concise, personalized summary focusing on aspects relevant 
                to this specific business and industry. Include actionable insights.
                """}
            ],
            max_tokens=500,
            temperature=0.7
        )

        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error generating summary: {e}")
        return None