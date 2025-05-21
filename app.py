import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from business_data import OPTION_DESCRIPTIONS, load_process_details
from business_outcomes_mapper import (
    get_business_outcomes,
    calculate_outcome_score,
    get_outcome_process_details,
    get_outcome_summary,
    create_outcome_radar_data
)
from data_loader import load_data, get_bank_names, get_bank_scores
from visualization import create_radar_chart, create_stage_chart, create_outcome_chart
from components import (
    render_bank_selection, 
    render_assessment_view, 
    render_comparison_view,
    render_outcome_analysis
)
from dashboard import render_dashboard_tab
from root_cause_analysis import render_root_cause_analysis

# Set page configuration
st.set_page_config(
    page_title="Payment Capability Diagnostic",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS from file
with open('custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    # App header
    st.title("Payment Capability Diagnostic Tool")
    st.markdown("<p style='color:#333333; font-size:1.2em;'>Assess and compare payment processing capabilities across banks and financial institutions</p>", unsafe_allow_html=True)
    
    # Initialize session state for storing assessment data
    if 'assessment_data' not in st.session_state:
        st.session_state.assessment_data = {}
    if 'current_bank' not in st.session_state:
        st.session_state.current_bank = None
    if 'comparison_banks' not in st.session_state:
        st.session_state.comparison_banks = []
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    
    # Load benchmark data
    process_data = load_process_details()
    banks = get_bank_names()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio(
        "Select Mode",
        ["Control Tower Dashboard", "Root Cause Analysis", "Assessment Tool", "Bank Comparison", "Business Outcome Analysis & Improvement"]
    )
    
    # Main application logic based on selected mode
    if app_mode == "Control Tower Dashboard":
        render_dashboard_tab()
    elif app_mode == "Root Cause Analysis":
        render_root_cause_analysis()
    elif app_mode == "Assessment Tool":
        render_assessment_view(process_data)
    elif app_mode == "Bank Comparison":
        render_comparison_view(banks)
    else:  # Business Outcome Analysis & Improvement
        render_outcome_analysis(process_data, banks)

if __name__ == "__main__":
    main()
