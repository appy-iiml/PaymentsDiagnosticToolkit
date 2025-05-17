import streamlit as st
import pandas as pd
from business_data import OPTION_DESCRIPTIONS, load_process_details
from business_outcomes_mapper import (
    get_business_outcomes,
    calculate_outcome_score,
    get_outcome_process_details,
    get_outcome_summary,
    create_outcome_radar_data
)
from data_loader import (
    load_data,
    get_bank_names,
    get_bank_scores,
    get_stage_names,
    get_process_data_for_stage
)
from visualization import (
    create_radar_chart,
    create_stage_chart,
    create_outcome_chart,
    create_maturity_heatmap
)

def render_bank_selection(banks, mode="single"):
    """
    Render bank selection component
    
    Parameters:
    - banks: List of available banks
    - mode: 'single' for selecting one bank, 'multiple' for selecting many
    """
    if mode == "single":
        selected_bank = st.selectbox(
            "Select a bank to analyze:",
            options=banks
        )
        return selected_bank
    else:
        selected_banks = st.multiselect(
            "Select banks to compare:",
            options=banks,
            default=banks[:2] if len(banks) >= 2 else banks
        )
        return selected_banks

def render_maturity_scale():
    """Render a description of the maturity scale"""
    with st.expander("About the Maturity Scale"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("### Basic (1)")
            st.write(OPTION_DESCRIPTIONS["Basic"]["description"])
        
        with col2:
            st.markdown("### Advanced (2)")
            st.write(OPTION_DESCRIPTIONS["Advanced"]["description"])
        
        with col3:
            st.markdown("### Leading (3)")
            st.write(OPTION_DESCRIPTIONS["Leading"]["description"])
        
        with col4:
            st.markdown("### Emerging (4)")
            st.write(OPTION_DESCRIPTIONS["Emerging"]["description"])

def render_process_assessment(process_data, stage_id):
    """
    Render assessment form for processes in a stage
    
    Parameters:
    - process_data: List of process dictionaries for the current stage
    - stage_id: Current stage ID
    
    Returns:
    - Total score for the stage (sum of all process scores)
    """
    stage_total = 0
    process_count = 0
    
    for process in process_data:
        st.subheader(f"{process['qid']}. {process['process']}")
        st.write(process['description'])
        
        with st.expander("See maturity level descriptions"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Basic")
                st.write(process['basic'])
                
                st.markdown("#### Advanced")
                st.write(process['advanced'])
            
            with col2:
                st.markdown("#### Leading")
                st.write(process['leading'])
                
                st.markdown("#### Emerging")
                st.write(process['emerging'])
        
        # Selection for maturity level
        maturity_options = ["Basic (1)", "Advanced (2)", "Leading (3)", "Emerging (4)"]
        current_value = None
        
        # Check if there's already a value in session state
        if process['qid'] in st.session_state.assessment_data:
            current_value = st.session_state.assessment_data[process['qid']]
            default_index = int(current_value) - 1 if current_value else 0
        else:
            default_index = 0
        
        selected_maturity = st.select_slider(
            f"Select maturity level for {process['process']}",
            options=maturity_options,
            value=maturity_options[default_index] if current_value else maturity_options[0]
        )
        
        # Extract numeric value from selection
        maturity_label = selected_maturity.split("(")[0].strip()
        
        # Convert label to score value based on new scoring system
        if maturity_label == "Basic":
            maturity_value = 0
        elif maturity_label == "Advanced":
            maturity_value = 0.33
        elif maturity_label == "Leading":
            maturity_value = 0.66
        elif maturity_label == "Emerging":
            maturity_value = 1.0
        else:
            maturity_value = 0
        
        # Store in session state
        st.session_state.assessment_data[process['qid']] = maturity_value
        
        # Accumulate for total score calculation
        stage_total += maturity_value
        process_count += 1
        
        st.markdown("---")
    
    # Return the total score for the stage (max 4 points)
    return stage_total

def render_assessment_view(process_data):
    """
    Render the assessment tool view
    
    Parameters:
    - process_data: Complete process data
    """
    st.header("Payment Capability Assessment")
    st.write("Evaluate your organization's payment capabilities across 12 stages")
    
    render_maturity_scale()
    
    # Get stage names
    stage_names = get_stage_names()
    
    # Stage selection
    selected_stage = st.selectbox(
        "Select a stage to assess:",
        options=list(range(1, 13)),
        format_func=lambda x: f"Stage {x}: {stage_names[x]}"
    )
    
    st.markdown(f"## Stage {selected_stage}: {stage_names[selected_stage]}")
    
    # Get processes for the selected stage
    stage_processes = get_process_data_for_stage(selected_stage)
    
    # Display the assessment form
    stage_score = render_process_assessment(stage_processes, selected_stage)
    
    # Show stage results
    st.markdown("## Stage Results")
    st.metric(
        label=f"Total Score for Stage {selected_stage}",
        value=f"{stage_score:.2f}/4.00"
    )
    
    # Benchmark comparison
    st.markdown("## Benchmark Comparison")
    banks_data, _ = load_data()
    
    # Allow user to select benchmark banks for comparison
    all_banks = list(banks_data.keys())
    benchmark_banks = st.multiselect(
        "Select banks for benchmark comparison:",
        options=all_banks,
        default=["JPMC (Global)", "DBS (Asia)"]
    )
    
    if not benchmark_banks:
        st.warning("Please select at least one bank for benchmark comparison")
        # Default to top banks if none selected
        benchmark_banks = ["JPMC (Global)", "DBS (Asia)"]
    
    # Filter to only include selected banks for comparison
    comparison_banks = {bank: scores for bank, scores in banks_data.items() if bank in benchmark_banks}
    
    chart = create_stage_chart(st.session_state.assessment_data, selected_stage, comparison_banks)
    st.plotly_chart(chart, use_container_width=True)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if selected_stage > 1:
            if st.button("Previous Stage"):
                st.session_state.current_stage = selected_stage - 1
                st.rerun()
    
    with col3:
        if selected_stage < 12:
            if st.button("Next Stage"):
                st.session_state.current_stage = selected_stage + 1
                st.rerun()
    
    with col2:
        if st.button("View Overall Results"):
            st.session_state.view_results = True
            st.rerun()
    
    # Overall results view
    if st.session_state.get('view_results', False):
        st.markdown("## Overall Assessment Results")
        
        # Calculate sum of scores per stage
        stage_scores = {}
        for stage_id in range(1, 13):
            stage_processes = get_process_data_for_stage(stage_id)
            process_ids = [p['qid'] for p in stage_processes]
            
            # Filter the assessment data to get only processes for this stage
            stage_assessment = {pid: st.session_state.assessment_data.get(pid, 0) 
                               for pid in process_ids if pid in st.session_state.assessment_data}
            
            if stage_assessment:
                stage_scores[stage_id] = sum(stage_assessment.values())
            else:
                stage_scores[stage_id] = 0
        
        # Overall total (out of 48 possible points - 12 stages × 4 points)
        if stage_scores:
            overall_total = sum(stage_scores.values())
            max_possible = 48.0  # 12 stages × 4 points per stage
        else:
            overall_total = 0
            max_possible = 48.0
            
        st.metric("Overall Maturity Score", f"{overall_total:.2f}/{max_possible:.2f}")
        
        # Create results dataframe
        results_df = pd.DataFrame({
            "Stage": [f"{i}. {stage_names[i]}" for i in range(1, 13)],
            "Score": [stage_scores.get(i, 0) for i in range(1, 13)]
        })
        
        st.dataframe(results_df, use_container_width=True)
        
        # Radar chart comparison with benchmarks
        st.subheader("Comparison with Industry Benchmarks")
        
        # Competitor Selection for comparison
        st.markdown("### Competitor Selection")
        show_all = st.checkbox("Show all competitors on radar", value=False)
        
        # Allow selecting benchmark banks for overall comparison
        if not show_all:
            benchmark_banks = st.multiselect(
                "Select competitors to compare",
                options=all_banks,
                default=benchmark_banks[:2] if len(benchmark_banks) >= 2 else benchmark_banks
            )
            
            if not benchmark_banks:
                st.warning("Please select at least one bank for comparison")
                benchmark_banks = ["JPMC (Global)"]
        else:
            benchmark_banks = all_banks
        
        # Prepare data for comparison including user assessment
        assessment_data = {"Your Assessment": {**stage_scores, "Overall": overall_total}}
        
        # Add assessment to bank data
        combined_data = {**assessment_data, **banks_data}
        
        # Create radar chart with selected benchmarks
        radar_banks = ["Your Assessment"] + benchmark_banks
        
        radar_fig = create_radar_chart(
            combined_data,
            radar_banks,
            "Your Assessment vs Industry Leaders"
        )
        
        st.plotly_chart(radar_fig, use_container_width=True)
        
        # Reset view results state
        if st.button("Back to Assessment"):
            st.session_state.view_results = False
            st.rerun()
            
        # Store assessment data in session state for use in other views
        st.session_state.assessment_stage_scores = stage_scores
        st.session_state.assessment_overall_total = overall_total

def render_comparison_view(banks):
    """
    Render the bank comparison view
    
    Parameters:
    - banks: List of available banks
    """
    st.header("Bank Capability Comparison")
    st.write("Compare payment capabilities across different banks")
    
    # Load data
    banks_data, _ = load_data()
    
    # Check if user has assessment data to include
    has_assessment = 'assessment_stage_scores' in st.session_state and st.session_state.assessment_stage_scores
    
    # Option to include user's assessment in comparison
    include_assessment = False
    if has_assessment:
        include_assessment = st.checkbox("Include my assessment in comparison", value=True)
        
        if include_assessment:
            # Create assessment data entry
            assessment_data = {
                "Your Assessment": {
                    **st.session_state.assessment_stage_scores,
                    "Overall": st.session_state.assessment_overall_avg
                }
            }
            # Combine with bank data
            combined_data = {**assessment_data, **banks_data}
            all_options = ["Your Assessment"] + list(banks)
        else:
            combined_data = banks_data
            all_options = list(banks)
    else:
        combined_data = banks_data
        all_options = list(banks)
    
    # Bank selection
    st.subheader("Payment Process Maturity")
    
    # Competitor Selection with checkbox for "Show all"
    st.markdown("### Competitor Selection")
    show_all = st.checkbox("Show all competitors on radar", value=False)
    
    if show_all:
        selected_banks = all_options
    else:
        selected_banks = st.multiselect(
            "Select competitors to compare",
            options=all_options,
            default=["JPMC (Global)", "DBS (Asia)"] if not include_assessment else ["Your Assessment", "JPMC (Global)"]
        )
    
    if not selected_banks:
        st.warning("Please select at least one bank to analyze")
        selected_banks = ["JPMC (Global)"]
    
    # Create radar chart
    radar_fig = create_radar_chart(combined_data, selected_banks)
    st.plotly_chart(radar_fig, use_container_width=True)
    
    # Create heatmap for detailed comparison
    if len(selected_banks) > 1:
        st.subheader("Detailed Maturity Comparison")
        try:
            heatmap = create_maturity_heatmap(combined_data, selected_banks)
            st.plotly_chart(heatmap, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate heatmap: {str(e)}")
    
    # Show overall scores in a table
    st.subheader("Overall Maturity Scores")
    
    # Create dataframe for comparison
    bank_data = []
    for bank in selected_banks:
        if bank in combined_data:
            bank_data.append({
                "Bank": bank,
                "Overall Score": combined_data[bank]["Overall"] if "Overall" in combined_data[bank] else 0
            })
    
    comparison_df = pd.DataFrame(bank_data).sort_values(by="Overall Score", ascending=False)
    st.dataframe(comparison_df, use_container_width=True)
    
    # Show stage-by-stage comparison
    st.subheader("Stage-by-Stage Comparison")
    
    # Create dataframe for detailed comparison
    stage_names = get_stage_names()
    
    # Create a column for each stage
    comparison_rows = []
    for bank in selected_banks:
        if bank in combined_data:
            row_data = {"Bank": bank}
            for stage_id in range(1, 13):
                stage_name = f"Stage {stage_id}"
                # Handle cases where bank data might not have the stage
                value = combined_data[bank].get(stage_id, 0)
                row_data[stage_name] = value
            comparison_rows.append(row_data)
    
    stage_df = pd.DataFrame(comparison_rows)
    
    if not stage_df.empty:
        st.dataframe(stage_df, use_container_width=True)
    else:
        st.warning("No data available for stage-by-stage comparison")
    
    # Add stage details
    with st.expander("Stage Details"):
        for stage_id, stage_name in stage_names.items():
            st.markdown(f"**Stage {stage_id}**: {stage_name}")

def render_outcome_analysis(banks):
    """
    Render the business outcome analysis view
    
    Parameters:
    - banks: List of available banks
    """
    st.header("Business Outcome Analysis")
    st.write("Analyze how payment capabilities impact business outcomes")
    
    # Check if user has completed an assessment
    has_assessment = len(st.session_state.get('assessment_data', {})) > 0
    
    # Select mode - either existing bank or custom assessment
    options = ["Analyze Existing Bank"]
    if has_assessment:
        options.append("Analyze Your Assessment")
        default_mode = "Analyze Your Assessment"
    else:
        default_mode = "Analyze Existing Bank"
    
    analysis_mode = st.radio(
        "Select analysis mode:",
        options,
        index=options.index(default_mode)
    )
    
    if analysis_mode == "Analyze Existing Bank":
        # Bank selection
        selected_bank = render_bank_selection(banks)
        
        if not selected_bank:
            st.warning("Please select a bank to analyze")
            return
        
        # Load data
        banks_data, _ = load_data()
        
        if selected_bank in banks_data:
            bank_data = banks_data.get(selected_bank, {})
            
            # Convert stage scores to process scores (simplified mapping)
            process_values = {}
            for stage_id in range(1, 13):
                # Get process data for stage
                stage_processes = get_process_data_for_stage(stage_id)
                score = bank_data[stage_id]
                
                # Assign the stage score to all processes in the stage
                for process in stage_processes:
                    process_values[process['qid']] = score
            
            # For comparison analysis
            selected_entity = selected_bank
        else:
            st.error(f"Data for {selected_bank} not found")
            return
    else:  # Analyze Your Assessment
        if not st.session_state.assessment_data:
            st.warning("You need to complete an assessment first. Go to the Assessment Tool to evaluate your capabilities.")
            return
        
        # Use assessment data directly
        process_values = st.session_state.assessment_data
        selected_entity = "Your Assessment"
    
    # Generate business outcome data
    outcome_data = create_outcome_radar_data(process_values)
    
    # Create radar chart for outcomes
    outcome_fig = create_outcome_chart(outcome_data)
    st.plotly_chart(outcome_fig, use_container_width=True)
    
    # Benchmark comparison
    banks_data, _ = load_data()
    
    # Allow selecting benchmark banks for outcome comparison
    st.subheader("Benchmark Comparison")
    benchmark_banks = st.multiselect(
        "Select banks for benchmark comparison:",
        options=banks,
        default=["JPMC (Global)"] if banks else []
    )
    
    if benchmark_banks:
        # Create comparison data
        comparison_data = {}
        
        # Add current entity data
        entity_outcomes = {outcome["Outcome"]: outcome["Score"] for outcome in outcome_data}
        comparison_data[selected_entity] = entity_outcomes
        
        # Add benchmark data
        for bank in benchmark_banks:
            if bank in banks_data:
                bank_process_values = {}
                for stage_id in range(1, 13):
                    # Get process data for stage
                    stage_processes = get_process_data_for_stage(stage_id)
                    score = banks_data[bank][stage_id]
                    
                    # Assign the stage score to all processes in the stage
                    for process in stage_processes:
                        bank_process_values[process['qid']] = score
                
                # Calculate outcomes for this bank
                bank_outcomes = create_outcome_radar_data(bank_process_values)
                bank_outcome_dict = {outcome["Outcome"]: outcome["Score"] for outcome in bank_outcomes}
                comparison_data[bank] = bank_outcome_dict
        
        # Create comparison table
        outcomes = get_business_outcomes()
        comparison_rows = []
        
        for outcome in outcomes:
            row = {"Business Outcome": outcome}
            for entity, entity_data in comparison_data.items():
                row[entity] = entity_data.get(outcome, 0)
            comparison_rows.append(row)
        
        comparison_df = pd.DataFrame(comparison_rows)
        st.dataframe(comparison_df, use_container_width=True)
    
    # Display detailed outcome analysis
    st.subheader("Business Outcome Details")
    
    # Create dataframe for outcomes
    outcome_df = pd.DataFrame(outcome_data).sort_values(by="Score", ascending=False)
    
    st.dataframe(outcome_df, use_container_width=True)
    
    # Show detailed breakdown for each outcome
    selected_outcome = st.selectbox(
        "Select an outcome for detailed analysis:",
        options=get_business_outcomes()
    )
    
    if selected_outcome:
        st.subheader(f"Detailed Analysis: {selected_outcome}")
        
        # Get process details for this outcome
        process_details = get_outcome_process_details(
            process_values,
            {p['qid']: p['process'] for p in load_process_details()},
            selected_outcome
        )
        
        # Create dataframe for process details
        process_df = pd.DataFrame(process_details).sort_values(by="Score", ascending=False)
        
        st.dataframe(process_df, use_container_width=True)
        
        # Show insights
        score = calculate_outcome_score(process_values, selected_outcome)
        
        st.metric(f"{selected_outcome} Score", f"{score:.2f}/4.00")
        
        # Provide recommendations based on score
        st.subheader("Insights & Recommendations")
        
        if score < 2.0:
            st.write(f"Your {selected_outcome} capability is below industry average. Focus on improving the lowest scoring processes first.")
        elif score < 3.0:
            st.write(f"Your {selected_outcome} capability is at industry average. To gain competitive advantage, invest in the processes that scored below 3.0.")
        else:
            st.write(f"Your {selected_outcome} capability is above industry average. Maintain your advantage by continuing to advance emerging capabilities.")
        
        # Show top processes to improve
        lowest_scoring = process_df.nsmallest(3, "Score")
        
        st.write("Top processes to improve:")
        for _, row in lowest_scoring.iterrows():
            st.write(f"- {row['ID']}: {row['Question']} (Score: {row['Score']})")

def render_targeted_outcome(process_data, banks):
    """
    Render the targeted outcome view by connecting assessment weaknesses with business outcomes
    
    Parameters:
    - process_data: Complete process data
    - banks: List of available banks
    """
    from data_loader import KPI_MATRIX
    from business_outcomes_mapper import get_business_outcomes, get_processes_for_outcome
    
    st.header("Targeted Outcome Analysis")
    st.write("Connect your weakest assessment areas with business outcomes to focus improvement efforts")
    
    # Check if user has completed an assessment
    has_assessment = len(st.session_state.get('assessment_data', {})) > 0
    
    if not has_assessment:
        st.warning("You need to complete an assessment first. Go to the Assessment Tool tab to evaluate your capabilities.")
        return
    
    # Get assessment data
    assessment_data = st.session_state.assessment_data
    
    # Calculate stage totals (sum of process scores)
    stage_names = get_stage_names()
    stage_averages = {}
    for stage_id in range(1, 13):
        # Get processes for this stage
        stage_processes = get_process_data_for_stage(stage_id)
        process_ids = [p['qid'] for p in stage_processes]
        
        # Calculate sum of scores for stage
        stage_scores = [assessment_data.get(pid, 0) for pid in process_ids if pid in assessment_data]
        if stage_scores:
            stage_sum = sum(stage_scores)
        else:
            stage_sum = 0
        
        # Each stage can have a maximum of 4 points (4 processes × 1.0 max score)
        stage_averages[stage_id] = {
            "name": stage_names[stage_id],
            "score": stage_sum,
            "max_score": 4.0  # Maximum possible score for any stage
        }
    
    # Get the weakest stages (lowest 3)
    weak_stages = sorted([(id, data) for id, data in stage_averages.items()], 
                        key=lambda x: x[1]["score"])[:3]
    
    # Select an outcome to target
    outcomes = get_business_outcomes()
    selected_outcome = st.selectbox(
        "Select a business outcome to target for improvement:",
        options=outcomes
    )
    
    # Get processes related to this outcome
    outcome_processes = get_processes_for_outcome(selected_outcome)
    
    # Find the intersection of weak stages and outcome processes
    targeted_processes = []
    
    for stage_id, stage_data in weak_stages:
        # Get processes for this stage
        stage_processes = get_process_data_for_stage(stage_id)
        
        # Filter for processes that belong to both this stage and the selected outcome
        for process in stage_processes:
            if process['qid'] in outcome_processes:
                score = assessment_data.get(process['qid'], 0)
                targeted_processes.append({
                    "id": process['qid'],
                    "stage": stage_data["name"],
                    "process": process['process'],
                    "description": process['description'],
                    "score": score
                })
    
    # Sort by score (lowest first)
    targeted_processes = sorted(targeted_processes, key=lambda x: x["score"])
    
    # Display results
    if targeted_processes:
        st.subheader(f"Priority Improvement Areas for {selected_outcome}")
        
        for i, process in enumerate(targeted_processes[:5]):  # Show top 5 improvement areas
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.metric(f"Process {process['id']}", f"{process['score']:.2f}/1.00")
                
                with col2:
                    st.markdown(f"**{process['process']}** - {process['stage']}")
                    st.write(process['description'])
                    
                    # Get KPI and PPE capability info
                    if process['id'] in KPI_MATRIX:
                        kpi_info = KPI_MATRIX[process['id']]
                        
                        st.markdown("##### Key Performance Indicators")
                        st.info(f"**KPI Metric:** {kpi_info['kpi']}")
                        
                        if kpi_info['ppe_cap']:
                            st.markdown("##### PPE Implementation Capability")
                            st.success(kpi_info['ppe_cap'])
                
                st.markdown("---")
    else:
        st.info(f"No specific processes found at the intersection of your weakest areas and {selected_outcome}. Try selecting a different outcome or complete more of your assessment.")
    
    # Strategy overview
    st.subheader("Strategic Improvement Approach")
    st.write("""
    1. **Focus on the high-priority processes listed above.** These represent the intersection of your weakest capabilities with the selected business outcome.
    2. **Track and monitor the listed KPIs** to measure improvement as you enhance these processes.
    3. **Consider the PPE implementation capabilities** as potential solutions to address the capability gaps.
    """)
    
    # Allow comparing with benchmark banks to see where they excel
    st.subheader("Benchmark Comparison")
    
    # Load benchmark data
    banks_data, _ = load_data()
    
    # Select banks for comparison
    benchmark_banks = st.multiselect(
        "Select banks to benchmark against:",
        options=banks,
        default=banks[:2] if len(banks) >= 2 else banks
    )
    
    if benchmark_banks:
        # Prepare comparison data
        comparison_data = []
        
        # Add benchmark data
        for process in targeted_processes[:5]:
            process_id = process['id']
            # Extract stage number
            stage_id = int(process_id[0]) if process_id[0].isdigit() else int(process_id[:2])
            
            row_data = {
                "Process ID": process_id,
                "Process": process['process'],
                "Your Score": process['score']
            }
            
            # Add bank scores
            for bank in benchmark_banks:
                if bank in banks_data:
                    # Use the stage score as proxy for process score
                    bank_score = banks_data[bank].get(stage_id, 0)
                    row_data[bank] = bank_score
            
            comparison_data.append(row_data)
        
        # Create comparison table
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True)
            
            # Provide insights
            st.markdown("### Insights")
            for bank in benchmark_banks:
                bank_scores = [row.get(bank, 0) for row in comparison_data]
                if bank_scores:
                    bank_avg = sum(bank_scores) / len(bank_scores)
                    st.write(f"**{bank}** averages **{bank_avg:.2f}/4.00** in these processes, " + 
                            f"{'significantly higher than your score' if bank_avg > 0.6 else 'comparable to your current capability'}.")
        else:
            st.warning("No comparison data available for the selected banks.")