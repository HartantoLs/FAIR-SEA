# tests/test_evaluation.py
import pytest
from fairsea.evaluationTest import analyze_sentiment

def test_positive_sentiment():
    """Tests if the function correctly identifies positive sentiment."""
    text = "The candidate's performance was excellent."
    result = analyze_sentiment(text)
    assert result == "Positive"

def test_negative_sentiment():
    """Tests if the function correctly identifies negative sentiment."""
    text = "There was a problem with the data."
    result = analyze_sentiment(text)
    assert result == "Negative"

def test_neutral_sentiment():
    """Tests if the function returns neutral for text with no keywords."""
    text = "The report was submitted on Tuesday."
    result = analyze_sentiment(text)
    assert result == "Neutral"