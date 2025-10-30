import re
import numpy as np
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from bias_metrics import *

# ensure vader lexicon is available (harmless if already present)
nltk.download('vader_lexicon', quiet=True)
analyzer = SentimentIntensityAnalyzer()

def process_i3(df):
    """Process prompt group I3.
    - Extract binary decision (Yes/No) from the start of `llm_output` and run categorical analyses.
    - Compute sentiment on the remaining justification text for exploratory continuous analyses.
    """
    i3 = df[df['prompt_id_full'].astype(str).str.startswith('I3')].copy()
    i3 = i3.reset_index(drop=True)

    # Decision extraction (permissive): pick the first standalone 'yes' or 'no' anywhere in the text
    # This is robust to forms like 'Decision: Yes', 'Yes — because...', or 'I think no.'
    i3['decision'] = i3['llm_output'].str.extract(r'(?i)\b(yes|no)\b', expand=False)
    i3['decision'] = i3['decision'].str.capitalize().fillna('Unknown')

    # Justification: remove only the first matched 'yes'/'no' so sentiment is computed on the rest
    def _remove_first_yesno(s):
        return re.sub(r'(?i)\b(yes|no)\b', '', str(s), count=1).strip()

    i3['justification'] = i3['llm_output'].apply(_remove_first_yesno)

    # Sentiment score (compound) for justification
    i3['sentiment_score'] = i3['justification'].apply(lambda x: analyzer.polarity_scores(str(x))['compound'])

    # Primary dashboard focus: decision (categorical)
    demo_results = run_demographic_analysis_categorical(i3, output_col='decision')
    inter_results = run_intersectional_analysis_categorical(i3, output_col='decision', plot=True)

    # We also return sentiment stats (not used as primary outcome here)
    sentiment_summary = i3.groupby(['Gender','Race'])['sentiment_score'].mean().reset_index()

    return {
        'is_continuous': False,
        'demographic': demo_results,
        'intersectional': inter_results,
        'sentiment_summary': sentiment_summary
    }

def sample(df):
    i3 = df[df['prompt_id_full'].astype(str).str.startswith('I3')].copy()
    i3 = i3.reset_index(drop=True)
    return i3.sample(n=min(5, len(i3)), random_state=42)[['prompt_text','llm_output']]
