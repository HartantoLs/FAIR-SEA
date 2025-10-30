# d3_processing.py
import numpy as np
import pandas as pd
from bias_metrics import *

def process_d3(df):
    # Filter
    d3 = df[df['prompt_id_full'].str.startswith('D3')].copy()
    d3 = d3.reset_index(drop=True)

    # 5️⃣ Run analyses
    demo_results = run_demographic_analysis_categorical(d3, output_col="llm_output")
    inter_results = run_intersectional_analysis_categorical(d3, output_col="llm_output", plot=True)

    return {"is_continuous": False,  # categorical,
            "demographic": demo_results, 
            "intersectional": inter_results}

def sample(df):
    d3 = df[df['prompt_id_full'].str.startswith('D3')].copy()
    d3 = d3.reset_index(drop=True)
    return d3.sample(n=min(5, len(d3)), random_state=42)[["prompt_text", "llm_output"]]