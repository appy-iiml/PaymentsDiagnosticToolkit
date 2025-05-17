import streamlit as st
import pandas as pd
from business_data import OPTION_DESCRIPTIONS, load_process_details
from business_outcomes_mapper import (
    get_business_outcomes,
    get_processes_for_outcome,
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
    # Check if current_stage is already set in session state
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 1
        
    # Use the current_stage from session state as the default index
    selected_stage = st.selectbox(
        "Select a stage to assess:",
        options=list(range(1, 13)),
        index=st.session_state.current_stage - 1,
        format_func=lambda x: f"Stage {x}: {stage_names[x]}"
    )
    
    # Update current_stage in session state when selectbox changes
    st.session_state.current_stage = selected_stage
    
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
            if st.button("Previous Stage", key="prev_stage_btn"):
                st.session_state.current_stage = selected_stage - 1
                st.rerun()
    
    with col3:
        if selected_stage < 12:
            if st.button("Next Stage", key="next_stage_btn"):
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
        st.session_state.assessment_overall_avg = overall_total / 12  # For radar chart comparison

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
    
    # Maturity heatmap
    st.subheader("Maturity Heatmap by Stage")
    
    # Create heatmap of selected banks
    heatmap_fig = create_maturity_heatmap(combined_data, selected_banks)
    st.plotly_chart(heatmap_fig, use_container_width=True)
    
    # Stage-by-stage comparison
    st.subheader("Stage-by-Stage Comparison")
    
    # Stage selection
    stage_names = get_stage_names()
    selected_stage = st.selectbox(
        "Select a stage to compare:",
        options=list(range(1, 13)),
        format_func=lambda x: f"Stage {x}: {stage_names[x]}"
    )
    
    # Create a bar chart for the selected stage across banks
    stage_data = {}
    for bank in selected_banks:
        if bank in combined_data:
            stage_data[bank] = combined_data[bank][selected_stage]
    
    # Create a dataframe for the stage comparison
    stage_df = pd.DataFrame({
        "Bank": list(stage_data.keys()),
        "Score": list(stage_data.values())
    })
    
    # Sort by score (descending)
    stage_df = stage_df.sort_values("Score", ascending=False)
    
    st.markdown(f"### Stage {selected_stage}: {stage_names[selected_stage]}")
    st.dataframe(stage_df, use_container_width=True)
    
    # Bar chart of stage comparison
    st.bar_chart(stage_df.set_index("Bank"))

def render_outcome_analysis(banks):
    """
    Render the business outcome analysis view
    
    Parameters:
    - banks: List of available banks
    """
    st.header("Business Outcome Analysis")
    st.write("Analyze how payment capabilities contribute to business outcomes")
    
    # Load data
    banks_data, _ = load_data()
    all_processes = load_process_details()
    
    # Create a mapping of process IDs to names for reference
    process_names = {p['qid']: p['process'] for p in all_processes}
    
    # Check if user has assessment data to include
    has_assessment = 'assessment_data' in st.session_state and st.session_state.assessment_data
    
    # Source selection (user assessment or bank benchmark)
    st.subheader("Analysis Source")
    
    analysis_source = "Bank Benchmark"
    if has_assessment:
        analysis_source = st.radio(
            "Select source for analysis:",
            ["Your Assessment", "Bank Benchmark"],
            horizontal=True
        )
    
    if analysis_source == "Your Assessment":
        if not st.session_state.assessment_data:
            st.warning("Please complete at least one stage of assessment first")
            return
        
        # Use the user's assessment data
        process_values = st.session_state.assessment_data
        source_name = "Your Assessment"
    else:
        # Select a bank for benchmark analysis
        selected_bank = render_bank_selection(banks)
        bank_data = get_bank_scores(selected_bank)
        
        if not bank_data:
            st.error(f"No data available for {selected_bank}")
            return
        
        # Convert bank stage scores to process scores
        # This is an approximation as we don't have actual process scores for banks
        process_values = {}
        for stage_id, stage_score in bank_data.items():
            if isinstance(stage_id, int):  # Skip the "Overall" key
                stage_processes = get_process_data_for_stage(stage_id)
                avg_process_score = stage_score / len(stage_processes) if stage_processes else 0
                
                for process in stage_processes:
                    process_values[process['qid']] = avg_process_score
        
        source_name = selected_bank
    
    # Generate outcome data
    outcome_data = create_outcome_radar_data(process_values)
    
    # Create radar chart for outcomes
    st.subheader(f"Business Outcome Analysis for {source_name}")
    
    outcome_fig = create_outcome_chart(outcome_data)
    st.plotly_chart(outcome_fig, use_container_width=True)
    
    # Show outcome scores in a table
    outcome_df = pd.DataFrame(outcome_data)
    outcome_df = outcome_df.sort_values("Score", ascending=False)
    
    st.dataframe(outcome_df, use_container_width=True)
    
    # Allow selecting an outcome for detailed analysis
    st.subheader("Detailed Outcome Analysis")
    selected_outcome = st.selectbox(
        "Select an outcome to analyze:",
        options=get_business_outcomes()
    )
    
    # Show the processes that contribute to this outcome
    outcome_processes = get_outcome_process_details(process_values, process_names, selected_outcome)
    
    st.markdown(f"### Processes Contributing to: {selected_outcome}")
    
    # Create a dataframe for the processes
    outcome_process_df = pd.DataFrame(outcome_processes)
    outcome_process_df = outcome_process_df.sort_values("Score", ascending=False)
    
    st.dataframe(outcome_process_df, use_container_width=True)
    
    # Show the average score for this outcome
    avg_score = calculate_outcome_score(process_values, selected_outcome)
    st.metric(f"Average Score for {selected_outcome}", f"{avg_score:.2f}/1.00")
    
    # Recommendations based on the outcome analysis
    st.subheader("Recommendations")
    
    # Find the processes with lowest scores to highlight improvement areas
    improvement_areas = sorted(outcome_processes, key=lambda x: x["Score"])[:3]
    
    st.markdown("### Top Areas for Improvement")
    
    for area in improvement_areas:
        st.markdown(f"#### {area['ID']}: {area['Question']}")
        st.write(f"Current Score: {area['Score']:.2f}")
        
        # Get the process description and maturity levels
        process_detail = next((p for p in all_processes if p['qid'] == area['ID']), None)
        
        if process_detail:
            st.write(f"**Description**: {process_detail['description']}")
            
            with st.expander("See improvement recommendations"):
                st.markdown("**Current Level**:")
                current_level = "Basic"
                next_level = "Advanced"
                
                if area['Score'] >= 0.33 and area['Score'] < 0.66:
                    current_level = "Advanced"
                    next_level = "Leading"
                elif area['Score'] >= 0.66 and area['Score'] < 1.0:
                    current_level = "Leading"
                    next_level = "Emerging"
                elif area['Score'] >= 1.0:
                    current_level = "Emerging"
                    next_level = "Already at top level"
                
                st.write(f"Your organization is currently at the **{current_level}** level.")
                
                if next_level != "Already at top level":
                    st.markdown(f"**Next Level ({next_level})**:")
                    st.write(process_detail[next_level.lower()])
                    st.markdown("**Recommended Actions**:")
                    st.write("1. Assess current capabilities and identify gaps")
                    st.write(f"2. Develop a roadmap to implement {next_level.lower()}-level capabilities")
                    st.write("3. Prioritize improvements based on business impact")
                else:
                    st.write("Congratulations! You're already at the highest maturity level for this process.")

def render_targeted_outcome(process_data, banks):
    """
    Render the targeted outcome view
    
    Parameters:
    - process_data: Complete process data
    - banks: List of available banks
    """
    st.header("Targeted Outcome Analysis")
    st.write("Identify which capabilities to improve to achieve specific business outcomes")
    
    # Get business outcomes
    outcomes = get_business_outcomes()
    
    # Select target outcome
    target_outcome = st.selectbox(
        "Select your priority business outcome:",
        options=outcomes
    )
    
    # Create a mapping of process IDs to names for reference
    process_names = {p['qid']: p['process'] for p in process_data}
    
    # Get processes for the selected outcome
    outcome_processes = get_processes_for_outcome(target_outcome)
    
    # Display the processes that contribute to this outcome
    st.subheader(f"Processes Contributing to {target_outcome}")
    
    # Create a table for the processes
    process_table = []
    for process_id in outcome_processes:
        process_info = next((p for p in process_data if p['qid'] == process_id), None)
        if process_info:
            process_table.append({
                "ID": process_id,
                "Process": process_info['process'],
                "Description": process_info['description'],
                "Stage": process_info['stage']
            })
    
    # Create a dataframe for the processes
    process_df = pd.DataFrame(process_table)
    
    # Allow sorting and filtering
    st.dataframe(process_df, use_container_width=True)
    
    # Load benchmark data
    banks_data, _ = load_data()
    
    # Check if user has assessment data to include
    has_assessment = 'assessment_data' in st.session_state and st.session_state.assessment_data
    
    # Option to include user's assessment in comparison
    include_assessment = False
    if has_assessment:
        include_assessment = st.checkbox("Include my assessment in comparison", value=True)
    
    # Select banks for comparison
    st.subheader("Compare Outcome Performance")
    
    if include_assessment:
        bank_options = ["Your Assessment"] + banks
    else:
        bank_options = banks
    
    selected_banks = st.multiselect(
        "Select banks for comparison:",
        options=bank_options,
        default=bank_options[:3] if len(bank_options) >= 3 else bank_options
    )
    
    if not selected_banks:
        st.warning("Please select at least one bank for comparison")
        return
    
    # Prepare data for comparison
    comparison_data = {}
    
    for bank in selected_banks:
        if bank == "Your Assessment":
            # Use user assessment data
            process_values = st.session_state.assessment_data
            avg_score = calculate_outcome_score(process_values, target_outcome)
            comparison_data[bank] = avg_score
        else:
            # Use bank benchmark data
            bank_data = banks_data.get(bank, {})
            
            # Convert bank stage scores to process scores (approximation)
            process_values = {}
            for stage_id, stage_score in bank_data.items():
                if isinstance(stage_id, int):  # Skip the "Overall" key
                    stage_processes = get_process_data_for_stage(stage_id)
                    avg_process_score = stage_score / len(stage_processes) if stage_processes else 0
                    
                    for process in stage_processes:
                        process_values[process['qid']] = avg_process_score
            
            avg_score = calculate_outcome_score(process_values, target_outcome)
            comparison_data[bank] = avg_score
    
    # Create bar chart for outcome comparison
    comparison_df = pd.DataFrame({
        "Bank": list(comparison_data.keys()),
        "Score": list(comparison_data.values())
    })
    
    # Sort by score (descending)
    comparison_df = comparison_df.sort_values("Score", ascending=False)
    
    st.bar_chart(comparison_df.set_index("Bank"))
    
    # Detailed gap analysis
    st.subheader("Gap Analysis & Improvement Plan")
    
    # If user's assessment is included, show gap analysis
    if include_assessment and "Your Assessment" in selected_banks:
        # Find the top-performing bank for this outcome
        top_bank = max([(bank, score) for bank, score in comparison_data.items() if bank != "Your Assessment"], 
                       key=lambda x: x[1], default=(None, 0))
        
        if top_bank[0]:
            st.markdown(f"### Gap Analysis vs. {top_bank[0]}")
            
            # Calculate the gap
            user_score = comparison_data.get("Your Assessment", 0)
            top_score = top_bank[1]
            gap = top_score - user_score
            
            # Show the gap
            st.metric("Outcome Performance Gap", f"{gap:.2f}")
            
            # Generate top 3 processes with largest gaps
            user_values = st.session_state.assessment_data
            
            # Get bank process values (approximation)
            bank_process_values = {}
            bank_data = banks_data.get(top_bank[0], {})
            
            for stage_id, stage_score in bank_data.items():
                if isinstance(stage_id, int):
                    stage_processes = get_process_data_for_stage(stage_id)
                    avg_process_score = stage_score / len(stage_processes) if stage_processes else 0
                    
                    for process in stage_processes:
                        bank_process_values[process['qid']] = avg_process_score
            
            # Calculate gaps for each process in the outcome
            process_gaps = []
            for process_id in outcome_processes:
                user_value = user_values.get(process_id, 0)
                bank_value = bank_process_values.get(process_id, 0)
                gap = bank_value - user_value
                
                process_info = next((p for p in process_data if p['qid'] == process_id), None)
                if process_info:
                    process_gaps.append({
                        "ID": process_id,
                        "Process": process_info['process'],
                        "Your Score": user_value,
                        "Top Score": bank_value,
                        "Gap": gap
                    })
            
            # Sort by gap (descending)
            process_gaps.sort(key=lambda x: x["Gap"], reverse=True)
            
            # Show the top 3 processes with largest gaps
            st.markdown("### Top Improvement Opportunities")
            
            for i, gap_info in enumerate(process_gaps[:3]):
                st.markdown(f"#### {i+1}. {gap_info['ID']}: {gap_info['Process']}")
                st.write(f"Your Score: {gap_info['Your Score']:.2f}")
                st.write(f"Top Performer Score: {gap_info['Top Score']:.2f}")
                st.write(f"Gap: {gap_info['Gap']:.2f}")
                
                # Get improvement advice
                process_detail = next((p for p in process_data if p['qid'] == gap_info['ID']), None)
                
                if process_detail:
                    with st.expander("Improvement Recommendations"):
                        # Determine current and next levels
                        current_level = "Basic"
                        next_level = "Advanced"
                        
                        if gap_info['Your Score'] >= 0.33 and gap_info['Your Score'] < 0.66:
                            current_level = "Advanced"
                            next_level = "Leading"
                        elif gap_info['Your Score'] >= 0.66 and gap_info['Your Score'] < 1.0:
                            current_level = "Leading"
                            next_level = "Emerging"
                        
                        st.markdown(f"**Current Level ({current_level})**:")
                        st.write(process_detail[current_level.lower()])
                        
                        st.markdown(f"**Target Level ({next_level})**:")
                        st.write(process_detail[next_level.lower()])
                        
                        st.markdown("**Implementation Approach**:")
                        st.write("1. Assess current state capabilities in detail")
                        st.write("2. Identify specific technology and process gaps")
                        st.write("3. Develop a phased implementation plan")
                        st.write("4. Prioritize quick wins for early business impact")
