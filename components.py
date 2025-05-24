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

def render_bank_outcome_analysis(banks):
    """
    Legacy function for bank outcome analysis only
    
    Parameters:
    - banks: List of available banks
    """
    st.header("Business Outcome Analysis")
    st.write("Analyze how payment capabilities contribute to specific business outcomes")
    
    # Load data
    banks_data, _ = load_data()
    
    # Get questions mapping
    process_data = load_process_details()
    questions = {p['qid']: p['process'] for p in process_data}
    
    # Create tabs for different analyses
    tab1, tab2 = st.tabs(["Your Assessment", "Bank Comparison"])
    
    with tab1:
        st.subheader("Your Assessment Outcomes")
        
        # Check if there's assessment data
        if 'assessment_data' not in st.session_state or not st.session_state.assessment_data:
            st.warning("No assessment data found. Please complete the assessment first.")
            return
        
        # Get outcome data
        outcome_data = create_outcome_radar_data(st.session_state.assessment_data)
        
        # Create outcome radar chart
        radar_fig = create_outcome_chart(outcome_data)
        st.plotly_chart(radar_fig, use_container_width=True)
        
        # Create outcome summary table
        summary = get_outcome_summary(st.session_state.assessment_data)
        summary_df = pd.DataFrame(summary)
        summary_df = summary_df.sort_values("Score", ascending=False)
        
        st.subheader("Business Outcome Summary")
        st.dataframe(summary_df, use_container_width=True)
        
        # Detailed analysis for a selected outcome
        st.subheader("Detailed Outcome Analysis")
        selected_outcome = st.selectbox(
            "Select a business outcome to analyze:",
            options=get_business_outcomes()
        )
        
        # Get processes for this outcome
        outcome_processes = get_outcome_process_details(
            st.session_state.assessment_data,
            questions,
            selected_outcome
        )
        
        # Calculate score
        outcome_score = calculate_outcome_score(st.session_state.assessment_data, selected_outcome)
        
        st.metric(
            label=f"Overall Score for {selected_outcome}",
            value=f"{outcome_score:.2f}"
        )
        
        # Create process breakdown table
        process_df = pd.DataFrame(outcome_processes)
        st.dataframe(process_df, use_container_width=True)
        
        # Recommendations based on score
        st.subheader("Recommendations")
        if outcome_score < 0.33:
            st.write("Your organization is at the Basic maturity level for this outcome. Consider the following improvements:")
            processes_to_improve = [p for p in outcome_processes if p["Score"] < 0.33]
            for p in processes_to_improve[:3]:  # Top 3 to improve
                st.markdown(f"- Improve **{p['Question']}** (currently at Basic level)")
        elif outcome_score < 0.66:
            st.write("Your organization is at the Advanced maturity level for this outcome. To reach Leading level, focus on:")
            processes_to_improve = [p for p in outcome_processes if p["Score"] < 0.66]
            for p in processes_to_improve[:3]:  # Top 3 to improve
                st.markdown(f"- Enhance **{p['Question']}** to reach Leading maturity")
        else:
            st.write("Your organization is at the Leading or Emerging maturity level for this outcome. To maintain leadership:")
            processes_to_improve = [p for p in outcome_processes if p["Score"] < 1.0]
            for p in processes_to_improve[:3]:  # Top 3 to improve
                st.markdown(f"- Consider innovating **{p['Question']}** to reach Emerging maturity")
    
    with tab2:
        st.subheader("Bank Outcome Comparison")
        
        # Bank selection for comparison
        selected_bank = st.selectbox(
            "Select a bank to analyze:",
            options=banks
        )
        
        # Get bank scores
        bank_scores = get_bank_scores(selected_bank)
        
        if not bank_scores:
            st.warning(f"No data available for {selected_bank}")
            return
        
        # Create process-to-score mapping
        process_values = {}
        for stage in range(1, 13):
            stage_processes = get_process_data_for_stage(stage)
            stage_score = bank_scores.get(stage, 0)
            
            # Distribute stage score across processes (simplified approach)
            for process in stage_processes:
                process_values[process['qid']] = stage_score / len(stage_processes)
        
        # Get outcome data
        outcome_data = create_outcome_radar_data(process_values)
        
        # Create outcome radar chart
        radar_fig = create_outcome_chart(outcome_data)
        st.plotly_chart(radar_fig, use_container_width=True)
        
        # Create outcome summary table
        summary = get_outcome_summary(process_values)
        summary_df = pd.DataFrame(summary)
        summary_df = summary_df.sort_values("Score", ascending=False)
        
        st.subheader(f"Business Outcome Summary for {selected_bank}")
        st.dataframe(summary_df, use_container_width=True)

def render_outcome_analysis(process_data, banks):
    """
    Render the holistic business outcome analysis and improvement view
    
    Parameters:
    - process_data: Process data dictionary
    - banks: List of available banks
    """
    st.header("Business Outcome Analysis & Improvement")
    st.write("Analyze and improve business outcomes with targeted process enhancements")
    
    # Load data
    banks_data, _ = load_data()
    from data_loader import KPI_MATRIX
    
    # Convert data from the Excel image to a structured format for PPE implementation data
    PPE_IMPLEMENTATION_DATA = {
        "1A": {"process": "Channel Access & Log-In", "lead_ppe": "Platform Modernization + Platform Adoption", "how_ppe_engages": "Platform to supply gateway, run change-management to move users over.", "technical_solution": "Omni-channel front-end + FIDO2 / OAuth CIAM"},
        "1B": {"process": "Payment Setup", "lead_ppe": "Agile Implementation + Platform Modernization", "how_ppe_engages": "Sprint team rewires set-up flow; integrate payee-lookup APIs.", "technical_solution": "Container autofill (Experian API, Form.io)"},
        "1C": {"process": "Data Entry & Input Validation", "lead_ppe": "Program Delivery", "how_ppe_engages": "Stand-up real-time validation micro-service.", "technical_solution": "IBAN+ / NPCI pump-drop API in CloudFlare Worker"},
        "1D": {"process": "Submission & Order Creation", "lead_ppe": "Program Delivery + Platform Modernization", "how_ppe_engages": "Deliver Kafka/Kinesis event bus with idempotency tokens.", "technical_solution": "Event-stream hub, exactly-once processing"},
        "2A": {"process": "Credential Verification", "lead_ppe": "Edge Consulting + Platform Modernization", "how_ppe_engages": "Design device-binding at edge (APIs / POS) and roll out biometrics.", "technical_solution": "NuData/Twilio SDK on edge/nodes"},
        "2B": {"process": "Multi-Factor / Risk MFA", "lead_ppe": "Platform Modernization", "how_ppe_engages": "Configure adaptive MFA engine, tune risk rules.", "technical_solution": "Transmit Security, Ping/Intelligence"},
        "2C": {"process": "Role / Limit Checks", "lead_ppe": "ServiceNow Consulting", "how_ppe_engages": "Low-code decision tables on ServiceNow; audits auto-logged.", "technical_solution": "Camunda DMN / ABAC in ServiceNow Flow"},
        "2D": {"process": "Session Context", "lead_ppe": "Platform Modernization", "how_ppe_engages": "Deploy JWT/OAuth via Istio; remove stateful stores.", "technical_solution": "IBM / Kong + Redis token cache"},
        "3A": {"process": "Rule Enforcement", "lead_ppe": "ServiceNow Consulting + Agile Implementation", "how_ppe_engages": "Build wired UX & BPA enrichment flows in Now Platform; iterative rollout.", "technical_solution": "UiPath bot, mandatory field wizard"},
        "3B": {"process": "Business Rule Compliance", "lead_ppe": "Regulated Agile-RAM + Platform Modernization", "how_ppe_engages": "Replace code rules with low-code engine; RAM gates ensure compliance.", "technical_solution": "Pega Decision Hub"},
        "3C": {"process": "Pre-AML Scan", "lead_ppe": "Program Delivery", "how_ppe_engages": "Integrate AI fuzzy-matching screen across all rails.", "technical_solution": "Silent Eight / ComplyAdvantage hub"},
        "3D": {"process": "Error Feedback", "lead_ppe": "Platform Modernization", "how_ppe_engages": "Wire cloud real-time BPA phase release with AutoScrum evidence.", "technical_solution": "Azure OpenAI + UiPath bot"},
        "4A": {"process": "Payment Classification", "lead_ppe": "Agile Implementation + Platform Modernization", "how_ppe_engages": "ML \"payment type\" model delivered by cross-functional squad.", "technical_solution": "SageMarker classifier, API gateway"},
        "4B": {"process": "Network Selection", "lead_ppe": "Platform Modernization", "how_ppe_engages": "Smart router with Redis A matrix; show CFO margin uplift.", "technical_solution": "Volante Smart Router"},
        "4C": {"process": "Routing Optimization", "lead_ppe": "Program Delivery", "how_ppe_engages": "Deliver real-time cut-off/fx optimizer; proven across ops & treasury.", "technical_solution": "TCS Quartz hub, liveFX feed"},
        "4D": {"process": "Handoff to Next Layer", "lead_ppe": "Regulated Agile-RAM", "how_ppe_engages": "Implement SX6 / choreography with risk gates.", "technical_solution": "Axoni Framework, NS/scrubBus"},
        "5A": {"process": "Risk Scoring (ML)", "lead_ppe": "Platform Modernization", "how_ppe_engages": "Deploy graph-ML risk engine, hook to case hub.", "technical_solution": "Feedzai / Neo4j"},
        "5B": {"process": "Sanctions Screening", "lead_ppe": "Program Delivery", "how_ppe_engages": "Integrate Quantexa network graph into screen flow.", "technical_solution": "Quantexa + SAS AML"},
        "5C": {"process": "AML Monitoring", "lead_ppe": "Platform Modernization", "how_ppe_engages": "Behavioral segmentation ML and risk thresholds.", "technical_solution": "NICE X-Sight"},
        "5D": {"process": "Case Handling", "lead_ppe": "ServiceNow Consulting", "how_ppe_engages": "Configure FS Ops case queues, SLAs & dashboards.", "technical_solution": "ServiceNow FS Operations"},
        "6A": {"process": "Transaction Confirmation", "lead_ppe": "Salesforce Consulting", "how_ppe_engages": "Rapid UX redesign + lightning; integrate payee-verify API.", "technical_solution": "Twilio Verify, custom Lightning cmp"},
        "6B": {"process": "Dual / Multi-Signatory", "lead_ppe": "MS Dynamics Consulting", "how_ppe_engages": "Add push-approval app, mobile biometrics.", "technical_solution": "ApproveitNow + Dynamics mobile app"},
        "6C": {"process": "Systemic Re-Check", "lead_ppe": "Platform Modernization", "how_ppe_engages": "Event API between core ledger & payment hub.", "technical_solution": "Finacle Event Hub / TM Vault API"},
        "6D": {"process": "Lock-in & Handover", "lead_ppe": "Regulated Agile-RAM", "how_ppe_engages": "Immutable state-machine on Kafka; RAM ensures auditability.", "technical_solution": "Confluent ledger stream"},
        "7A": {"process": "Message Generation", "lead_ppe": "Platform Modernization", "how_ppe_engages": "Containerized ISO mapper, CI/mapping tests.", "technical_solution": "SWIFT Translator / XMLdation in Docker"},
        "7B": {"process": "Data Enrichment", "lead_ppe": "Program Delivery", "how_ppe_engages": "Integrate GPI/SWIFT BIC APIs; cache & monitor SLAs.", "technical_solution": "Ref-data plug-in micro-service"},
        "7C": {"process": "Truncation Handling", "lead_ppe": "Platform Modernization", "how_ppe_engages": "Auto-split rules in route regression tests via AutoScrum.", "technical_solution": "MuleSoft transform set"},
        "7D": {"process": "Error / Repair Queue", "lead_ppe": "ServiceNow Consulting", "how_ppe_engages": "Queue & PX-bot integrate in Now; Live dashboards.", "technical_solution": "UiPath + ServiceNow Flow"},
        "8A": {"process": "Transmission / Network", "lead_ppe": "Platform Modernization", "how_ppe_engages": "Replace file-drop with MQ/API adapters; HA config.", "technical_solution": "IBM MQ on OpenShift"},
        "8B": {"process": "Queue & Processing", "lead_ppe": "Platform Modernization", "how_ppe_engages": "K8s HPA auto-scaling; stress-test via AutoScrum pipeline.", "technical_solution": "Kubernetes, AWS SQS"},
        "8C": {"process": "Monitoring & Confirmation", "lead_ppe": "Salesforce Consulting", "how_ppe_engages": "Track UETR / gpi options-status in Experience Cloud portal.", "technical_solution": "SWIFT gpi, GraphQL API"},
        "8D": {"process": "Clearing Completion", "lead_ppe": "Platform Modernization", "how_ppe_engages": "Webhook listener normalizes ACK to one event schema.", "technical_solution": "AWS EventBridge, Volante ACK svc"},
        "9A": {"process": "Debit/Credit Reserves", "lead_ppe": "Platform Modernization", "how_ppe_engages": "Real-time liquidity dashboard & auto-sweep rules.", "technical_solution": "Fusion+MLM, LCD dashboards"},
        "9B": {"process": "Beneficiary Credit", "lead_ppe": "Program Delivery + Platform Modernization", "how_ppe_engages": "Migrate to 24*7 posting core (Thought Machine/T24).", "technical_solution": "Cloud proxy ledger, APIs"},
        "9C": {"process": "Finality & Irrevocability", "lead_ppe": "Platform Adoption", "how_ppe_engages": "Treasury user training + AI cash-forecast rollout.", "technical_solution": "IOTR cash-forecast engine"},
        "9D": {"process": "Failure Handling", "lead_ppe": "(No native PPE)", "how_ppe_engages": "—", "technical_solution": "DLT / atomic settlement (Partior, Fnality)"},
        "10A": {"process": "Reconciliation", "lead_ppe": "ServiceNow Consulting", "how_ppe_engages": "Reconciliation app UI & Auto-match in Now; dashboards.", "technical_solution": "Duco/BlackLine + Now integration"},
        "10B": {"process": "Statement Updates", "lead_ppe": "MS Dynamics Consulting", "how_ppe_engages": "Event-driven statement micro-service + Dynamics doc gen.", "technical_solution": "Kafka + Dynamics 365"},
        "10C": {"process": "Exception Management", "lead_ppe": "ServiceNow Consulting", "how_ppe_engages": "Auto-return RPFI with e-sign; SLA times.", "technical_solution": "Pega BPM / Now Flow"},
        "10D": {"process": "Investigation & Dispute", "lead_ppe": "Salesforce Consulting", "how_ppe_engages": "Self-service gpi + Graph chart in Experience Cloud.", "technical_solution": "gpi API + Einstein GPT"},
        "11A": {"process": "Notifications", "lead_ppe": "Salesforce Consulting", "how_ppe_engages": "Omni-channel alert orchestrator (email/SMS/push).", "technical_solution": "Twilio Flex + Salesforce Service"},
        "11B": {"process": "Statement Generation", "lead_ppe": "MS Dynamics Consulting", "how_ppe_engages": "On-demand ISO camt API exposed via Dynamics portal.", "technical_solution": "Away API Mgr + Dynamics"},
        "11C": {"process": "Analytical Dashboards", "lead_ppe": "Platform Modernization", "how_ppe_engages": "Stream to Snowflake; real-time Tableau dashboards.", "technical_solution": "Kafka + Snowflake + Tableau"},
        "11D": {"process": "Status Tracking", "lead_ppe": "Salesforce Consulting", "how_ppe_engages": "GraphQL subscription API + client dashboards.", "technical_solution": "GraphQL + Lightning WebComp"},
        "12A": {"process": "Audit Trail Capture", "lead_ppe": "Platform Modernization", "how_ppe_engages": "Immutable QLDB ledger; auto-hash evidence.", "technical_solution": "AWS QLDB, Hyperledger"},
        "12B": {"process": "Long-Term Archival", "lead_ppe": "Program Delivery", "how_ppe_engages": "Cloud tiering strategy, cost governance.", "technical_solution": "AWS Glacier + Splunk Index"},
        "12C": {"process": "Regulatory Filings", "lead_ppe": "ServiceNow Consulting", "how_ppe_engages": "RegTech e-filing workflow & evidence store in Now.", "technical_solution": "AxoniSL gateway, Aurora"},
        "12D": {"process": "Compliance Reporting", "lead_ppe": "MS Dynamics Consulting", "how_ppe_engages": "Secure auditor portal with role-based data share.", "technical_solution": "Snowflake Secure Share + Dynamics"}
    }
    
    # Get questions mapping
    questions = {p['qid']: p['process'] for p in process_data}
    
    # Create tabs for different analyses
    tab1, tab2 = st.tabs(["Current Status", "Business Outcome Improvement"])
    
    with tab1:
        st.subheader("Your Business Outcome Performance")
        
        # Check if there's assessment data
        if 'assessment_data' not in st.session_state or not st.session_state.assessment_data:
            st.warning("No assessment data found. Please complete the assessment first.")
            return
        
        # Get outcome data
        outcome_data = create_outcome_radar_data(st.session_state.assessment_data)
        
        # Format all scores to 2 decimal places
        for item in outcome_data:
            item["Score"] = round(item["Score"], 2)
        
        # Create outcome radar chart
        radar_fig = create_outcome_chart(outcome_data)
        st.plotly_chart(radar_fig, use_container_width=True)
        
        # Create outcome summary table
        summary = get_outcome_summary(st.session_state.assessment_data)
        for item in summary:
            item["Score"] = round(item["Score"], 2)
        
        summary_df = pd.DataFrame(summary)
        summary_df = summary_df.sort_values("Score", ascending=False)
        
        st.subheader("Business Outcome Summary")
        st.dataframe(summary_df, use_container_width=True)
        
        # Detailed analysis for a selected outcome
        st.subheader("Detailed Outcome Analysis")
        selected_outcome = st.selectbox(
            "Select a business outcome to analyze:",
            options=get_business_outcomes(),
            key="outcome_analysis_select"
        )
        
        # Get processes for this outcome
        outcome_processes = get_outcome_process_details(
            st.session_state.assessment_data,
            questions,
            selected_outcome
        )
        
        # Format scores to 2 decimal places
        for process in outcome_processes:
            process["Score"] = round(process["Score"], 2)
        
        # Create dataframe for display
        outcome_df = pd.DataFrame(outcome_processes)
        st.dataframe(outcome_df, use_container_width=True)
    
    with tab2:
        # Improvement Planning section with Benchmark Comparison
        st.subheader("Outcome Improvement & Benchmarking")
        
        # Check if there's assessment data
        if 'assessment_data' not in st.session_state or not st.session_state.assessment_data:
            st.warning("No assessment data found. Please complete the assessment first.")
            return
        
        # Create columns for outcome selection and benchmark selection
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Select desired outcome
            selected_outcome = st.selectbox(
                "Select the business outcome you want to improve:",
                options=get_business_outcomes(),
                key="improvement_outcome_select"
            )
        
        with col2:
            # Select banks for comparison benchmark
            selected_banks = st.multiselect(
                "Select banks for benchmark comparison:",
                options=banks,
                default=banks[:2] if len(banks) >= 2 else banks
            )
        
        # Current score
        current_score = calculate_outcome_score(st.session_state.assessment_data, selected_outcome)
        current_score_rounded = round(current_score, 2)
        
        # Calculate benchmark average
        bank_scores = {}
        benchmark_avg = 0
        
        if selected_banks:
            banks_data, _ = load_data()
            
            for bank in selected_banks:
                bank_data = banks_data.get(bank, {})
                process_values = {}
                
                # Distribute stage scores across processes
                for stage in range(1, 13):
                    stage_processes = get_process_data_for_stage(stage)
                    stage_score = bank_data.get(stage, 0)
                    
                    for process in stage_processes:
                        process_values[process['qid']] = stage_score / len(stage_processes)
                
                # Calculate outcome score for this bank
                bank_score = calculate_outcome_score(process_values, selected_outcome)
                bank_scores[bank] = round(bank_score, 2)
            
            # Calculate average benchmark score
            if bank_scores:
                benchmark_avg = round(sum(bank_scores.values()) / len(bank_scores), 2)
        
        # Display current score and benchmark
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label=f"Your Current Score",
                value=f"{current_score_rounded:.2f}"
            )
        
        with col2:
            st.metric(
                label="Benchmark Average",
                value=f"{benchmark_avg:.2f}"
            )
        
        with col3:
            gap = benchmark_avg - current_score_rounded
            st.metric(
                label="Gap to Benchmark",
                value=f"{gap:.2f}",
                delta=f"{'-' if gap > 0 else '+'}{abs(gap*100):.1f}%" 
            )
        
        # Get processes for this outcome
        outcome_processes = get_processes_for_outcome(selected_outcome)
        
        # Process details for this outcome
        process_details = get_outcome_process_details(
            st.session_state.assessment_data,
            questions,
            selected_outcome
        )
        
        # Format scores to 2 decimal places
        for process in process_details:
            process["Score"] = round(process["Score"], 2)
        
        # Sort by score (ascending) to show lowest scoring processes first
        process_details = sorted(process_details, key=lambda x: x["Score"])
        
        # Technical Implementation section from Excel data
        st.subheader("Technical Implementation Opportunities")
        st.write("Based on your assessment, here are key processes that can be improved:")
        
        # Create a table of low-scoring processes with implementation details
        implementation_data = []
        
        for process in process_details[:5]:  # Focus on the top 5 improvement opportunities
            pid = process["ID"]
            if pid in PPE_IMPLEMENTATION_DATA:
                implementation_data.append({
                    "Process ID": pid,
                    "Process": questions.get(pid, "Unknown"),
                    "Current Score": process["Score"],
                    "Lead PPE Capability": PPE_IMPLEMENTATION_DATA[pid]["lead_ppe"],
                    "Technical Solution": PPE_IMPLEMENTATION_DATA[pid]["technical_solution"],
                    "How PPE Engages": PPE_IMPLEMENTATION_DATA[pid]["how_ppe_engages"]
                })
        
        if implementation_data:
            implementation_df = pd.DataFrame(implementation_data)
            st.dataframe(implementation_df, use_container_width=True)
        
        # Improvement simulation
        st.subheader("Improvement Simulation")
        st.write("Use the sliders below to simulate improvements to specific processes and see the impact on the overall outcome score.")
        
        # Copy current assessment data for simulation
        simulation_data = st.session_state.assessment_data.copy()
        
        # Show sliders for each process (limit to top 5 lowest scoring for simplicity)
        for process in process_details[:5]:
            pid = process["ID"]
            current_value = process["Score"]
            
            # Map score to maturity level for display
            if current_value <= 0:
                maturity_level = "Basic"
            elif current_value <= 0.33:
                maturity_level = "Advanced"
            elif current_value <= 0.66:
                maturity_level = "Leading"
            else:
                maturity_level = "Emerging"
            
            # Slider for improvement simulation
            maturity_options = ["Basic", "Advanced", "Leading", "Emerging"]
            current_index = maturity_options.index(maturity_level)
            
            new_maturity = st.select_slider(
                f"Improve {questions.get(pid, pid)}",
                options=maturity_options,
                value=maturity_level
            )
            
            # Convert maturity level to score
            if new_maturity == "Basic":
                new_value = 0
            elif new_maturity == "Advanced":
                new_value = 0.33
            elif new_maturity == "Leading":
                new_value = 0.66
            else:  # Emerging
                new_value = 1.0
            
            # Update simulation data
            simulation_data[pid] = new_value
        
        # Calculate new score
        new_score = calculate_outcome_score(simulation_data, selected_outcome)
        new_score_rounded = round(new_score, 2)
        
        # Display improvement impact with benchmark comparison
        st.subheader("Improvement Impact Analysis")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Current Score",
                value=f"{current_score_rounded:.2f}"
            )
        
        with col2:
            st.metric(
                label="Simulated Score",
                value=f"{new_score_rounded:.2f}"
            )
        
        with col3:
            improvement = new_score_rounded - current_score_rounded
            st.metric(
                label="Improvement",
                value=f"+{improvement:.2f}",
                delta=f"{improvement*100:.1f}%"
            )
        
        with col4:
            new_gap = benchmark_avg - new_score_rounded
            st.metric(
                label="New Gap to Benchmark",
                value=f"{new_gap:.2f}",
                delta=f"{'-' if new_gap < gap else '+'}{abs(new_gap*100):.1f}%",
                delta_color="inverse"
            )
            
        # Save simulation data for benchmark comparison
        st.session_state.simulation_data = simulation_data
        st.session_state.last_simulated_outcome = selected_outcome
        
        # Create benchmark comparison chart with current and simulated scores
        import plotly.express as px
        
        comparison_data = {
            "Your Current": current_score_rounded,
            "Your Simulated": new_score_rounded
        }
        
        # Add benchmark banks to comparison
        comparison_data.update(bank_scores)
        
        # Create DataFrame for plotting
        comparison_df = pd.DataFrame({
            "Organization": list(comparison_data.keys()),
            "Score": list(comparison_data.values())
        })
        
        # Sort by score in descending order
        comparison_df = comparison_df.sort_values("Score", ascending=False)
        
        # Create bar chart
        fig = px.bar(
            comparison_df,
            x="Organization",
            y="Score",
            title=f"{selected_outcome} - Benchmark Comparison",
            color="Organization",
            color_discrete_map={
                "Your Current": "#9370DB",  # Medium purple for current
                "Your Simulated": "#663399"  # Rebecca purple for simulated
            }
        )
        
        fig.update_layout(yaxis_range=[0, 1])
        st.plotly_chart(fig, use_container_width=True)
        
        # Implementation Plan recommendations
        st.subheader("Implementation Plan Recommendations")
        st.write("To achieve the simulated improvements, consider implementing these key technical solutions:")
        
        for process in process_details[:3]:
            pid = process["ID"]
            if pid in PPE_IMPLEMENTATION_DATA:
                with st.expander(f"{pid}: {questions.get(pid, 'Process')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Technical Solution:**")
                        st.markdown(f"_{PPE_IMPLEMENTATION_DATA[pid]['technical_solution']}_")
                        st.markdown("**Lead PPE Capability:**")
                        st.markdown(f"_{PPE_IMPLEMENTATION_DATA[pid]['lead_ppe']}_")
                    
                    with col2:
                        st.markdown("**How PPE Team Engages:**")
                        st.markdown(f"_{PPE_IMPLEMENTATION_DATA[pid]['how_ppe_engages']}_")
                        
