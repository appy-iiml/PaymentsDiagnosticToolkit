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
    
    # Create tabs for different comparison methods
    tab1, tab2 = st.tabs(["📊 Standard Comparison", "🤖 AI Bank Assessment"])
    
    with tab2:
        from ai_assessment_agent import render_ai_assessment_tab
        render_ai_assessment_tab()
    
    with tab1:
        # Load data
        banks_data, _ = load_data()
        
        # Check if user has assessment data to include
        has_assessment = 'assessment_stage_scores' in st.session_state and st.session_state.assessment_stage_scores
        
        # Check if there are AI-assessed banks to include
        has_ai_banks = 'ai_banks_for_comparison' in st.session_state and st.session_state.ai_banks_for_comparison
        
        # Combine all available data sources
        combined_data = banks_data.copy()
        all_options = list(banks)
        
        # Add user's own assessment if available
        if has_assessment:
            include_assessment = st.checkbox("Include my assessment in comparison", value=True)
            if include_assessment:
                assessment_data = {
                    "Your Assessment": {
                        **st.session_state.assessment_stage_scores,
                        "Overall": st.session_state.assessment_overall_avg
                    }
                }
                combined_data.update(assessment_data)
                all_options = ["Your Assessment"] + all_options
        
        # Add AI-assessed banks if available
        if has_ai_banks:
            include_ai_banks = st.checkbox("Include AI-assessed banks", value=True)
            if include_ai_banks:
                ai_banks = st.session_state.ai_banks_for_comparison
                for ai_bank_name, ai_bank_data in ai_banks.items():
                    combined_data[f"🤖 {ai_bank_name}"] = ai_bank_data
                    all_options.append(f"🤖 {ai_bank_name}")
                
                st.info(f"✨ {len(ai_banks)} AI-assessed bank(s) available for comparison!")
    
    # Bank selection for comparison
    selected_banks = render_bank_selection(all_options, mode="multiple")
    
    if len(selected_banks) < 2:
        st.warning("Please select at least 2 banks for comparison")
        return
    
    # Create comparison visualizations
    st.subheader("Overall Capability Comparison")
    
    # Radar chart
    radar_fig = create_radar_chart(
        combined_data, 
        selected_banks, 
        "Bank Payment Capability Comparison"
    )
    st.plotly_chart(radar_fig, use_container_width=True)
    
    # Maturity heatmap
    st.subheader("Maturity Heatmap")
    heatmap_fig = create_maturity_heatmap(combined_data, selected_banks)
    st.plotly_chart(heatmap_fig, use_container_width=True)
    
    # Detailed comparison table
    st.subheader("Detailed Scores by Stage")
    
    stage_names = get_stage_names()
    comparison_data = []
    
    for bank in selected_banks:
        if bank in combined_data:
            bank_data = combined_data[bank]
            row = {"Bank": bank}
            for stage_id in range(1, 13):
                row[f"Stage {stage_id}"] = bank_data.get(stage_id, 0)
            row["Overall"] = bank_data.get("Overall", 0)
            comparison_data.append(row)
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True)
    
    # Performance insights
    st.subheader("Key Insights")
    
    if len(selected_banks) >= 2:
        # Find best performing bank overall
        best_bank = max(selected_banks, key=lambda x: combined_data[x].get("Overall", 0))
        best_score = combined_data[best_bank].get("Overall", 0)
        
        st.success(f"**Top Performer:** {best_bank} with overall score of {best_score:.2f}")
        
        # Find stage with highest variation
        stage_variances = {}
        for stage_id in range(1, 13):
            scores = [combined_data[bank].get(stage_id, 0) for bank in selected_banks if bank in combined_data]
            if scores:
                stage_variances[stage_id] = max(scores) - min(scores)
        
        if stage_variances:
            max_variance_stage = max(stage_variances, key=stage_variances.get)
            st.info(f"**Highest Variation:** Stage {max_variance_stage} ({stage_names[max_variance_stage]}) shows the largest capability gap between institutions")

def render_outcome_analysis(process_data, banks):
    """
    Render the business outcome analysis view
    
    Parameters:
    - process_data: Complete process data
    - banks: List of available banks
    """
    st.header("Business Outcome Analysis & Improvement")
    st.write("Analyze payment capabilities from a business outcome perspective and identify improvement opportunities")
    
    # Check if user has assessment data
    has_assessment = 'assessment_data' in st.session_state and st.session_state.assessment_data
    
    if not has_assessment:
        st.warning("⚠️ Please complete the assessment first to analyze business outcomes")
        if st.button("Go to Assessment"):
            st.session_state.current_tab = "Assessment Tool"
            st.rerun()
        return
    
    # Business outcome selection
    outcomes = get_business_outcomes()
    selected_outcome = st.selectbox(
        "Select a business outcome to analyze:",
        options=outcomes
    )
    
    # Calculate outcome score based on user's assessment
    outcome_score = calculate_outcome_score(st.session_state.assessment_data, selected_outcome)
    
    # Display outcome score
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(
            label=f"{selected_outcome} Score",
            value=f"{outcome_score:.2f}/1.00"
        )
        
        # Status indicator
        if outcome_score >= 0.75:
            st.success("Excellent capability")
        elif outcome_score >= 0.50:
            st.warning("Good capability with room for improvement")
        else:
            st.error("Significant improvement needed")
    
    with col2:
        # Process breakdown for this outcome
        process_names = {p['qid']: p['process'] for p in process_data}
        outcome_processes = get_processes_for_outcome(selected_outcome)
        
        st.subheader("Contributing Processes")
        process_details = []
        for pid in outcome_processes:
            if pid in st.session_state.assessment_data:
                process_details.append({
                    "Process ID": pid,
                    "Process Name": process_names.get(pid, "Unknown"),
                    "Score": st.session_state.assessment_data[pid]
                })
        
        if process_details:
            process_df = pd.DataFrame(process_details)
            st.dataframe(process_df, use_container_width=True)
    
    # Benchmark comparison for this outcome
    st.subheader("Benchmark Comparison")
    
    # Load bank data and calculate outcome scores for each bank
    banks_data, _ = load_data()
    
    # Convert bank stage scores to process scores (simplified mapping)
    bank_outcome_scores = {}
    for bank, stages in banks_data.items():
        # Create a simplified process mapping from stage scores
        bank_process_scores = {}
        for pid in outcome_processes:
            stage_id = int(pid[0]) if pid[0].isdigit() else 1
            bank_process_scores[pid] = stages.get(stage_id, 0) / 4.0  # Normalize to 0-1 scale
        
        bank_outcome_scores[bank] = calculate_outcome_score(bank_process_scores, selected_outcome)
    
    # Add user's score
    bank_outcome_scores["Your Assessment"] = outcome_score
    
    # Create comparison chart
    comparison_data = list(bank_outcome_scores.items())
    comparison_df = pd.DataFrame(comparison_data, columns=["Institution", "Score"])
    comparison_df = comparison_df.sort_values("Score", ascending=False)
    
    import plotly.express as px
    fig = px.bar(
        comparison_df, 
        x="Institution", 
        y="Score",
        title=f"{selected_outcome} - Benchmark Comparison",
        color="Score",
        color_continuous_scale="viridis"
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Overall business outcomes radar
    st.subheader("Complete Business Outcome Analysis")
    
    outcome_data = create_outcome_radar_data(st.session_state.assessment_data)
    outcome_chart = create_outcome_chart(outcome_data)
    st.plotly_chart(outcome_chart, use_container_width=True)
    
    # Improvement recommendations
    st.subheader("Improvement Recommendations")
    
    # Find lowest scoring processes for this outcome
    low_score_processes = []
    for pid in outcome_processes:
        if pid in st.session_state.assessment_data:
            score = st.session_state.assessment_data[pid]
            if score < 0.5:  # Below advanced level
                low_score_processes.append({
                    "Process ID": pid,
                    "Process Name": process_names.get(pid, "Unknown"),
                    "Score": score,
                    "Gap": 1.0 - score
                })
    
    if low_score_processes:
        st.warning("**Priority Areas for Improvement:**")
        
        # Sort by gap (largest improvement opportunity first)
        low_score_processes.sort(key=lambda x: x["Gap"], reverse=True)
        
        for i, process in enumerate(low_score_processes[:3]):  # Show top 3
            with st.expander(f"Priority {i+1}: {process['Process Name']} (Gap: {process['Gap']:.2f})"):
                st.write(f"**Current Score:** {process['Score']:.2f}/1.00")
                st.write(f"**Improvement Potential:** {process['Gap']:.2f} points")
                
                # Find the process details for recommendations
                process_detail = next((p for p in process_data if p['qid'] == process['Process ID']), None)
                if process_detail:
                    st.write("**Next Level Capabilities:**")
                    current_level = "basic" if process['Score'] < 0.17 else ("advanced" if process['Score'] < 0.50 else "leading")
                    next_level = "advanced" if current_level == "basic" else ("leading" if current_level == "advanced" else "emerging")
                    st.write(process_detail.get(next_level, "No details available"))
    else:
        st.success("🎉 Excellent performance! All processes for this outcome are at advanced level or above.")
    
    # Export functionality
    st.subheader("Export Analysis")
    
    if st.button("Generate Improvement Report"):
        # Create a comprehensive report
        report_data = {
            "Business Outcome": selected_outcome,
            "Current Score": outcome_score,
            "Benchmark Ranking": f"{list(comparison_df[comparison_df['Institution'] == 'Your Assessment'].index)[0] + 1} of {len(comparison_df)}",
            "Contributing Processes": len(outcome_processes),
            "Improvement Opportunities": len(low_score_processes)
        }
        
        st.json(report_data)
        st.success("Report generated! You can copy the JSON data above for further analysis.")
