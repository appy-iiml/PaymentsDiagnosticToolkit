import streamlit as st
import requests
import json
import time
from business_data import load_process_details, OPTION_DESCRIPTIONS
from data_loader import get_stage_names
import pandas as pd

# Perplexity API configuration
PERPLEXITY_API_KEY = "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"
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

def call_perplexity_api(prompt, bank_name):
    """
    Call Perplexity AI API to get assessment for a specific bank and process
    """
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "system",
                "content": "You are a payment systems expert analyzing bank capabilities. Provide accurate, research-based assessments based on publicly available information about the bank's payment processing capabilities."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 500,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            return "Unable to get assessment from AI"
            
    except requests.exceptions.RequestException as e:
        st.error(f"API call failed: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

def get_benchmark_data():
    """
    Get benchmark data from existing banks to guide AI assessment
    """
    from data_loader import load_data
    benchmark_data, _ = load_data()
    return benchmark_data

def create_assessment_prompt(bank_name, process_info):
    """
    Create a detailed prompt for assessing a specific payment process capability
    strictly following the questionnaire structure and scoring system
    """
    # Get benchmark data for reference
    benchmark_banks = get_benchmark_data()
    
    # Extract the stage from the process ID to map to benchmark data
    process_id = process_info['qid']
    stage_id = int(process_id[0])
    
    # Build benchmark reference text
    benchmark_text = "Reference benchmark data from industry leaders:\n"
    for bank, scores in benchmark_banks.items():
        if stage_id in scores:
            stage_score = scores[stage_id]
            if stage_score >= 3.0:
                maturity = "Leading to Emerging level"
            elif stage_score >= 2.0:
                maturity = "Advanced to Leading level"
            elif stage_score >= 1.0:
                maturity = "Basic to Advanced level"
            else:
                maturity = "Basic level"
            benchmark_text += f"- {bank}: {maturity} ({stage_score:.2f}/4.0 in this stage)\n"
    
    prompt = f"""
    You are a payment systems expert conducting a precise assessment of {bank_name}'s capabilities.

    **Assessment Question {process_info['qid']}**: {process_info['process']}
    **Process Description**: {process_info['description']}

    **SCORING SYSTEM (STRICT ADHERENCE REQUIRED):**
    - Basic = 0 points (Total stage score contribution: 0)
    - Advanced = 0.33 points (Total stage score contribution: 0.33)  
    - Leading = 0.66 points (Total stage score contribution: 0.66)
    - Emerging = 1 point (Total stage score contribution: 1.0)

    **MATURITY LEVEL OPTIONS (Choose EXACTLY ONE):**

    **Option 1 - Basic (0 points):**
    {process_info['basic']}

    **Option 2 - Advanced (0.33 points):**
    {process_info['advanced']}

    **Option 3 - Leading (0.66 points):**
    {process_info['leading']}

    **Option 4 - Emerging (1.0 points):**
    {process_info['emerging']}

    {benchmark_text}

    **ASSESSMENT INSTRUCTIONS:**
    1. Research {bank_name}'s actual capabilities in this specific area
    2. Compare their documented features/capabilities against the 4 option descriptions above
    3. Select the option that BEST MATCHES their current documented capabilities
    4. Consider their market position relative to the benchmark banks shown above
    5. Be conservative - only choose higher levels if there's clear evidence

    **RESPONSE FORMAT (REQUIRED):**
    [OPTION_NUMBER]: [Brief factual justification]

    Examples:
    - "Option 2: Bank has automated workflows but lacks AI integration"
    - "Option 3: Documented real-time processing with ML fraud detection"

    Respond with ONLY the option number (1, 2, 3, or 4) and brief justification.
    """
    
    return prompt

def parse_ai_response(response_text):
    """
    Parse the AI response to extract option number and convert to score
    Following the strict questionnaire scoring system
    """
    if not response_text:
        return 0.0, "No response received"
    
    response_text = response_text.strip()
    
    # Extract option number from response
    option_number = 1  # Default to Basic
    justification = response_text
    
    if ":" in response_text:
        parts = response_text.split(":", 1)
        option_part = parts[0].strip().lower()
        justification = parts[1].strip() if len(parts) > 1 else response_text
        
        # Extract option number
        if "option 4" in option_part or "4" in option_part:
            option_number = 4
        elif "option 3" in option_part or "3" in option_part:
            option_number = 3
        elif "option 2" in option_part or "2" in option_part:
            option_number = 2
        else:
            option_number = 1
    else:
        # Try to find option in the text
        response_lower = response_text.lower()
        if "option 4" in response_lower or "emerging" in response_lower:
            option_number = 4
        elif "option 3" in response_lower or "leading" in response_lower:
            option_number = 3
        elif "option 2" in response_lower or "advanced" in response_lower:
            option_number = 2
        else:
            option_number = 1
    
    # Convert option number to score (strict questionnaire scoring)
    score_mapping = {
        1: 0.0,    # Basic
        2: 0.33,   # Advanced
        3: 0.66,   # Leading
        4: 1.0     # Emerging
    }
    
    maturity_names = {
        1: "Basic",
        2: "Advanced", 
        3: "Leading",
        4: "Emerging"
    }
    
    score = score_mapping.get(option_number, 0.0)
    maturity_name = maturity_names.get(option_number, "Basic")
    
    return score, f"{maturity_name} (Option {option_number}): {justification}"

def assess_bank_with_ai(bank_name, progress_callback=None):
    """
    Assess all 48 processes for a specific bank using AI
    """
    process_data = load_process_details()
    assessment_results = {}
    detailed_justifications = {}
    
    total_processes = len(process_data)
    
    for i, process_info in enumerate(process_data):
        if progress_callback:
            progress_callback(i + 1, total_processes, f"Assessing {process_info['qid']}: {process_info['process']}")
        
        # Create prompt for this specific process
        prompt = create_assessment_prompt(bank_name, process_info)
        
        # Call Perplexity API
        ai_response = call_perplexity_api(prompt, bank_name)
        
        if ai_response:
            score, justification = parse_ai_response(ai_response)
            assessment_results[process_info['qid']] = score
            detailed_justifications[process_info['qid']] = justification
        else:
            # Fallback to basic level if API fails
            assessment_results[process_info['qid']] = 0.00
            detailed_justifications[process_info['qid']] = "Basic: Assessment failed, using default"
        
        # Small delay to respect API rate limits
        time.sleep(0.5)
    
    return assessment_results, detailed_justifications

def render_ai_assessment_tab():
    """
    Render the AI assessment interface
    """
    st.header("🤖 AI-Powered Bank Assessment")
    st.write("Let AI automatically assess payment capabilities for any bank by analyzing publicly available information")
    
    # Bank selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        bank_name = st.text_input(
            "Enter Bank Name for AI Assessment:",
            placeholder="e.g., Chase Bank, Wells Fargo, Bank of America, etc.",
            help="Enter the name of any bank you want to assess"
        )
    
    with col2:
        assess_button = st.button("🚀 Start AI Assessment", type="primary")
    
    if assess_button and bank_name:
        # Initialize session state for AI assessment
        if 'ai_assessment_data' not in st.session_state:
            st.session_state.ai_assessment_data = {}
        if 'ai_justifications' not in st.session_state:
            st.session_state.ai_justifications = {}
        
        st.info(f"🔍 Starting comprehensive AI assessment for {bank_name}...")
        st.write("This process will analyze all 48 payment processes using AI. Please wait...")
        
        # Create progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(current, total, current_task):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"Progress: {current}/{total} - {current_task}")
        
        # Run AI assessment
        try:
            assessment_results, justifications = assess_bank_with_ai(bank_name, update_progress)
            
            # Store results in session state
            st.session_state.ai_assessment_data[bank_name] = assessment_results
            st.session_state.ai_justifications[bank_name] = justifications
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            st.success(f"✅ AI assessment completed for {bank_name}!")
            
            # Show results summary
            total_score = sum(assessment_results.values())
            max_possible = len(assessment_results) * 1.0
            percentage = (total_score / max_possible) * 100 if max_possible > 0 else 0
            
            st.metric(
                label="Overall AI Assessment Score",
                value=f"{total_score:.2f}/{max_possible:.0f}",
                delta=f"{percentage:.1f}% maturity"
            )
            
        except Exception as e:
            st.error(f"Assessment failed: {str(e)}")
            return
    
    # Display previous AI assessments
    if 'ai_assessment_data' in st.session_state and st.session_state.ai_assessment_data:
        st.subheader("📊 AI Assessment Results")
        
        assessed_banks = list(st.session_state.ai_assessment_data.keys())
        selected_bank = st.selectbox(
            "Select bank to view detailed results:",
            options=assessed_banks
        )
        
        if selected_bank:
            display_ai_assessment_details(selected_bank)

def display_ai_assessment_details(bank_name):
    """
    Display detailed AI assessment results for a specific bank
    """
    if bank_name not in st.session_state.ai_assessment_data:
        st.warning("No assessment data found for this bank")
        return
    
    assessment_data = st.session_state.ai_assessment_data[bank_name]
    justifications = st.session_state.ai_justifications.get(bank_name, {})
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Summary by Stage", 
        "🔍 Detailed Results", 
        "📊 Comparison Ready",
        "💡 AI Insights"
    ])
    
    with tab1:
        st.subheader(f"Assessment Summary for {bank_name}")
        
        # Calculate scores by stage following questionnaire structure
        stage_names = get_stage_names()
        process_data = load_process_details()
        
        stage_scores = {}
        for stage_id in range(1, 13):
            stage_processes = [p for p in process_data if p['stage'].startswith(stage_names[stage_id])]
            # Sum of 4 process scores (each 0, 0.33, 0.66, or 1.0) = max 4.0 per stage
            stage_total = sum(assessment_data.get(p['qid'], 0) for p in stage_processes)
            stage_scores[stage_id] = stage_total
        
        # Create summary DataFrame
        summary_data = []
        for stage_id in range(1, 13):
            summary_data.append({
                "Stage": f"{stage_id}. {stage_names[stage_id]}",
                "Score": f"{stage_scores[stage_id]:.2f}/4.00",
                "Percentage": f"{(stage_scores[stage_id]/4.0)*100:.1f}%"
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
    
    with tab2:
        st.subheader("Detailed Process Assessments")
        
        # Group by stage for better organization
        process_data = load_process_details()
        stage_names = get_stage_names()
        
        for stage_id in range(1, 13):
            stage_processes = [p for p in process_data if p['stage'].startswith(stage_names[stage_id])]
            
            if stage_processes:
                with st.expander(f"Stage {stage_id}: {stage_names[stage_id]}"):
                    for process in stage_processes:
                        qid = process['qid']
                        score = assessment_data.get(qid, 0)
                        justification = justifications.get(qid, "No justification available")
                        
                        # Color code based on score
                        if score >= 0.66:
                            color = "🟢"
                        elif score >= 0.33:
                            color = "🟡"
                        else:
                            color = "🔴"
                        
                        st.write(f"{color} **{qid}. {process['process']}**")
                        st.write(f"Score: {score:.2f}/1.00")
                        st.write(f"AI Analysis: {justification}")
                        st.markdown("---")
    
    with tab3:
        st.subheader("Ready for Comparison")
        st.write("This AI-assessed bank is now ready to be compared with other banks in the comparison tool!")
        
        # Add to comparison button
        if st.button(f"Add {bank_name} to Comparison Tool"):
            # Store in the format expected by comparison tool
            if 'ai_banks_for_comparison' not in st.session_state:
                st.session_state.ai_banks_for_comparison = {}
            
            # Convert to stage-based scores for comparison
            stage_scores = {}
            process_data = load_process_details()
            stage_names = get_stage_names()
            
            # Get benchmark data to normalize scores
            benchmark_data = get_benchmark_data()
            benchmark_avg = {}
            
            # Calculate average benchmark scores per stage
            for stage_id in range(1, 13):
                stage_scores_list = [bank_data.get(stage_id, 0) for bank_data in benchmark_data.values()]
                if stage_scores_list:
                    benchmark_avg[stage_id] = sum(stage_scores_list) / len(stage_scores_list)
                else:
                    benchmark_avg[stage_id] = 0
            
            # Calculate scores following strict questionnaire structure
            # Each stage has exactly 4 processes, each scoring 0, 0.33, 0.66, or 1.0
            # Stage score = sum of all 4 process scores (max 4.0 per stage)
            for stage_id in range(1, 13):
                stage_processes = [p for p in process_data if p['stage'].startswith(stage_names[stage_id])]
                
                # Sum the individual process scores (already following 0, 0.33, 0.66, 1.0 scale)
                stage_total = sum(assessment_data.get(p['qid'], 0) for p in stage_processes)
                
                # Store the stage score directly (no normalization needed)
                # This matches the questionnaire structure: sum of 4 process scores
                stage_scores[stage_id] = stage_total
            
            # Calculate overall score for radar chart
            overall_score = sum(stage_scores.values()) / 12
            stage_scores["Overall"] = overall_score
            
            st.session_state.ai_banks_for_comparison[bank_name] = stage_scores
            
            st.success(f"✅ {bank_name} has been added to the comparison tool!")
            st.info("You can now go to the 'Bank Comparison' section to compare this AI-assessed bank with others.")
    
    with tab4:
        st.subheader("AI-Generated Insights")
        
        # Calculate some insights
        assessment_scores = list(assessment_data.values())
        avg_score = sum(assessment_scores) / len(assessment_scores) if assessment_scores else 0
        
        # Find strongest and weakest areas
        stage_scores = {}
        process_data = load_process_details()
        stage_names = get_stage_names()
        
        for stage_id in range(1, 13):
            stage_processes = [p for p in process_data if p['stage'].startswith(stage_names[stage_id])]
            if stage_processes:
                stage_avg = sum(assessment_data.get(p['qid'], 0) for p in stage_processes) / len(stage_processes)
                stage_scores[stage_id] = stage_avg
        
        if stage_scores:
            strongest_stage = max(stage_scores, key=stage_scores.get)
            weakest_stage = min(stage_scores, key=stage_scores.get)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "🏆 Strongest Area",
                    f"Stage {strongest_stage}",
                    f"{stage_scores[strongest_stage]:.2f}/1.0 avg"
                )
                st.write(stage_names[strongest_stage])
            
            with col2:
                st.metric(
                    "⚠️ Improvement Area", 
                    f"Stage {weakest_stage}",
                    f"{stage_scores[weakest_stage]:.2f}/1.0 avg"
                )
                st.write(stage_names[weakest_stage])
            
            st.write(f"**Overall Maturity Level**: {avg_score:.2f}/1.0 ({(avg_score*100):.1f}%)")
            
            # Maturity interpretation
            if avg_score >= 0.75:
                maturity_level = "🌟 Industry Leading"
                description = "This bank demonstrates cutting-edge payment capabilities"
            elif avg_score >= 0.50:
                maturity_level = "🚀 Advanced"
                description = "Strong payment infrastructure with modern capabilities"
            elif avg_score >= 0.25:
                maturity_level = "📈 Developing"
                description = "Solid foundation with room for technological advancement"
            else:
                maturity_level = "🔧 Basic"
                description = "Traditional approach with significant modernization opportunities"
            
            st.info(f"**{maturity_level}**: {description}")