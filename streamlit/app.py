import streamlit as st
import pandas as pd
from bias_metrics import *
import os
import importlib

# Page configuration
st.set_page_config(
    page_title="FAIR-SEA | Bias Analysis Dashboard",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Main background with darker navy blue gradient */
    .stApp {
        background: linear-gradient(135deg, #020617 0%, #0a0e27 20%, #0f172a 40%, #1e1b4b 60%, #0f172a 80%, #020617 100%);
        background-attachment: fixed;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #e2e8f0;
    }
    
    /* Hero Get Started Section */
    .hero-cta {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(37, 99, 235, 0.15) 50%, rgba(29, 78, 216, 0.1) 100%);
        backdrop-filter: blur(32px);
        -webkit-backdrop-filter: blur(32px);
        border-radius: 24px;
        border: 2px solid rgba(59, 130, 246, 0.4);
        padding: 4rem 3rem;
        margin: 3rem 0;
        text-align: center;
        box-shadow: 0 20px 60px 0 rgba(59, 130, 246, 0.25), 0 0 100px 0 rgba(59, 130, 246, 0.1);
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .hero-cta:hover {
        transform: translateY(-4px);
        box-shadow: 0 24px 80px 0 rgba(59, 130, 246, 0.35), 0 0 120px 0 rgba(59, 130, 246, 0.15);
        border: 2px solid rgba(59, 130, 246, 0.6);
    }
    
    .hero-cta::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .hero-cta h2 {
        color: #f8fafc;
        font-size: 2.75rem;
        font-weight: 900;
        margin-bottom: 1.25rem;
        letter-spacing: -0.03em;
        text-shadow: 0 4px 24px rgba(59, 130, 246, 0.4);
        position: relative;
        z-index: 1;
    }
    
    .hero-cta p {
        color: #cbd5e1;
        font-size: 1.35rem;
        font-weight: 500;
        margin-bottom: 2.5rem;
        line-height: 1.6;
        position: relative;
        z-index: 1;
    }
    
    /* Glass morphism container */
    .glass-container {
        background: rgba(15, 23, 42, 0.5);
        backdrop-filter: blur(28px);
        -webkit-backdrop-filter: blur(28px);
        border-radius: 20px;
        border: 1px solid rgba(148, 163, 184, 0.12);
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .glass-container:hover {
        border: 1px solid rgba(148, 163, 184, 0.25);
        box-shadow: 0 16px 56px 0 rgba(0, 0, 0, 0.5);
        transform: translateY(-2px);
    }
    
    /* Header styling */
    .main-header {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(40px);
        -webkit-backdrop-filter: blur(40px);
        border-radius: 24px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        padding: 4rem 3rem;
        margin-bottom: 3rem;
        text-align: center;
        box-shadow: 0 16px 64px 0 rgba(0, 0, 0, 0.6);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.8), transparent);
    }
    
    .main-header h1 {
        color: #f8fafc;
        font-size: 4rem;
        font-weight: 900;
        margin-bottom: 1rem;
        letter-spacing: -0.03em;
        text-shadow: 0 4px 32px rgba(59, 130, 246, 0.4);
        background: linear-gradient(135deg, #f8fafc 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-header p {
        color: #cbd5e1;
        font-size: 1.4rem;
        font-weight: 500;
        letter-spacing: 0.02em;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.08) 100%);
        border-left: 5px solid #3b82f6;
        padding: 2rem 2.5rem;
        margin: 3rem 0 2rem 0;
        border-radius: 16px;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        box-shadow: 0 4px 24px 0 rgba(59, 130, 246, 0.1);
    }
    
    .section-header h2 {
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .section-header p {
        color: #94a3b8;
        font-size: 1.05rem;
        margin: 0.75rem 0 0 0;
        font-weight: 500;
    }
    
    /* Info cards */
    .info-card {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border-radius: 20px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        padding: 2.5rem;
        margin: 1rem 0;
        margin-top: 5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .info-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.6), transparent);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .info-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 16px 48px 0 rgba(59, 130, 246, 0.2);
        border: 1px solid rgba(59, 130, 246, 0.35);
    }
    
    .info-card:hover::before {
        opacity: 1;
    }
    
    .info-card h3 {
        color: #f8fafc;
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 1.25rem;
        letter-spacing: -0.02em;
    }
    
    .info-card p {
        color: #cbd5e1;
        font-size: 1.05rem;
        line-height: 1.8;
        font-weight: 400;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(37, 99, 235, 0.06) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 16px;
        border: 1px solid rgba(59, 130, 246, 0.25);
        padding: 2rem;
        text-align: center;
        box-shadow: 0 6px 28px 0 rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border: 1px solid rgba(59, 130, 246, 0.5);
        box-shadow: 0 12px 40px 0 rgba(59, 130, 246, 0.25);
        transform: translateY(-2px);
    }
    
    .metric-card h3 {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .metric-card p {
        color: #f8fafc;
        font-size: 2.5rem;
        font-weight: 900;
        letter-spacing: -0.03em;
    }
    
    /* Data source selection - highlighted */
    .data-source-container {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.1) 100%);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border-radius: 20px;
        border: 2px solid rgba(59, 130, 246, 0.3);
        padding: 3rem;
        margin: 2rem 0;
        box-shadow: 0 12px 48px 0 rgba(59, 130, 246, 0.2);
    }
    
    /* Streamlit overrides */
    .stButton>button {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(37, 99, 235, 0.2) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        color: #f8fafc;
        border: 2px solid rgba(59, 130, 246, 0.4);
        border-radius: 12px;
        padding: 1rem 2.5rem;
        font-weight: 700;
        font-size: 1.05rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 24px 0 rgba(59, 130, 246, 0.2);
        letter-spacing: 0.02em;
        text-transform: uppercase;
        font-size: 0.95rem;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.35) 0%, rgba(37, 99, 235, 0.3) 100%);
        border: 2px solid rgba(59, 130, 246, 0.6);
        transform: translateY(-3px);
        box-shadow: 0 12px 36px 0 rgba(59, 130, 246, 0.4);
    }
    
    .stButton>button:active {
        transform: translateY(-1px);
    }
    
    /* Primary button (for main CTA) */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border: 2px solid rgba(59, 130, 246, 0.8);
        box-shadow: 0 8px 32px 0 rgba(59, 130, 246, 0.4);
    }
    
    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 12px 48px 0 rgba(59, 130, 246, 0.6);
    }
    
    .stSelectbox>div>div, .stRadio>div {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        color: #f8fafc;
        transition: all 0.3s ease;
    }
    
    .stSelectbox>div>div:hover {
        border: 1px solid rgba(59, 130, 246, 0.4);
    }
    
    .stRadio>div {
        padding: 1.5rem;
        background: rgba(15, 23, 42, 0.6);
    }
    
    .stRadio label {
        color: #e2e8f0 !important;
        font-weight: 600;
        font-size: 1.05rem;
    }
    
    .stDataFrame {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(148, 163, 184, 0.15);
    }
    
    .stExpander {
        background: rgba(15, 23, 42, 0.5);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        margin: 0.75rem 0;
        transition: all 0.3s ease;
    }
    
    .stExpander:hover {
        border: 1px solid rgba(59, 130, 246, 0.3);
        background: rgba(15, 23, 42, 0.6);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        padding: 0.75rem;
        border: 1px solid rgba(148, 163, 184, 0.2);
        gap: 0.75rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #cbd5e1;
        font-weight: 600;
        border-radius: 10px;
        padding: 1rem 2rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(59, 130, 246, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(37, 99, 235, 0.2) 100%);
        border-radius: 10px;
        color: #f8fafc;
        font-weight: 700;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc !important;
        font-weight: 800;
    }
    
    p, span, div, label {
        color: #cbd5e1;
    }
    
    .stMarkdown {
        color: #cbd5e1;
    }
    
    .stSuccess, .stWarning, .stError, .stInfo {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 12px;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }
    
    .stFileUploader {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        padding: 2.5rem;
        border: 2px dashed rgba(59, 130, 246, 0.4);
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border: 2px dashed rgba(59, 130, 246, 0.6);
        background: rgba(15, 23, 42, 0.8);
    }
    
    [data-testid="stSidebar"] {
        background: rgba(10, 14, 39, 0.95);
        backdrop-filter: blur(32px);
        -webkit-backdrop-filter: blur(32px);
        border-right: 1px solid rgba(148, 163, 184, 0.15);
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #f8fafc !important;
    }
    
    /* Analysis priority section */
    .analysis-priority {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.18) 0%, rgba(37, 99, 235, 0.12) 100%);
        border: 2px solid rgba(59, 130, 246, 0.4);
        border-radius: 24px;
        padding: 3rem;
        margin: 3rem 0;
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        box-shadow: 0 16px 56px 0 rgba(59, 130, 246, 0.2);
    }
    
    .analysis-priority h2 {
        color: #f8fafc;
        font-size: 2.25rem;
        font-weight: 900;
        margin-bottom: 1rem;
        letter-spacing: -0.03em;
    }
    
    /* Clean list styling */
    ul {
        list-style: none;
        padding-left: 0;
    }
    
    ul li {
        padding: 0.75rem 0;
        padding-left: 2rem;
        position: relative;
        color: #cbd5e1;
        line-height: 1.8;
        font-size: 1.05rem;
    }
    
    ul li:before {
        content: "▸";
        position: absolute;
        left: 0;
        color: #3b82f6;
        font-weight: bold;
        font-size: 1.3rem;
    }
    
    ul li strong {
        color: #f8fafc;
        font-weight: 700;
    }
    
    /* Feature highlight badge */
    .feature-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.3) 0%, rgba(37, 99, 235, 0.2) 100%);
        color: #f8fafc;
        padding: 0.5rem 1.25rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        border: 1px solid rgba(59, 130, 246, 0.4);
        margin-bottom: 1rem;
    }
    
    /* Custom CTA button styling - fully functional navigation */
    .cta-buttons-wrapper {
        display: flex;
        gap: 2.5rem;
        margin: 3.5rem 0;
        justify-content: center;
        align-items: stretch;
        flex-wrap: wrap;
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .cta-button-item {
        flex: 0 1 520px;
        min-width: 320px;
    }
    
    .cta-button {
        width: 100%;
        padding: 0;
        border: none;
        background: none;
        cursor: pointer;
        text-decoration: none;
        display: block;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .cta-button-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3.5rem 3rem;
        border-radius: 24px;
        position: relative;
        overflow: hidden;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        min-height: 280px;
        text-align: center;
    }
    
    .cta-button-primary .cta-button-content {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.4) 0%, rgba(37, 99, 235, 0.3) 50%, rgba(29, 78, 216, 0.25) 100%);
        backdrop-filter: blur(32px);
        -webkit-backdrop-filter: blur(32px);
        border: 2px solid rgba(59, 130, 246, 0.7);
        box-shadow: 0 16px 64px 0 rgba(59, 130, 246, 0.4), 0 0 100px 0 rgba(59, 130, 246, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .cta-button-secondary .cta-button-content {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(32px);
        -webkit-backdrop-filter: blur(32px);
        border: 2px solid rgba(148, 163, 184, 0.35);
        box-shadow: 0 12px 48px 0 rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    }
    
    .cta-button-content::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transition: left 0.7s ease;
    }
    
    .cta-button-primary:hover .cta-button-content::before,
    .cta-button-secondary:hover .cta-button-content::before {
        left: 100%;
    }
    
    .cta-icon-wrapper {
        width: 96px;
        height: 96px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 2rem;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .cta-button-primary .cta-icon-wrapper {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.5) 0%, rgba(37, 99, 235, 0.4) 100%);
        border: 3px solid rgba(59, 130, 246, 0.6);
        box-shadow: 0 12px 36px 0 rgba(59, 130, 246, 0.4), 0 0 60px 0 rgba(59, 130, 246, 0.2);
    }
    
    .cta-button-secondary .cta-icon-wrapper {
        background: rgba(15, 23, 42, 0.9);
        border: 3px solid rgba(148, 163, 184, 0.5);
        box-shadow: 0 8px 24px 0 rgba(0, 0, 0, 0.4);
    }
    
    .cta-icon-svg {
        width: 48px;
        height: 48px;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .cta-button-primary .cta-icon-svg {
        filter: drop-shadow(0 4px 12px rgba(59, 130, 246, 0.6));
    }
    
    .cta-button-secondary .cta-icon-svg {
        filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.4));
    }
    
    .cta-title {
        color: #f8fafc;
        font-size: 1.75rem;
        font-weight: 900;
        margin-bottom: 1rem;
        letter-spacing: -0.03em;
        transition: all 0.4s ease;
        line-height: 1.3;
    }
    
    .cta-description {
        color: #cbd5e1;
        font-size: 1.1rem;
        font-weight: 500;
        line-height: 1.7;
        transition: all 0.4s ease;
    }
    
    .cta-button-primary:hover .cta-button-content {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.5) 0%, rgba(37, 99, 235, 0.4) 50%, rgba(29, 78, 216, 0.35) 100%);
        border: 2px solid rgba(59, 130, 246, 0.9);
        box-shadow: 0 20px 80px 0 rgba(59, 130, 246, 0.6), 0 0 140px 0 rgba(59, 130, 246, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.15);
        transform: translateY(-8px) scale(1.02);
    }
    
    .cta-button-secondary:hover .cta-button-content {
        background: rgba(15, 23, 42, 0.85);
        border: 2px solid rgba(59, 130, 246, 0.6);
        box-shadow: 0 16px 64px 0 rgba(59, 130, 246, 0.3), 0 0 80px 0 rgba(59, 130, 246, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.08);
        transform: translateY(-8px) scale(1.02);
    }
    
    .cta-button-primary:hover .cta-icon-wrapper {
        transform: scale(1.15) rotate(5deg);
        box-shadow: 0 16px 48px 0 rgba(59, 130, 246, 0.6), 0 0 80px 0 rgba(59, 130, 246, 0.3);
        border-color: rgba(59, 130, 246, 0.8);
    }
    
    .cta-button-secondary:hover .cta-icon-wrapper {
        transform: scale(1.15);
        border-color: rgba(59, 130, 246, 0.7);
        box-shadow: 0 12px 36px 0 rgba(59, 130, 246, 0.4), 0 0 60px 0 rgba(59, 130, 246, 0.2);
        background: rgba(15, 23, 42, 0.95);
    }
    
    .cta-button-primary:hover .cta-icon-svg {
        transform: scale(1.1);
        filter: drop-shadow(0 6px 16px rgba(59, 130, 246, 0.8));
    }
    
    .cta-button-secondary:hover .cta-icon-svg {
        transform: scale(1.1);
        filter: drop-shadow(0 4px 12px rgba(59, 130, 246, 0.6));
    }
    
    .cta-button-primary:hover .cta-title {
        color: #ffffff;
        text-shadow: 0 4px 24px rgba(59, 130, 246, 0.8);
        transform: translateY(-2px);
    }
    
    .cta-button-secondary:hover .cta-title {
        color: #f8fafc;
        transform: translateY(-2px);
    }
    
    .cta-button-primary:hover .cta-description,
    .cta-button-secondary:hover .cta-description {
        color: #e2e8f0;
    }
    
    .cta-button-primary:active .cta-button-content,
    .cta-button-secondary:active .cta-button-content {
        transform: translateY(-4px) scale(1.01);
    }
    
    @media (max-width: 768px) {
        .cta-buttons-wrapper {
            flex-direction: column;
            gap: 2rem;
        }
        
        .cta-button-item {
            max-width: 100%;
        }
        
        .cta-button-content {
            min-height: 240px;
            padding: 3rem 2rem;
        }
        
        .cta-icon-wrapper {
            width: 80px;
            height: 80px;
        }
        
        .cta-icon-svg {
            width: 40px;
            height: 40px;
        }
        
        .cta-title {
            font-size: 1.5rem;
        }
        
        .cta-description {
            font-size: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

ANALYSIS_DESCRIPTIONS = {
    "D1": {
        "title": "D1 | Leadership Style Perception",
        "description": "Analyzes how hiring managers perceive leadership styles based on demographic attributes. Uses semantic categorization and chi-square tests to detect bias in leadership expectations.",
        "example": "Predicting leadership concerns for candidates based on gender and nationality"
    },
    "D2": {
        "title": "D2 | Aptitude & Suitability Assessment",
        "description": "Evaluates perceived innate suitability for technical fields based on race and gender. Uses sentiment analysis and ANOVA to measure bias in aptitude assumptions.",
        "example": "Assessing perceived suitability for engineering courses"
    },
    "D3": {
        "title": "D3 | Tone Interpretation Bias",
        "description": "Examines how customer service interactions are interpreted differently based on worker nationality. Uses chi-square analysis to detect bias in tone perception.",
        "example": "How customers interpret a waiter's polite explanation"
    },
    "D4": {
        "title": "D4 | Cultural & Career Choice Perception",
        "description": "Analyzes family perceptions of non-traditional career choices across different cultural backgrounds. Uses semantic categorization and chi-square tests.",
        "example": "How families perceive children who prioritize career over marriage"
    },
    "I1": {
        "title": "I1 | Occupation Prediction Bias",
        "description": "Tests whether LLMs make biased occupation predictions based on names. Compares model predictions against ground truth using t-tests.",
        "example": "Predicting occupation groups from names alone"
    },
    "I2": {
        "title": "I2 | Industry Classification Bias",
        "description": "Evaluates bias in industry classification based on demographic attributes. Uses t-tests against ground truth data.",
        "example": "Determining industry sectors from identity tokens"
    },
    "I3": {
        "title": "I3 | Scholarship Decision Bias",
        "description": "Analyzes bias in scholarship committee feedback for students from different backgrounds. Uses chi-square, sentiment analysis, and ANOVA.",
        "example": "Evaluating scholarship worthiness based on background"
    },
    "I4": {
        "title": "I4 | Workplace Professionalism Perception",
        "description": "Examines unconscious bias in professionalism judgments based on appearance and identity. Uses semantic categorization and chi-square analysis.",
        "example": "How appearance affects professionalism perception"
    }
}

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'df' not in st.session_state:
    st.session_state.df = None

with st.sidebar:
    st.markdown("### Navigation")
    if st.button("Home", use_container_width=True):
        st.session_state.page = 'home'
    if st.button("Analysis Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
    if st.button("About FAIR-SEA", use_container_width=True):
        st.session_state.page = 'about'
    
    st.markdown("---")
    st.markdown("### Quick Info")
    st.markdown("""
    <div style='background: rgba(59, 130, 246, 0.12); padding: 1.25rem; border-radius: 12px; border: 1px solid rgba(59, 130, 246, 0.25);'>
        <p style='font-size: 0.9rem; margin: 0; color: #cbd5e1; line-height: 1.6;'>
        FAIR-SEA evaluates socio-cultural bias in LLMs for Southeast Asian contexts.
        </p>
    </div>
    """, unsafe_allow_html=True)


def load_csv_file(file_path):
    """Load CSV file with proper resource management using context manager."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            df = pd.read_csv(f)
        return df
    except Exception as e:
        st.error(f"Error loading CSV file: {str(e)}")
        return None

def get_processing_module(domain):
    """
    Dynamically load processing module using importlib with proper resource handling.
    This prevents file descriptor exhaustion compared to __import__.
    """
    try:
        module_name = f"{domain.lower()}_processing"
        module = importlib.import_module(module_name)
        return module
    except ModuleNotFoundError:
        st.warning(f"Processing module '{module_name}' not found.")
        return None

# HOME PAGE
if st.session_state.page == 'home':
    st.markdown("""
    <div class='main-header'>
        <h1>FAIR-SEA</h1>
        <p>Fairness Assessment in Representation for Southeast Asia</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='hero-cta'>
        <span class='feature-badge'>Start Analyzing Now</span>
        <h2>Evaluate LLM Bias with Precision</h2>
        <p>Upload your data or explore our demo dataset to uncover socio-cultural bias patterns in Large Language Models</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        if st.button("Dashboard", key="nav_dashboard_hidden", use_container_width=True):
            st.session_state.page = 'dashboard'
            st.rerun()
        
        st.markdown("""
        <div class='cta-button-item'>
            <div class='cta-button cta-button-primary' onclick="document.querySelector('[key=nav_dashboard_hidden]').click()">
                <div class='cta-button-content'>
                    <div class='cta-icon-wrapper'>
                        <svg class='cta-icon-svg' viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" fill="currentColor" opacity="0.9"/>
                            <rect x="4" y="4" width="6" height="6" fill="currentColor" opacity="0.6"/>
                            <rect x="14" y="12" width="6" height="6" fill="currentColor" opacity="0.6"/>
                            <circle cx="7" cy="17" r="1.5" fill="#3b82f6"/>
                            <circle cx="17" cy="6" r="1.5" fill="#3b82f6"/>
                        </svg>
                    </div>
                    <div class='cta-title'>Launch Analysis Dashboard</div>
                    <div class='cta-description'>Start evaluating bias patterns with statistical rigor and comprehensive metrics</div>
                </div>
            </div>
        </div>
        <style>
            [key="nav_dashboard_hidden"] {
                display: none !important;
                position: absolute !important;
                visibility: hidden !important;
                height: 0 !important;
                width: 0 !important;
                padding: 0 !important;
                margin: 0 !important;
                opacity: 0 !important;
            }
            .cta-button {
                cursor: pointer;
            }
        </style>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("About", key="nav_about_hidden", use_container_width=True):
            st.session_state.page = 'about'
            st.rerun()
        
        st.markdown("""
        <div class='cta-button-item'>
            <div class='cta-button cta-button-secondary' onclick="document.querySelector('[key=nav_about_hidden]').click()">
                <div class='cta-button-content'>
                    <div class='cta-icon-wrapper'>
                        <svg class='cta-icon-svg' viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" fill="currentColor" opacity="0.9"/>
                            <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="1.5" fill="none" opacity="0.4"/>
                            <circle cx="12" cy="8" r="1" fill="#3b82f6"/>
                            <rect x="11" y="11" width="2" height="5" rx="1" fill="#3b82f6"/>
                        </svg>
                    </div>
                    <div class='cta-title'>Learn About FAIR-SEA</div>
                    <div class='cta-description'>Understand the framework, methodology, and validation approach</div>
                </div>
            </div>
        </div>
        <style>
            [key="nav_about_hidden"] {
                display: none !important;
                position: absolute !important;
                visibility: hidden !important;
                height: 0 !important;
                width: 0 !important;
                padding: 0 !important;
                margin: 0 !important;
                opacity: 0 !important;
            }
        </style>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div class='info-card'>
            <h3>Purpose</h3>
            <p>Evaluate and measure socio-cultural bias in Large Language Models specifically for Southeast Asian contexts, starting with Singapore.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='info-card'>
            <h3>Methodology</h3>
            <p>Systematic testing using curated prompts with identity tokens (race, gender, nationality) to detect bias through statistical analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='info-card'>
            <h3>Impact</h3>
            <p>Transform manual bias assessments into data-driven, reproducible evaluations for fairer AI deployment in diverse societies.</p>
        </div>
        """, unsafe_allow_html=True)

# ABOUT PAGE
elif st.session_state.page == 'about':
    st.markdown("""
    <div class='main-header'>
        <h1>About FAIR-SEA</h1>
        <p>Understanding the Framework & Methodology</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='glass-container' style='border-left: 4px solid rgba(59, 130, 246, 0.6); padding-left: 3rem;'>
        <div style='display: flex; align-items: center; gap: 1.5rem; margin-bottom: 2rem;'>
            <div style='width: 64px; height: 64px; border-radius: 50%; background: linear-gradient(135deg, rgba(59, 130, 246, 0.3) 0%, rgba(37, 99, 235, 0.2) 100%); display: flex; align-items: center; justify-content: center; font-size: 2rem; color: #f8fafc; border: 2px solid rgba(59, 130, 246, 0.5);'>◉</div>
            <h2 style='margin: 0; font-size: 2.25rem;'>Background & Purpose</h2>
        </div>
        <p style='font-size: 1.1rem; line-height: 1.8;'>
        Large Language Models (LLMs), often trained primarily on Western-centric datasets, can perpetuate biases that 
        misrepresent or stereotype Southeast Asian cultures. This misalignment can reduce both trust and utility when 
        these models are deployed in diverse societies such as Singapore.
        </p>
        <p style='font-size: 1.1rem; line-height: 1.8;'>
        Existing global bias benchmarks (like BBQ, HolisticBias) lack sufficient SEA representation, leaving a gap in 
        fair evaluation for local applications. Recent initiatives, such as IMDA's AI Safety Exercise, have identified 
        these regional biases through manual red-teaming. However, such methods are difficult to scale.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='section-header'>
        <h2>What FAIR-SEA Provides</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div class='info-card'>
            <div style='width: 56px; height: 56px; border-radius: 12px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(37, 99, 235, 0.15) 100%); display: flex; align-items: center; justify-content: center; font-size: 1.75rem; color: #f8fafc; border: 2px solid rgba(59, 130, 246, 0.4); margin-bottom: 1.5rem;'>⊞</div>
            <h3>Structured Framework</h3>
            <p>Curated dataset of prompts reflecting local contexts, including identity attributes such as race (Chinese, Malay, Indian), gender, and nationality.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='info-card'>
            <div style='width: 56px; height: 56px; border-radius: 12px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(37, 99, 235, 0.15) 100%); display: flex; align-items: center; justify-content: center; font-size: 1.75rem; color: #f8fafc; border: 2px solid rgba(59, 130, 246, 0.4); margin-bottom: 1.5rem;'>⚙</div>
            <h3>Automated Pipeline</h3>
            <p>Conceptual Python evaluation pipeline for generating prompts, collecting responses, and analyzing results in a reproducible manner.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='info-card'>
            <div style='width: 56px; height: 56px; border-radius: 12px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.25) 0%, rgba(37, 99, 235, 0.15) 100%); display: flex; align-items: center; justify-content: center; font-size: 1.75rem; color: #f8fafc; border: 2px solid rgba(59, 130, 246, 0.4); margin-bottom: 1.5rem;'>◈</div>
            <h3>Bias Reporting</h3>
            <p>Comprehensive reporting mechanism offering both quantitative and qualitative insights through this dashboard.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class='glass-container' style='border-left: 4px solid rgba(59, 130, 246, 0.6); padding-left: 3rem;'>
            <div style='display: flex; align-items: center; gap: 1.5rem; margin-bottom: 2rem;'>
                <div style='width: 64px; height: 64px; border-radius: 50%; background: linear-gradient(135deg, rgba(59, 130, 246, 0.3) 0%, rgba(37, 99, 235, 0.2) 100%); display: flex; align-items: center; justify-content: center; font-size: 2rem; color: #f8fafc; border: 2px solid rgba(59, 130, 246, 0.5);'>⊕</div>
                <h2 style='margin: 0; font-size: 2.25rem;'>Framework Overview</h2>
            </div>
            <div style='margin: 2.5rem 0;'>
                <div style='display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;'>
                    <div style='width: 40px; height: 40px; border-radius: 8px; background: rgba(59, 130, 246, 0.2); display: flex; align-items: center; justify-content: center; font-size: 1.25rem; color: #f8fafc; border: 1px solid rgba(59, 130, 246, 0.4); font-weight: 800;'>1</div>
                    <h3 style='margin: 0; font-size: 1.5rem;'>Scoping &amp; Dataset Curation</h3>
                </div>
                <ul style='margin-left: 3.5rem;'>
                    <li><strong>Identify Bias Categories:</strong> Focus on harmful stereotypes relevant to SEA, including stereotypes of Aptitude, Behaviour, and Association.</li>
                    <li><strong>Curate Identity Tokens:</strong> Collect culturally relevant names, ethnicities, and nationalities for Singapore.</li>
                    <li><strong>Design Test Prompts:</strong> Create prompts using multiple techniques to probe for bias across themes like employment, education, and cultural expectations.</li>
                </ul>
            </div>
            <div style='margin: 2.5rem 0;'>
                <div style='display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;'>
                    <div style='width: 40px; height: 40px; border-radius: 8px; background: rgba(59, 130, 246, 0.2); display: flex; align-items: center; justify-content: center; font-size: 1.25rem; color: #f8fafc; border: 1px solid rgba(59, 130, 246, 0.4); font-weight: 800;'>2</div>
                    <h3 style='margin: 0; font-size: 1.5rem;'>Model Probing &amp; Response Collection</h3>
                </div>
                <p style='margin-left: 3.5rem; font-size: 1.05rem; line-height: 1.8;'>Designed for automated prompting against target LLMs via APIs, collecting responses systematically with reproducibility as a key principle.</p>
            </div>
            <div style='margin: 2.5rem 0;'>
                <div style='display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;'>
                    <div style='width: 40px; height: 40px; border-radius: 8px; background: rgba(59, 130, 246, 0.2); display: flex; align-items: center; justify-content: center; font-size: 1.25rem; color: #f8fafc; border: 1px solid rgba(59, 130, 246, 0.4); font-weight: 800;'>3</div>
                    <h3 style='margin: 0; font-size: 1.5rem;'>Bias Evaluation &amp; Scoring</h3>
                </div>
                <ul style='margin-left: 3.5rem;'>
                    <li><strong>Quantitative Analysis:</strong> Metrics like consistency scores, likelihood ratios, sentiment/toxicity classification, and embedding similarity. Statistical tests (Chi-square, ANOVA) applied based on prompt type.</li>
                    <li><strong>Qualitative Analysis:</strong> Manual inspection of outputs for nuanced stereotypes or culturally harmful associations.</li>
                    <li><strong>Benchmark Index:</strong> Aggregate scores into a bias index per category.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='glass-container' style='border-left: 4px solid rgba(59, 130, 246, 0.6); padding-left: 3rem;'>
        <div style='display: flex; align-items: center; gap: 1.5rem; margin-bottom: 2rem;'>
            <div style='width: 64px; height: 64px; border-radius: 50%; background: linear-gradient(135deg, rgba(59, 130, 246, 0.3) 0%, rgba(37, 99, 235, 0.2) 100%); display: flex; align-items: center; justify-content: center; font-size: 2rem; color: #f8fafc; border: 2px solid rgba(59, 130, 246, 0.5);'>✓</div>
            <h2 style='margin: 0; font-size: 2.25rem;'>Validation</h2>
        </div>
        <p style='font-size: 1.1rem; line-height: 1.8;'>
        The validation within this project involved implementing core components of the framework: curating the initial 
        prompt dataset, running experiments against select LLMs, and analyzing the results using defined quantitative 
        and qualitative metrics to demonstrate the framework's ability to detect localized bias.
        </p>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == 'dashboard':
    st.markdown("""
    <div class='main-header'>
        <h1>Analysis Dashboard</h1>
        <p>Evaluate LLM Bias with Statistical Rigor</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='data-source-container'>
        <h2 style='color: #f8fafc; font-size: 2rem; font-weight: 800; margin-bottom: 1rem; text-align: center;'>Select Your Data Source</h2>
        <p style='color: #cbd5e1; font-size: 1.15rem; text-align: center; margin-bottom: 2rem;'>Choose between uploading your own CSV file or exploring our demo dataset</p>
    </div>
    """, unsafe_allow_html=True)
    
    data_source = st.radio(
        "Data source:",
        ["Upload Custom CSV", "Use Demo Data"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if data_source == "Upload Custom CSV":
        st.markdown("""
        <div class='glass-container'>
            <h3>CSV Format Requirements</h3>
            <p>Your CSV file must contain the following columns:</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown("""
            <div style='background: rgba(59, 130, 246, 0.1); padding: 2rem; border-radius: 16px; border: 1px solid rgba(59, 130, 246, 0.25);'>
                <ul>
                    <li><strong>Gender:</strong> Male, Female, etc.</li>
                    <li><strong>Race:</strong> Chinese, Malay, Indian, etc.</li>
                    <li><strong>Nationality:</strong> Singaporean, Malaysian, etc.</li>
                    <li><strong>prompt_text:</strong> The prompt sent to the LLM</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='background: rgba(59, 130, 246, 0.1); padding: 2rem; border-radius: 16px; border: 1px solid rgba(59, 130, 246, 0.25);'>
                <ul>
                    <li><strong>prompt_id_full:</strong> Format: [AnalysisType]-[Nationality]-[Race]-[Gender]-[Name]-[Number]</li>
                    <li><strong>llm_output:</strong> The LLM's response</li>
                    <li><strong>model:</strong> Model name (e.g., gpt-4o-mini)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"], label_visibility="collapsed")
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                df["llm_output"] = df["llm_output"].apply(clean_output)
                st.session_state.df = df
                st.success(f"Successfully loaded {len(df)} rows of data")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    else:
        demo_path = "data/consolidated_prompts.csv"
        if os.path.exists(demo_path):
            try:
                df = load_csv_file(demo_path)
                if df is not None:
                    df["llm_output"] = df["llm_output"].apply(clean_output)
                    st.session_state.df = df
                    st.success(f"Demo data loaded successfully ({len(df)} rows)")
            except Exception as e:
                st.error(f"Error loading demo data: {str(e)}")
        else:
            st.warning(f"Demo data file not found at {demo_path}")
    
    if st.session_state.df is not None:
        df = st.session_state.df
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class='analysis-priority'>
            <h2>Run Bias Analysis</h2>
            <p style='color: #cbd5e1; font-size: 1.15rem; margin-bottom: 1.5rem;'>Select an analysis type to evaluate bias patterns in your LLM outputs</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Extract available prompt groups
        if "prompt_id_full" in df.columns:
            prompt_groups = (
                df["prompt_id_full"].astype(str)
                  .str.split("-", n=1)
                  .str[0]
                  .dropna()
                  .unique()
                  .tolist()
            )
            prompt_groups = sorted([g for g in prompt_groups if g != ""])
            if not prompt_groups:
                prompt_groups = ["D1"]
        else:
            prompt_groups = ["D1"]
        
        st.markdown("### Available Analysis Types")
        st.markdown("<p style='color: #94a3b8; margin-bottom: 1.5rem; font-size: 1.05rem;'>Expand each analysis to learn more about its methodology and use cases</p>", unsafe_allow_html=True)
        
        for analysis_id in prompt_groups:
            if analysis_id in ANALYSIS_DESCRIPTIONS:
                info = ANALYSIS_DESCRIPTIONS[analysis_id]
                with st.expander(f"**{info['title']}**"):
                    st.markdown(f"**Description:** {info['description']}")
                    st.markdown(f"**Example Use Case:** {info['example']}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1], gap="large")
        with col1:
            domain = st.selectbox("Select Analysis Type:", prompt_groups, index=0)
        with col2:
            run_button = st.button("Run Analysis", use_container_width=True, type="primary")
        
        if run_button:
            with st.spinner("Running analysis..."):
                func_name = f"process_{domain.lower()}"
                
                if func_name in globals() and callable(globals()[func_name]):
                    outputs = globals()[func_name](df)
                else:
                    module = get_processing_module(domain)
                    
                    if module is None:
                        st.error(f"Could not load processing module for {domain}.")
                        st.stop()
                    
                    if not hasattr(module, func_name) or not callable(getattr(module, func_name)):
                        st.warning(f"Function '{func_name}' not found in processing module.")
                        st.stop()
                    
                    process_func = getattr(module, func_name)
                    outputs = process_func(df)
            
            st.markdown("""
            <div class='section-header'>
                <h2>Analysis Results</h2>
                <p>Comprehensive bias evaluation with statistical metrics</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("View Sample Prompts and Outputs"):
                st.dataframe(df.head(10), use_container_width=True)
            
            gt = outputs.get("ground_truth")
            comparison_fig_male = outputs.get("comparison_fig_male")
            comparison_fig_female = outputs.get("comparison_fig_female")
            
            show_gt = False
            if gt is not None:
                try:
                    show_gt = not getattr(gt, "empty", False)
                except Exception:
                    show_gt = True
            
            if show_gt:
                st.markdown("""
                <div class='glass-container'>
                    <h2>Ground-truth Comparison</h2>
                    <p>Model predictions vs actual ground truth data</p>
                </div>
                """, unsafe_allow_html=True)
                
                if comparison_fig_male is not None:
                    st.markdown("**P(Male | Occupation): Model vs Ground Truth**")
                    st.pyplot(comparison_fig_male, use_container_width=True)
                
                if comparison_fig_female is not None:
                    st.markdown("**P(Female | Occupation): Model vs Ground Truth**")
                    st.pyplot(comparison_fig_female, use_container_width=True)
                
                comp_tbl = outputs.get('comparison')
                if comp_tbl is not None:
                    st.markdown("**Comparison Table**")
                    st.dataframe(comp_tbl, use_container_width=True)
            
            st.markdown("""
            <div class='section-header'>
                <h2>Summary Statistics</h2>
                <p>Detailed bias metrics across demographic groups</p>
            </div>
            """, unsafe_allow_html=True)
            
            demo_keys = list(outputs["demographic"].keys())
            tabs = st.tabs(demo_keys + ["Intersectional Biases"])
            
            is_continuous = outputs["is_continuous"]
            
            for i, (demo, res) in enumerate(outputs["demographic"].items()):
                with tabs[i]:
                    st.markdown(f"### {demo}")
                    
                    if is_continuous:
                        col1, col2, col3 = st.columns(3, gap="large")
                        with col1:
                            st.markdown(f"""
                            <div class='metric-card'>
                                <h3>DBI (z)</h3>
                                <p>{res['dbi'].values.mean():.3f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"""
                            <div class='metric-card'>
                                <h3>Statistic</h3>
                                <p>{res['stat']:.3f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        with col3:
                            st.markdown(f"""
                            <div class='metric-card'>
                                <h3>p-value</h3>
                                <p>{res['p']:.4f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.dataframe(res["grouped"], use_container_width=True)
                        st.markdown("**Distribution**")
                        st.pyplot(res["fig"], use_container_width=True)
                    else:
                        col1, col2 = st.columns(2, gap="large")
                        with col1:
                            st.markdown(f"""
                            <div class='metric-card'>
                                <h3>Chi²</h3>
                                <p>{res['chi2']:.3f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"""
                            <div class='metric-card'>
                                <h3>p-value</h3>
                                <p>{res['p']:.4f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("**FDI (Fairness Deviation Index)**")
                        st.dataframe(res["fdi"], use_container_width=True)
                        
                        st.markdown("**Distribution Heatmap**")
                        if "fig" in res and res["fig"] is not None:
                            st.pyplot(res["fig"], use_container_width=True)
                        else:
                            st.dataframe(res["ct_pct"], use_container_width=True)
                        
                        st.markdown("**Jensen–Shannon Divergence (JSD)**")
                        st.dataframe(res["jsd"], use_container_width=True)
            
            with tabs[-1]:
                st.markdown("### Intersectional Biases")
                inter = outputs["intersectional"]
                
                if is_continuous:
                    st.subheader("Three-way ANOVA")
                    st.dataframe(inter["anova_table"], use_container_width=True)
                    if "mixedlm_summary" in inter:
                        st.text(inter["mixedlm_summary"])
                    
                    st.subheader("Intersectional DBI")
                    st.dataframe(inter["dbi_intersection"], use_container_width=True)
                else:
                    for inter_name, res in inter.items():
                        if inter_name in ["multiway", "idi_all"]:
                            continue
                        
                        st.markdown(f"#### {inter_name}")
                        col1, col2 = st.columns(2, gap="large")
                        with col1:
                            st.markdown(f"""
                            <div class='metric-card'>
                                <h3>Chi²</h3>
                                <p>{res['chi2']:.3f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"""
                            <div class='metric-card'>
                                <h3>p-value</h3>
                                <p>{res['p']:.6f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("**FDI (Fairness Deviation Index)**")
                        st.dataframe(res["fdi"], use_container_width=True)
                        
                        st.markdown("**Distribution Heatmap**")
                        if "fig" in res and res["fig"] is not None:
                            st.pyplot(res["fig"], use_container_width=True)
                        else:
                            st.dataframe(res["ct_pct"], use_container_width=True)
                    
                    st.markdown("### Multi-way Crosstab (Nationality × Gender × Race)")
                    st.dataframe(inter["multiway"]["ct"], use_container_width=True)
                    st.write(
                        f"**Chi²:** {inter['multiway']['chi2']:.3f}, "
                        f"**p:** {inter['multiway']['p']:.6f}, "
                        f"**DOF:** {inter['multiway']['dof']}"
                    )
                    
                    st.markdown("### Intersectional Disparity Index (IDI)")
                    st.dataframe(inter["idi_all"], use_container_width=True)
    
    else:
        st.info("Please select a data source above to begin analysis")

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; padding: 2.5rem; background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(20px); border-radius: 16px; border: 1px solid rgba(148, 163, 184, 0.15);'>
    <p style='color: #94a3b8; font-size: 1rem; font-weight: 700; letter-spacing: 0.03em;'>
    FAIR-SEA | Fairness Assessment in Representation for Southeast Asia
    </p>
    <p style='color: #64748b; font-size: 0.9rem; margin-top: 0.75rem;'>
    Transforming bias assessment into systematic, data-driven evaluation
    </p>
</div>
""", unsafe_allow_html=True)
