import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from business_data import OPTION_DESCRIPTIONS, load_process_details, load_business_outcomes

# --- Constants & Data Structures ---

OPTIONS = ["Basic", "Advanced", "Leading", "Emerging"]
VALUE_MAP = {"Basic": 0.33, "Advanced": 1.33, "Leading": 2.66, "Emerging": 4}

QUESTIONS = {
    "1A": "How frictionless is omni‑channel user login (mobile, web, API)?",
    "1B": "How intuitive is the payment‑setup experience (single & bulk)?",
    "1C": "To what extent is field‑level validation automated?",
    "1D": "Is submission captured in real‑time event streams?",
    "2A": "Strength of primary credential verification (biometric / passkey)?",
    "2B": "Depth of multi‑factor & risk‑based authentication?",
    "2C": "Are corporate role & limit checks enforced real‑time?",
    "2D": "Sophistication of secure session management?",
    "3A": "Coverage of completeness & format checks pre‑submission?",
    "3B": "Automation of business‑rule enforcement (limits, duplicates)?",
    "3C": "Speed and accuracy of preliminary sanctions screening?",
    "3D": "Quality of real‑time error feedback to users?",
    "4A": "Granularity of payment classification (priority, value, rail)?",
    "4B": "Intelligence of network selection across rails?",
    "4C": "Effectiveness of AI route optimisation (cost, SLA)?",
    "4D": "Reliability of event hand‑off to processing layer?",
    "5A": "Sophistication of transaction risk‑scoring models?",
    "5B": "Sanctions & watch‑list screening accuracy?",
    "5C": "Real‑time AML monitoring effectiveness?",
    "5D": "Efficiency of case handling & auto‑clear mechanisms?",
    "6A": "Clarity & UX of final transaction confirmation?",
    "6B": "Robustness of multi‑signature approvals?",
    "6C": "Frequency of systemic re‑checks pre‑execution?",
    "6D": "Immutability of lock‑in & downstream hand‑over?",
    "7A": "Automation of message formatting for external networks?",
    "7B": "Degree of data enrichment & standard mapping?",
    "7C": "Handling of truncation & unmapped fields?",
    "7D": "Maturity of error/repair queue workflows?",
    "8A": "Real‑time API transmission to clearing networks?",
    "8B": "Scalability of queue & processing architecture?",
    "8C": "Transparency in intermediary/correspondent handling?",
    "8D": "Speed of clearing acknowledgements?",
    "9A": "Frequency of reserve debit/credit settlement cycles?",
    "9B": "Latency to beneficiary account credit?",
    "9C": "Intraday liquidity management sophistication?",
    "9D": "Legal finality & irrevocability assurance?",
    "10A": "Automation level of internal reconciliation?",
    "10B": "Timeliness of customer statement updates?",
    "10C": "Efficiency in handling exceptions & returns?",
    "10D": "Responsiveness of investigation & dispute processes?",
    "11A": "Promptness & richness of transactional notifications?",
    "11B": "Flexibility of statement generation & formats?",
    "11C": "Depth of analytical dashboards & MI reporting?",
    "11D": "Granularity of real‑time status tracking?",
    "12A": "Comprehensiveness of immutable audit trail capture?",
    "12B": "Security & searchability of long‑term archival?",
    "12C": "Level of automation in regulatory filings?",
    "12D": "Ease & speed of audit retrieval and forensics?",
}

SUB_IDS = list(QUESTIONS.keys())

STAGE_NAMES = [
    "Initiation", "Authentication", "Pre‑Validation", "Orchestration", "Risk & Compliance",
    "Final Authorisation", "Message Transformation", "Clearing & Ack", "Settlement",
    "Reconciliation", "Reporting & Analytics", "Audit & Compliance"
]

STAGE_MAP = {str(i+1): SUB_IDS[i*4:(i+1)*4] for i in range(12)}

BENCHMARK = {
    "1A": 4, "1B": 4, "1C": 2.66, "1D": 2.66, "2A": 4, "2B": 4, "2C": 2.66, "2D": 2.66,
    "3A": 2.66, "3B": 2.66, "3C": 2.66, "3D": 2.66, "4A": 2.66, "4B": 2.66, "4C": 2.66, "4D": 2.66,
    "5A": 4, "5B": 4, "5C": 4, "5D": 2.66, "6A": 2.66, "6B": 2.66, "6C": 2.66, "6D": 2.66,
    "7A": 2.66, "7B": 2.66, "7C": 1.33, "7D": 1.33, "8A": 4, "8B": 4, "8C": 4, "8D": 2.66,
    "9A": 4, "9B": 4, "9C": 4, "9D": 4, "10A": 2.66, "10B": 2.66, "10C": 2.66, "10D": 2.66,
    "11A": 4, "11B": 4, "11C": 4, "11D": 2.66, "12A": 2.66, "12B": 2.66, "12C": 2.66, "12D": 2.66,
}

# Load the detailed process descriptions and business outcomes
process_details_df = load_process_details()
business_outcomes_df = load_business_outcomes()

# --- Helper Functions ---

def average(keys, obj):
    """Calculate the average value for a list of keys from an object."""
    return sum(obj.get(k, 0) for k in keys) / len(keys)

def stage_chart_data(values, to_be=None):
    """Generate data for the radar chart by stage."""
    data = []
    for idx, name in enumerate(STAGE_NAMES):
        stage_key = str(idx+1)
        row = {
            "Stage": name,
            "AsIs": average(STAGE_MAP[stage_key], values),
            "Benchmark": average(STAGE_MAP[stage_key], BENCHMARK),
        }
        if to_be:
            row["ToBe"] = average(STAGE_MAP[stage_key], to_be)
        data.append(row)
    return data

def heatmap_data(values):
    """Generate data for the gap heatmap."""
    return [
        {
            "Stage": name,
            "Diff": average(STAGE_MAP[str(idx+1)], values) - average(STAGE_MAP[str(idx+1)], BENCHMARK),
        }
        for idx, name in enumerate(STAGE_NAMES)
    ]

def detailed_gap_analysis(values):
    """Generate detailed gap analysis by question."""
    data = []
    for qid in SUB_IDS:
        stage_num = qid[0:qid.find('A')] if 'A' in qid else qid[0]
        stage_name = STAGE_NAMES[int(stage_num) - 1]
        data.append({
            "ID": qid,
            "Stage": stage_name,
            "Question": QUESTIONS[qid],
            "Your Score": values[qid],
            "Benchmark": BENCHMARK[qid],
            "Gap": values[qid] - BENCHMARK[qid]
        })
    return data

def stage_summary(values):
    """Generate summary statistics by stage."""
    data = []
    for idx, name in enumerate(STAGE_NAMES):
        stage_key = str(idx+1)
        stage_questions = STAGE_MAP[stage_key]
        
        your_avg = average(stage_questions, values)
        benchmark_avg = average(stage_questions, BENCHMARK)
        
        data.append({
            "Stage": name,
            "Your Avg": round(your_avg, 2),
            "Benchmark Avg": round(benchmark_avg, 2),
            "Gap": round(your_avg - benchmark_avg, 2),
            "Questions": len(stage_questions)
        })
    return data

# --- Streamlit UI ---

def main():
    st.set_page_config(
        page_title="Payments Capability Benchmark Portal", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("Payments Capability Benchmark Portal")
    
    st.write("""
    This portal benchmarks your payments capability maturity across 12 key stages.
    For each question, select your maturity level: Basic, Advanced, Leading, or Emerging.
    
    **You can fill both 'As-Is' (current state) and 'To-Be' (target state) for comparison.**
    """)
    
    # Initialize session state for responses
    if "as_is" not in st.session_state:
        st.session_state["as_is"] = {k: "Basic" for k in SUB_IDS}
    if "to_be" not in st.session_state:
        st.session_state["to_be"] = {k: "Basic" for k in SUB_IDS}
    
    # Sidebar with explanation of maturity levels
    with st.sidebar:
        st.header("Maturity Levels")
        st.markdown("""
        **Basic (0.33)**: Minimal functionality, often manual processes  
        **Advanced (1.33)**: Standard industry functionality  
        **Leading (2.66)**: Above average capabilities  
        **Emerging (4.0)**: Cutting-edge, innovative capabilities
        """)
        
        st.header("Stage Descriptions")
        for i, stage in enumerate(STAGE_NAMES):
            with st.expander(f"{i+1}. {stage}"):
                st.write(f"Questions: {', '.join(STAGE_MAP[str(i+1)])}")
                for q in STAGE_MAP[str(i+1)]:
                    st.write(f"- **{q}**: {QUESTIONS[q]}")
    
    # Assessment mode selection
    mode = st.radio("Select assessment mode", ["As-Is", "To-Be"], horizontal=True)
    answers = st.session_state["as_is"] if mode == "As-Is" else st.session_state["to_be"]
    
    # Organize questions by stage for the form
    tab1, tab2, tab3 = st.tabs(["Assessment Form", "Results & Insights", "Business Outcomes"])
    
    with tab1:
        st.subheader(f"Select maturity for each sub-process ({mode}):")
        
        # Create a form organized by stages
        with st.form("assessment_form"):
            for i, stage_name in enumerate(STAGE_NAMES):
                stage_num = str(i+1)
                st.markdown(f"### Stage {stage_num}: {stage_name}")
                
                # Create columns for side-by-side questions
                cols = st.columns(2)
                stage_questions = STAGE_MAP[stage_num]
                
                for j, qid in enumerate(stage_questions):
                    col_idx = j % 2
                    with cols[col_idx]:
                        # Get the process details for this question ID
                        process_info = process_details_df[process_details_df['qid'] == qid]
                        
                        # First show the question
                        st.markdown(f"**{qid}: {QUESTIONS[qid]}**")
                        
                        # If process details are available, show the description
                        if not process_info.empty:
                            with st.expander("See description and maturity details"):
                                st.markdown(f"**Process:** {process_info.iloc[0]['process']}")
                                st.markdown(f"**Description:** {process_info.iloc[0]['description']}")
                                
                                # Display maturity level descriptions
                                st.markdown("### Maturity Levels for this Process:")
                                st.markdown(f"**Basic:** {process_info.iloc[0]['basic']}")
                                st.markdown(f"**Advanced:** {process_info.iloc[0]['advanced']}")
                                st.markdown(f"**Leading:** {process_info.iloc[0]['leading']}")
                                st.markdown(f"**Emerging:** {process_info.iloc[0]['emerging']}")
                        
                        # Show the options with tooltips
                        answers[qid] = st.selectbox(
                            "Select maturity level:",
                            OPTIONS,
                            index=OPTIONS.index(answers[qid]),
                            key=f"{mode}-{qid}",
                            help=f"{OPTIONS[0]}: {OPTION_DESCRIPTIONS[OPTIONS[0]]['description']}\n"
                                 f"{OPTIONS[1]}: {OPTION_DESCRIPTIONS[OPTIONS[1]]['description']}\n"
                                 f"{OPTIONS[2]}: {OPTION_DESCRIPTIONS[OPTIONS[2]]['description']}\n"
                                 f"{OPTIONS[3]}: {OPTION_DESCRIPTIONS[OPTIONS[3]]['description']}"
                        )
                
                if i < len(STAGE_NAMES) - 1:
                    st.divider()
                    
            submitted = st.form_submit_button("Save responses")
        
        if submitted:
            st.success(f"Responses for '{mode}' saved.")
    
    # Convert responses to numerical values for analysis
    as_is_values = {k: VALUE_MAP[v] for k, v in st.session_state["as_is"].items()}
    to_be_values = {k: VALUE_MAP[v] for k, v in st.session_state["to_be"].items()}
    
    with tab2:
        if all(k in st.session_state["as_is"] for k in SUB_IDS):
            st.header("Results & Insights")
            
            # --- Radar Chart by Stage ---
            st.subheader("Capability Radar by Stage")
            radar_df = pd.DataFrame(stage_chart_data(as_is_values, to_be_values))
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=radar_df["AsIs"], 
                theta=radar_df["Stage"], 
                fill="toself", 
                name="As-Is",
                line=dict(color="blue")
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=radar_df["Benchmark"], 
                theta=radar_df["Stage"], 
                fill="toself", 
                name="Benchmark",
                line=dict(color="green")
            ))
            
            if any(st.session_state["to_be"][k] != "Basic" for k in SUB_IDS):
                fig.add_trace(go.Scatterpolar(
                    r=radar_df["ToBe"], 
                    theta=radar_df["Stage"], 
                    fill="toself", 
                    name="To-Be",
                    line=dict(color="orange")
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True, 
                        range=[0, 4],
                        tickvals=[0, 1, 2, 3, 4],
                        ticktext=["0", "1", "2", "3", "4"]
                    )
                ),
                showlegend=True,
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # --- Stage Summary Table ---
            st.subheader("Stage Summary")
            summary_df = pd.DataFrame(stage_summary(as_is_values))
            
            # Apply custom formatting instead of background gradient
            # Create a new column for colored text based on gap values
            summary_df["Gap Status"] = summary_df["Gap"].apply(
                lambda x: 
                    "🔴 Critical Gap" if x <= -2 else
                    "🟠 Significant Gap" if x <= -1 else
                    "🟡 Minor Gap" if x < 0 else
                    "🟢 On Track" if x < 1 else
                    "🔵 Leading"
            )
            
            st.dataframe(
                summary_df,
                hide_index=True,
                use_container_width=True
            )
            
            # --- Heatmap ---
            st.subheader("Stage-wise Gaps vs Benchmark (As-Is)")
            heat_df = pd.DataFrame(heatmap_data(as_is_values))
            
            fig_heat = go.Figure(data=go.Bar(
                x=heat_df["Stage"],
                y=heat_df["Diff"],
                marker_color=heat_df["Diff"].apply(
                    lambda x: "red" if x < -1 else "orange" if x < 0 else "lightgreen" if x < 1 else "green"
                )
            ))
            
            fig_heat.update_layout(
                title="Gap Analysis (Positive = Above Benchmark)",
                xaxis_title="Stage",
                yaxis_title="Gap Score",
                height=400
            )
            
            st.plotly_chart(fig_heat, use_container_width=True)
            
            # --- Detailed Analysis ---
            st.subheader("Detailed Question Analysis")
            detailed_df = pd.DataFrame(detailed_gap_analysis(as_is_values))
            
            # Add status column instead of using background gradient
            detailed_df["Status"] = detailed_df["Gap"].apply(
                lambda x: 
                    "🔴 Critical Gap" if x <= -2 else
                    "🟠 Significant Gap" if x <= -1 else
                    "🟡 Minor Gap" if x < 0 else
                    "🟢 On Track" if x < 1 else
                    "🔵 Leading"
            )
            
            # Allow filtering by stage
            selected_stage = st.selectbox(
                "Filter by stage:",
                ["All Stages"] + STAGE_NAMES
            )
            
            if selected_stage != "All Stages":
                filtered_df = detailed_df[detailed_df["Stage"] == selected_stage]
            else:
                filtered_df = detailed_df
            
            st.dataframe(
                filtered_df,
                hide_index=True,
                use_container_width=True
            )
            
            # --- Improvement Recommendations ---
            st.subheader("Top Improvement Opportunities")
            
            # Find the areas with the biggest gaps
            opportunity_df = detailed_df.sort_values("Gap", ascending=True).head(5)
            
            for _, row in opportunity_df.iterrows():
                with st.expander(f"{row['ID']}: {row['Question']} (Gap: {row['Gap']:.2f})"):
                    st.write(f"**Stage:** {row['Stage']}")
                    st.write(f"**Your Score:** {OPTIONS[list(VALUE_MAP.values()).index(row['Your Score'])]}")
                    st.write(f"**Benchmark:** {OPTIONS[min(3, int(row['Benchmark'] / 1.33))]}")
                    
                    # Generic improvement recommendations based on the gap
                    st.write("**Improvement Recommendation:**")
                    if row['Gap'] <= -2:
                        st.write("🔴 Critical improvement needed. Consider making this a high priority in your roadmap.")
                    elif row['Gap'] <= -1:
                        st.write("🟠 Significant gap exists. Review your current capabilities and plan for enhancement.")
                    elif row['Gap'] <= -0.5:
                        st.write("🟡 Minor gap. Consider incremental improvements to reach industry benchmark.")
                    else:
                        st.write("🟢 Close to benchmark. Maintain current capabilities while monitoring industry trends.")
        else:
            st.info("Fill all the questions in the Assessment Form tab and hit 'Save responses' to generate insights.")
            
    # Business Outcomes Tab
    with tab3:
        st.header("Business Outcomes Analysis")
        st.write("""
        Select your target business outcomes to identify which payment processes 
        you should focus on to achieve your strategic goals.
        """)
        
        # Get unique business outcomes
        business_outcomes = sorted(business_outcomes_df['business_outcome'].unique())
        
        # Allow the user to select business outcomes
        selected_outcomes = st.multiselect(
            "Select your target business outcomes:",
            business_outcomes,
            default=[business_outcomes[0]] if business_outcomes else []
        )
        
        if selected_outcomes:
            # Filter processes by selected business outcomes
            filtered_processes = business_outcomes_df[
                business_outcomes_df['business_outcome'].isin(selected_outcomes)
            ]
            
            # Create tabs for different views
            bo_tab1, bo_tab2 = st.tabs(["Processes by Outcome", "Detailed View"])
            
            with bo_tab1:
                for outcome in selected_outcomes:
                    st.subheader(f"{outcome}")
                    outcome_processes = filtered_processes[
                        filtered_processes['business_outcome'] == outcome
                    ]
                    
                    # Show processes for this outcome
                    cols = st.columns(2)
                    
                    with cols[0]:
                        st.markdown("#### Key Processes")
                        for _, row in outcome_processes.iterrows():
                            process_id = row['process_id']
                            
                            # Get the current maturity from as-is assessment
                            current_maturity = "Not assessed"
                            if process_id in st.session_state["as_is"]:
                                current_maturity = st.session_state["as_is"][process_id]
                            
                            # Get process details
                            process_info = process_details_df[process_details_df['qid'] == process_id]
                            process_name = ""
                            if not process_info.empty:
                                process_name = process_info.iloc[0]['process']
                            
                            st.markdown(f"**{process_id}: {process_name}**")
                            st.markdown(f"Current Maturity: **{current_maturity}**")
                            st.markdown(f"KPI: {row['kpi']}")
                            st.markdown(f"BOI: {row['boi']}")
                            st.markdown("---")
                    
                    with cols[1]:
                        st.markdown("#### Recommended Actions")
                        for _, row in outcome_processes.iterrows():
                            st.markdown(f"**Best-fit Lever:** {row['best_fit_lever']}")
                            st.markdown(f"**Technology Examples:** {row['tech_example']}")
                            st.markdown("---")
            
            with bo_tab2:
                st.markdown("### Detailed Business Outcome Analysis")
                
                # Prepare a dataframe for display
                display_df = filtered_processes[['process_id', 'business_outcome', 'kpi', 'boi', 'best_fit_lever']]
                
                # Add current maturity from the assessment
                display_df['Current Maturity'] = display_df['process_id'].apply(
                    lambda pid: st.session_state["as_is"].get(pid, "Not assessed")
                )
                
                # Add process name
                display_df['Process'] = display_df['process_id'].apply(
                    lambda pid: process_details_df[process_details_df['qid'] == pid]['process'].iloc[0] 
                    if not process_details_df[process_details_df['qid'] == pid].empty else ""
                )
                
                # Reorder columns for better display
                final_df = display_df[['process_id', 'Process', 'Current Maturity', 'business_outcome', 'kpi', 'boi', 'best_fit_lever']]
                final_df = final_df.rename(columns={
                    'process_id': 'ID',
                    'business_outcome': 'Business Outcome',
                    'kpi': 'KPI',
                    'boi': 'Business Outcome Indicator',
                    'best_fit_lever': 'Best-fit Lever'
                })
                
                st.dataframe(final_df, hide_index=True, use_container_width=True)
                
                # Add capability impact visualization
                st.markdown("### Impact on Capability Radar")
                
                # Create a dataframe with just the processes for the selected business outcomes
                target_processes = filtered_processes['process_id'].unique()
                
                if all(k in st.session_state["as_is"] for k in SUB_IDS):
                    # Calculate avg scores for processes aligned with business outcomes
                    targeted_values = {k: v for k, v in as_is_values.items() if k in target_processes}
                    
                    # Create a complete set of values for the radar chart
                    # For non-targeted processes, use As-Is values
                    target_focus_values = as_is_values.copy()
                    
                    # For targeted processes, assume they are improved to Leading level (2.66)
                    # This shows the impact of focusing on these processes
                    for pid in target_processes:
                        if pid in target_focus_values:
                            target_focus_values[pid] = max(target_focus_values[pid], 2.66)
                    
                    # Create radar chart
                    radar_df = pd.DataFrame(stage_chart_data(as_is_values, target_focus_values))
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatterpolar(
                        r=radar_df["AsIs"], 
                        theta=radar_df["Stage"], 
                        fill="toself", 
                        name="Current State",
                        line=dict(color="blue")
                    ))
                    
                    fig.add_trace(go.Scatterpolar(
                        r=radar_df["Benchmark"], 
                        theta=radar_df["Stage"], 
                        fill="toself", 
                        name="Benchmark",
                        line=dict(color="green")
                    ))
                    
                    if "ToBe" in radar_df.columns:
                        fig.add_trace(go.Scatterpolar(
                            r=radar_df["ToBe"], 
                            theta=radar_df["Stage"], 
                            fill="toself", 
                            name="Potential Impact",
                            line=dict(color="red")
                        ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True, 
                                range=[0, 4],
                                tickvals=[0, 1, 2, 3, 4],
                                ticktext=["0", "1", "2", "3", "4"]
                            )
                        ),
                        showlegend=True,
                        height=600
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("""
                    **Note:** This chart shows the potential impact on your capability radar 
                    if you improve the processes related to your selected business outcomes 
                    to at least a "Leading" maturity level.
                    """)
                else:
                    st.info("Complete the Assessment Form to see the potential impact on your capability radar.")

if __name__ == "__main__":
    main()
