# d2_processing.py
import numpy as np
import pandas as pd
from bias_metrics import *
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')
analyzer = SentimentIntensityAnalyzer()
    
def get_sentiment_score(text):
    score = analyzer.polarity_scores(str(text))
    # Return compound score (-1 very negative → +1 very positive)
    return score['compound']
    
def process_d2(df):
    # Filter
    d2 = df[df['prompt_id_full'].str.startswith('D2')].copy()
    d2 = d2.reset_index(drop=True)

    d2['sentiment_score'] = d2['llm_output'].apply(get_sentiment_score)

    # 5️⃣ Run analyses
    demo_results = run_demographic_analysis_continuous(d2, score_col="sentiment_score")
    inter_results = run_intersectional_analysis_continuous(d2, score_col="sentiment_score")

    return {"is_continuous": True,  # continuous
            "demographic": demo_results, 
            "intersectional": inter_results}

def sample(df):
    d2 = df[df['prompt_id_full'].str.startswith('D2')].copy()
    d2 = d2.reset_index(drop=True)
    return d2.sample(n=min(5, len(d2)), random_state=42)[["prompt_text", "llm_output"]]