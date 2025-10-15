# fairsea/evaluationTest.py

def analyze_sentiment(text: str) -> str:
    """
    Analyzes the sentiment of a given text based on simple keywords.

    This is a basic example function to be tested by our CI pipeline.

    Args:
        text: The input string to analyze.

    Returns:
        A string indicating the sentiment ("Positive", "Negative", or "Neutral").
    """
    text_lower = text.lower()
    positive_keywords = ["excellent", "good", "great", "success"]
    negative_keywords = ["poor", "bad", "failure", "problem"]

    for word in positive_keywords:
        if word in text_lower:
            return "Positive"

    for word in negative_keywords:
        if word in text_lower:
            return "Negative"

    return "Neutral"