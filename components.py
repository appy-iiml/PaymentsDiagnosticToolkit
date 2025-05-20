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
            # Map the decimal value to the closest maturity level
            if current_value < 0.17:  # Basic
                default_index = 0
            elif current_value < 0.50:  # Advanced
                default_index = 1
            elif current_value < 0.83:  # Leading
                default_index = 2
            else:  # Emerging
                default_index = 3
        else:
            default_index = 0
        
        selected_maturity = st.select_slider(
            f"Select maturity level for {process['process']}",
            options=maturity_options,
            value=maturity_options[default_index]
        )
        
        # Extract numeric value from selection
        maturity_label = selected_maturity.split("(")[0].strip()
        
        # Convert label to score value based on new scoring system
        if maturity_label == "Basic":
            maturity_value = 0.00
        elif maturity_label == "Advanced":
            maturity_value = 0.33
        elif maturity_label == "Leading":
            maturity_value = 0.66
        elif maturity_label == "Emerging":
            maturity_value = 1.00
        else:
            maturity_value = 0.00
        
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
    
    # Select banks to compare
    selected_banks = st.multiselect(
        "Select banks to compare:",
        options=all_options,
        default=all_options[:3] if len(all_options) >= 3 else all_options
    )
    
    if not selected_banks:
        st.warning("Please select at least two banks to compare")
        return
    
    # Show comparison
    tabs = st.tabs(["Radar Chart", "Heatmap", "Table View"])
    
    with tabs[0]:
        st.subheader("Capability Radar Comparison")
        radar_fig = create_radar_chart(combined_data, selected_banks)
        st.plotly_chart(radar_fig, use_container_width=True)
    
    with tabs[1]:
        st.subheader("Maturity Heatmap")
        heatmap_fig = create_maturity_heatmap(combined_data, selected_banks)
        st.plotly_chart(heatmap_fig, use_container_width=True)
    
    with tabs[2]:
        st.subheader("Detailed Score Comparison")
        
        # Create comparison table
        comparison_data = []
        stage_names = get_stage_names()
        
        for stage_id in range(1, 13):
            row_data = {
                "Stage": f"{stage_id}. {stage_names[stage_id]}"
            }
            
            for bank in selected_banks:
                if bank in combined_data:
                    row_data[bank] = combined_data[bank].get(stage_id, 0)
            
            comparison_data.append(row_data)
        
        # Add overall row
        overall_row = {"Stage": "Overall"}
        for bank in selected_banks:
            if bank in combined_data:
                overall_row[bank] = combined_data[bank].get("Overall", 0)
        
        comparison_data.append(overall_row)
        
        # Convert to DataFrame and display
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Calculate average scores for each bank
        if len(selected_banks) > 1:
            st.subheader("Summary Statistics")
            
            avg_scores = []
            for bank in selected_banks:
                if bank in combined_data:
                    avg_score = combined_data[bank].get("Overall", 0)
                    avg_scores.append({
                        "Bank": bank,
                        "Average Score": avg_score
                    })
            
            avg_df = pd.DataFrame(avg_scores).sort_values(by="Average Score", ascending=False)
            st.dataframe(avg_df, use_container_width=True)

def render_outcome_analysis(process_data, banks):
    """
    Render business outcome analysis view
    
    Parameters:
    - process_data: Complete process data
    - banks: List of available banks
    """
    st.header("Business Outcome Analysis & Improvement")
    st.write("Analyze how payment capabilities translate to business outcomes")
    
    # Determine if we should use assessment data or bank data
    use_assessment = False
    has_assessment = 'assessment_data' in st.session_state and st.session_state.assessment_data
    
    tabs = st.tabs(["Your Assessment", "Bank Analysis"])
    
    with tabs[0]:
        if has_assessment:
            st.subheader("Business Outcomes from Your Assessment")
            
            # Process assessment data
            process_values = st.session_state.assessment_data
            
            # Create mapping of process IDs to names
            process_names = {p['qid']: p['process'] for p in process_data}
            
            # Calculate business outcome scores
            outcome_data = create_outcome_radar_data(process_values)
            
            # Create radar chart
            radar_fig = create_outcome_chart(outcome_data)
            st.plotly_chart(radar_fig, use_container_width=True)
            
            # Show outcome details
            outcomes = get_business_outcomes()
            
            # Select specific outcome to analyze
            selected_outcome = st.selectbox(
                "Select a business outcome to analyze:",
                options=outcomes
            )
            
            # Show details for selected outcome
            st.subheader(f"Analysis: {selected_outcome}")
            
            # Calculate score for this outcome
            outcome_score = calculate_outcome_score(process_values, selected_outcome)
            st.metric(f"Score for {selected_outcome}", f"{outcome_score:.2f}/1.00")
            
            # Get process details for this outcome
            process_details = get_outcome_process_details(process_values, process_names, selected_outcome)
            
            # Display as table
            if process_details:
                st.subheader("Contributing Processes")
                
                # Create DataFrame for display
                details_df = pd.DataFrame(process_details)
                details_df = details_df.sort_values("Score", ascending=False)
                st.dataframe(details_df, use_container_width=True)
                
                # Identify improvement opportunities (processes with low scores)
                low_scores = [p for p in process_details if p["Score"] < 0.33]  # Basic level
                
                if low_scores:
                    st.subheader("Improvement Opportunities")
                    st.write("Focus on these areas to improve this business outcome:")
                    
                    for item in low_scores:
                        process_id = item["ID"]
                        process_info = next((p for p in process_data if p["qid"] == process_id), None)
                        
                        if process_info:
                            with st.expander(f"{process_id}. {process_info['process']} (Current: Basic)"):
                                st.write(process_info["description"])
                                
                                st.markdown("#### To move to Advanced level:")
                                st.write(process_info["advanced"])
                                
                                st.markdown("#### To move to Leading level:")
                                st.write(process_info["leading"])
                else:
                    st.success("Great job! All processes for this outcome are at Advanced level or above.")
            else:
                st.warning("No process data available for this outcome.")
        else:
            st.info("Complete the assessment first to see business outcome analysis.")
            
            if st.button("Go to Assessment"):
                st.session_state.current_view = "assessment"
                st.rerun()
    
    with tabs[1]:
        st.subheader("Bank Business Outcome Analysis")
        
        # Bank selection
        selected_bank = render_bank_selection(banks)
        
        if not selected_bank:
            st.warning("Please select a bank to analyze")
            return
        
        # Load bank data
        banks_data, _ = load_data()
        
        if selected_bank in banks_data:
            bank_scores = banks_data[selected_bank]
            
            # Convert bank scores to process scores format
            process_values = {}
            
            # Map stage scores to individual processes
            for stage_id, stage_score in bank_scores.items():
                if isinstance(stage_id, int):  # Skip "Overall" key
                    # Get processes for this stage
                    stage_processes = get_process_data_for_stage(stage_id)
                    process_count = len(stage_processes)
                    
                    if process_count > 0:
                        # Distribute stage score evenly across processes
                        process_score = stage_score / 4  # Normalize to 0-1 scale
                        
                        # Assign to each process
                        for process in stage_processes:
                            process_values[process['qid']] = process_score
            
            # Create mapping of process IDs to names
            process_names = {p['qid']: p['process'] for p in process_data}
            
            # Calculate business outcome scores
            outcome_data = create_outcome_radar_data(process_values)
            
            # Create radar chart
            radar_fig = create_outcome_chart(outcome_data)
            st.plotly_chart(radar_fig, use_container_width=True)
            
            # Show outcome summary
            outcome_summary = get_outcome_summary(process_values)
            
            # Convert to DataFrame and display
            summary_df = pd.DataFrame(outcome_summary).sort_values("Score", ascending=False)
            st.dataframe(summary_df, use_container_width=True)
            
            # Analysis of top and bottom outcomes
            if outcome_summary:
                # Find top outcome
                top_outcome = max(outcome_summary, key=lambda x: x["Score"])
                
                # Find bottom outcome
                bottom_outcome = min(outcome_summary, key=lambda x: x["Score"])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Strongest Outcome")
                    st.metric("Top Outcome", top_outcome["Outcome"])
                    st.metric("Score", f"{top_outcome['Score']:.2f}")
                    
                    # Get processes for top outcome
                    top_processes = get_processes_for_outcome(top_outcome["Outcome"])
                    if top_processes:
                        st.write("Key capabilities:")
                        for pid in top_processes[:3]:  # Show top 3
                            if pid in process_names:
                                st.write(f"- {pid}: {process_names[pid]}")
                
                with col2:
                    st.subheader("Area for Improvement")
                    st.metric("Bottom Outcome", bottom_outcome["Outcome"])
                    st.metric("Score", f"{bottom_outcome['Score']:.2f}")
                    
                    # Get processes for bottom outcome
                    bottom_processes = get_processes_for_outcome(bottom_outcome["Outcome"])
                    if bottom_processes:
                        st.write("Key improvement areas:")
                        for pid in bottom_processes[:3]:  # Show top 3
                            if pid in process_names:
                                st.write(f"- {pid}: {process_names[pid]}")
        else:
            st.warning(f"No data available for {selected_bank}")
