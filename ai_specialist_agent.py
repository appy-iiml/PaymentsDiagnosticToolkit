import streamlit as st
import requests
import json
from business_data import load_process_details
from data_loader import load_data

def create_comprehensive_bank_profile(bank_name):
    """Create detailed bank profile for specialized assessment"""
    bank_profiles = {
        "JPMorgan Chase": {
            "market_position": "Global Tier 1 bank, largest US bank by assets ($3.7T)",
            "technology_focus": "Heavy investment in blockchain, AI, quantum computing research ($12B annual tech spend)",
            "payment_innovations": "JPM Coin, blockchain-based repo transactions, real-time payments leader",
            "regulatory_strength": "Exemplary compliance frameworks, extensive regulatory experience across 60+ countries",
            "geographic_reach": "Global presence with strong US, European, and Asian operations",
            "strengths": ["Real-time payments", "Cross-border capabilities", "Risk management", "Technology innovation"],
            "recent_initiatives": "Massive fintech investments, blockchain payments platform, AI fraud detection systems",
            "payment_volume": "Processes $6 trillion daily in wholesale payments",
            "technology_maturity": "Leading edge - custom blockchain solutions, proprietary AI models"
        },
        "DBS Bank": {
            "market_position": "Leading Southeast Asian bank, recognized digital transformation leader",
            "technology_focus": "API-first architecture, cloud-native solutions, AI/ML integration across all services",
            "payment_innovations": "DBS PayLah! (5M+ users), real-time cross-border payments, comprehensive digital wallet ecosystem",
            "regulatory_strength": "Strong regional compliance, multiple digital banking licenses across ASEAN",
            "geographic_reach": "Dominant ASEAN presence, growing regional cross-border payment capabilities",
            "strengths": ["Digital payments", "API integration", "Customer experience", "Regional payment expertise"],
            "recent_initiatives": "Open banking platform launch, cryptocurrency trading services, full digital transformation",
            "payment_volume": "Processes 90%+ of transactions digitally",
            "technology_maturity": "Digital-first - cloud-native architecture, extensive API ecosystem"
        },
        "HSBC": {
            "market_position": "Global bank with strong Asia-Pacific and UK presence ($2.9T assets)",
            "technology_focus": "Digital transformation initiative, cloud migration, AI implementation across operations",
            "payment_innovations": "HSBC Connect platform, trade finance digitization, enhanced cross-border payment solutions",
            "regulatory_strength": "Multi-jurisdictional compliance expertise across 40+ countries",
            "geographic_reach": "Extensive global network, particularly strong Asia-Europe payment corridor",
            "strengths": ["Cross-border payments", "Trade finance", "Multi-currency capabilities", "Global payment reach"],
            "recent_initiatives": "Digital trade platform, enhanced payment rails, sustainability finance integration",
            "payment_volume": "Handles 150+ currencies, $4 trillion annual trade finance",
            "technology_maturity": "Modernizing - legacy system transformation, API development"
        },
        "Wells Fargo": {
            "market_position": "Major US retail bank with strong commercial banking presence",
            "technology_focus": "Digital modernization programs, mobile-first initiatives, cloud migration",
            "payment_innovations": "Zelle integration, enhanced mobile payments, commercial payment solutions",
            "regulatory_strength": "Rebuilding compliance frameworks, enhanced risk management",
            "geographic_reach": "Strong US domestic presence, selective international operations",
            "strengths": ["Retail payments", "Commercial banking", "Risk management", "Customer relationships"],
            "recent_initiatives": "Digital platform modernization, enhanced mobile capabilities, compliance strengthening",
            "payment_volume": "Processes millions of retail transactions daily",
            "technology_maturity": "Modernizing - significant legacy system upgrades underway"
        },
        "Bank of America": {
            "market_position": "Second largest US bank by assets, extensive retail and commercial presence",
            "technology_focus": "AI-driven solutions, mobile technology leadership, digital transformation",
            "payment_innovations": "Erica AI assistant, Zelle leadership, comprehensive mobile payment suite",
            "regulatory_strength": "Strong compliance frameworks, extensive regulatory experience",
            "geographic_reach": "Dominant US presence, selective global commercial banking",
            "strengths": ["Mobile payments", "AI integration", "Customer analytics", "Retail banking technology"],
            "recent_initiatives": "AI-powered customer service, enhanced mobile features, sustainable finance",
            "payment_volume": "40+ million mobile users, billions in digital transactions",
            "technology_maturity": "Advanced - significant AI integration, modern mobile platforms"
        }
    }
    
    return bank_profiles.get(bank_name, {
        "market_position": "Regional or specialized financial institution",
        "technology_focus": "Digital transformation initiatives and modernization programs",
        "payment_innovations": "Standard digital payment capabilities and mobile solutions",
        "regulatory_strength": "Regional compliance frameworks and risk management",
        "geographic_reach": "Local or regional operations focus",
        "strengths": ["Customer service", "Local market knowledge", "Relationship banking"],
        "recent_initiatives": "Digital modernization programs and customer experience improvements",
        "payment_volume": "Regional transaction processing",
        "technology_maturity": "Developing - ongoing digital transformation efforts"
    })

def create_specialist_assessment_prompt(bank_name, process_info):
    """
    Create highly specialized assessment prompt with comprehensive context
    """
    benchmark_data = load_data()[0]  # Get benchmark data
    bank_profile = create_comprehensive_bank_profile(bank_name)
    
    # Enhanced stage context mapping
    stage_contexts = {
        "1": {
            "area": "Transaction Initiation & Customer Interface",
            "key_technologies": "Multi-factor authentication, biometrics, digital identity, mobile apps",
            "industry_trends": "Passwordless authentication, behavioral biometrics, AI-powered fraud prevention",
            "regulatory_focus": "PCI DSS, data privacy, customer authentication standards"
        },
        "2": {
            "area": "Real-time Authorization & Decision Making", 
            "key_technologies": "Real-time processing engines, ML risk models, account verification systems",
            "industry_trends": "Sub-second authorization, AI risk scoring, real-time balance checks",
            "regulatory_focus": "PSD2, open banking, account access regulations"
        },
        "3": {
            "area": "Fraud Detection & Risk Management",
            "key_technologies": "AI/ML models, behavioral analytics, pattern recognition, real-time monitoring", 
            "industry_trends": "Advanced AI models, consortium fraud data, behavioral biometrics",
            "regulatory_focus": "Fraud prevention standards, data sharing regulations, liability frameworks"
        },
        "4": {
            "area": "Payment Network Routing & Connectivity",
            "key_technologies": "API gateways, message transformation, network connectivity, routing logic",
            "industry_trends": "API-first architecture, real-time rails, intelligent routing optimization",
            "regulatory_focus": "Network interoperability, message standards, cross-border regulations"
        },
        "5": {
            "area": "AML & Compliance Screening",
            "key_technologies": "Sanctions screening, PEP databases, transaction monitoring, case management",
            "industry_trends": "AI-powered monitoring, natural language processing, automated case resolution", 
            "regulatory_focus": "AML/CFT, sanctions compliance, suspicious activity reporting"
        },
        "6": {
            "area": "Payment Execution & Processing",
            "key_technologies": "Payment engines, currency conversion, cross-border networks, settlement systems",
            "industry_trends": "Real-time payments, blockchain rails, central bank digital currencies",
            "regulatory_focus": "Payment service regulations, cross-border compliance, settlement finality"
        },
        "7": {
            "area": "Settlement & Clearing Operations",
            "key_technologies": "Clearing house integration, netting engines, settlement optimization, liquidity management",
            "industry_trends": "Instant settlement, blockchain clearing, liquidity optimization algorithms",
            "regulatory_focus": "Settlement finality, systemic risk, clearing house regulations"
        },
        "8": {
            "area": "Account Management & Posting",
            "key_technologies": "Core banking systems, real-time posting, balance management, transaction history",
            "industry_trends": "Real-time account updates, cloud-native cores, API-driven architecture",
            "regulatory_focus": "Account accuracy, audit trails, data retention requirements"
        },
        "9": {
            "area": "Reconciliation & Financial Control",
            "key_technologies": "Automated matching, exception handling, reporting systems, data analytics",
            "industry_trends": "AI-powered reconciliation, automated break resolution, real-time monitoring",
            "regulatory_focus": "Financial controls, audit requirements, operational risk management"
        },
        "10": {
            "area": "Exception Handling & Issue Resolution",
            "key_technologies": "Workflow management, case tracking, automated resolution, escalation systems",
            "industry_trends": "AI-powered triage, automated resolution, predictive issue detection",
            "regulatory_focus": "Operational resilience, customer protection, dispute resolution"
        },
        "11": {
            "area": "Reporting & Analytics",
            "key_technologies": "Data warehouses, BI tools, real-time dashboards, advanced analytics",
            "industry_trends": "Real-time analytics, AI insights, predictive monitoring, self-service BI",
            "regulatory_focus": "Regulatory reporting, data governance, management information"
        },
        "12": {
            "area": "Customer Service & Support",
            "key_technologies": "CRM systems, case management, chatbots, knowledge management",
            "industry_trends": "AI-powered support, omnichannel service, predictive customer service",
            "regulatory_focus": "Customer protection, complaint handling, service level agreements"
        }
    }
    
    # Extract stage number from process ID
    process_id = process_info.get('qid', '1.1')
    stage_num = process_id.split('.')[0] if '.' in process_id else process_id[0]
    stage_context = stage_contexts.get(stage_num, stage_contexts["1"])
    
    # Build comparative benchmark context
    benchmark_context = f"Industry Benchmark Analysis:\n"
    for bank, scores in benchmark_data.items():
        stage_score = scores.get(int(stage_num) if stage_num.isdigit() else 1, 0)
        maturity_level = "Emerging" if stage_score >= 3.5 else "Leading" if stage_score >= 2.5 else "Advanced" if stage_score >= 1.5 else "Basic"
        benchmark_context += f"• {bank}: {stage_score:.1f}/4.0 ({maturity_level} level)\n"
    
    prompt = f"""You are Dr. Sarah Mitchell, a globally recognized payment systems expert with 25+ years of experience. You've personally consulted for 200+ financial institutions worldwide, authored industry standards, and served on regulatory committees. Your assessments are considered the gold standard in the industry.

TARGET INSTITUTION: {bank_name}

INSTITUTIONAL INTELLIGENCE PROFILE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏛️  Market Position: {bank_profile['market_position']}
🔬  Technology Strategy: {bank_profile['technology_focus']}
💡  Payment Innovation Portfolio: {bank_profile['payment_innovations']}
⚖️  Regulatory Excellence: {bank_profile['regulatory_strength']}
🌍  Geographic Footprint: {bank_profile['geographic_reach']}
📊  Transaction Volume: {bank_profile['payment_volume']}
🚀  Technology Maturity: {bank_profile['technology_maturity']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ASSESSMENT DOMAIN: {stage_context['area']}
🔧 Core Technologies: {stage_context['key_technologies']}
📈 Industry Evolution: {stage_context['industry_trends']}
📋 Regulatory Landscape: {stage_context['regulatory_focus']}

SPECIFIC CAPABILITY EVALUATION:
"{process_info['question']}"

MATURITY FRAMEWORK (Select ONE option number):
1️⃣ BASIC (0.0 points): {process_info['basic']}
2️⃣ ADVANCED (0.33 points): {process_info['advanced']}
3️⃣ LEADING (0.66 points): {process_info['leading']}
4️⃣ EMERGING (1.0 points): {process_info['emerging']}

{benchmark_context}

EXPERT ASSESSMENT METHODOLOGY:
═══════════════════════════════════════════════════════════
As Dr. Mitchell, conduct your assessment using this rigorous framework:

🔍 EVIDENCE-BASED ANALYSIS:
• What specific evidence exists of {bank_name}'s capability in this area?
• How does their known technology infrastructure support this capability?
• What public announcements, partnerships, or case studies demonstrate this level?

🏆 COMPETITIVE POSITIONING:
• How does {bank_name} compare to the benchmark institutions in this specific area?
• What is their demonstrated track record vs. aspirational goals?
• Are they a follower, fast follower, or leader in this capability?

🎯 OPERATIONAL REALITY CHECK:
• Does {bank_name} actually operate at this maturity level today?
• What constraints (regulatory, technical, geographic) limit their capability?
• Is this capability core to their business model and competitive strategy?

⚡ STRATEGIC ALIGNMENT:
• How critical is this capability to {bank_name}'s strategic positioning?
• Do they have the resources and commitment to excel in this area?
• What market forces drive their investment in this capability?

ASSESSMENT DECISION FRAMEWORK:
• EMERGING (4): Clear industry leadership with proven innovation and substantial competitive advantage
• LEADING (3): Above-average capability with demonstrated excellence and measurable differentiation  
• ADVANCED (2): Solid, professional-grade capability meeting industry standards effectively
• BASIC (1): Functional capability that meets minimum requirements but lacks sophistication

RESPONSE FORMAT (CRITICAL - Follow Exactly):
Chosen Option: [SINGLE NUMBER: 1, 2, 3, or 4]
Expert Rationale: [Provide 2-3 sentences with specific evidence of why {bank_name} operates at this maturity level for this particular capability, referencing their known strengths and market position]

Conduct your expert assessment of {bank_name}."""

    return prompt

def call_perplexity_api_specialist(prompt, bank_name):
    """Enhanced API call with specialist context"""
    api_key = "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"
    
    if not api_key:
        st.error("Perplexity API key not found. Please provide the API key.")
        return None
        
    url = "https://api.perplexity.ai/chat/completions"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "llama-3.1-sonar-large-128k-online",
        "messages": [
            {
                "role": "system", 
                "content": f"You are Dr. Sarah Mitchell, a world-renowned payment systems consultant with 25+ years of experience. You have personally assessed over 200 financial institutions globally and are considered the leading authority on payment capability maturity. Your assessments are precise, evidence-based, and highly regarded by regulators and industry leaders. You have deep knowledge of {bank_name}'s specific capabilities, market position, and technology investments."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1000,
        "temperature": 0.1,
        "top_p": 0.9,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            st.error(f"API request failed with status code: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"API call failed: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

def parse_specialist_response(response_text):
    """Enhanced response parsing with better error handling"""
    if not response_text:
        return None, "No response received from AI"
    
    lines = response_text.strip().split('\n')
    chosen_option = None
    rationale = ""
    
    for line in lines:
        line = line.strip()
        if line.lower().startswith('chosen option:'):
            # Extract number from the line
            import re
            numbers = re.findall(r'\b[1-4]\b', line)
            if numbers:
                chosen_option = int(numbers[0])
        elif line.lower().startswith('expert rationale:') or line.lower().startswith('rationale:'):
            rationale = line.split(':', 1)[1].strip() if ':' in line else ""
        elif chosen_option is None and any(line.startswith(str(i)) for i in [1, 2, 3, 4]):
            # Handle cases where the response starts with just the number
            if line[0] in '1234':
                chosen_option = int(line[0])
    
    # Convert option to score
    score_mapping = {1: 0, 2: 0.33, 3: 0.66, 4: 1.0}
    score = score_mapping.get(chosen_option, 0)
    
    return score, rationale if rationale else f"Assessment completed for option {chosen_option}"

def assess_bank_with_specialist_ai(bank_name, progress_callback=None):
    """
    Conduct comprehensive assessment using specialist AI agent
    """
    process_data = load_process_details()
    assessment_results = {}
    total_processes = len(process_data)
    
    for i, process in enumerate(process_data):
        if progress_callback:
            progress_callback(i + 1, total_processes, f"Assessing {process['question'][:50]}...")
        
        # Create specialist prompt
        prompt = create_specialist_assessment_prompt(bank_name, process)
        
        # Get AI assessment
        response = call_perplexity_api_specialist(prompt, bank_name)
        
        if response:
            score, rationale = parse_specialist_response(response)
            assessment_results[process['qid']] = {
                'score': score,
                'rationale': rationale,
                'question': process['question']
            }
        else:
            # Fallback with conservative scoring
            assessment_results[process['qid']] = {
                'score': 0.33,  # Default to Advanced level
                'rationale': f"Assessment unavailable - defaulted to Advanced level",
                'question': process['question']
            }
        
        # Brief pause to avoid rate limiting
        import time
        time.sleep(0.5)
    
    return assessment_results

def render_specialist_agent_tab():
    """
    Render enhanced AI specialist agent interface
    """
    st.header("🧠 AI Payment Systems Specialist")
    st.markdown("**Dr. Sarah Mitchell** - World-renowned payment systems consultant with 25+ years of experience")
    
    # Enhanced assessment interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Comprehensive Bank Assessment")
        
        # Bank selection with enhanced profiles
        available_banks = [
            "JPMorgan Chase", "DBS Bank", "HSBC", "Wells Fargo", 
            "Bank of America", "Citibank", "Goldman Sachs", "Morgan Stanley",
            "UBS", "Deutsche Bank", "ING", "Santander"
        ]
        
        selected_bank = st.selectbox(
            "Select Bank for Assessment:",
            available_banks,
            help="Choose a bank for comprehensive payment capability assessment"
        )
        
        # Assessment options
        assessment_type = st.radio(
            "Assessment Type:",
            ["Full Capability Assessment (48 processes)", "Quick Assessment (12 key processes)", "Custom Process Selection"],
            help="Choose the scope of your assessment"
        )
        
        if st.button("🚀 Start Specialist Assessment", type="primary"):
            if assessment_type == "Full Capability Assessment (48 processes)":
                with st.spinner(f"Dr. Mitchell is conducting comprehensive assessment of {selected_bank}..."):
                    # Create progress placeholder
                    progress_placeholder = st.empty()
                    status_placeholder = st.empty()
                    
                    def update_progress(current, total, current_task):
                        progress = current / total
                        progress_placeholder.progress(progress)
                        status_placeholder.text(f"Progress: {current}/{total} - {current_task}")
                    
                    # Run specialist assessment
                    results = assess_bank_with_specialist_ai(selected_bank, update_progress)
                    
                    # Store results in session state
                    st.session_state[f'specialist_assessment_{selected_bank}'] = results
                    
                    st.success(f"✅ Specialist assessment completed for {selected_bank}!")
                    st.balloons()
    
    with col2:
        st.subheader("Specialist Profile")
        st.markdown("""
        **Dr. Sarah Mitchell, Ph.D.**
        
        🎓 **Credentials:**
        - 25+ years payment systems expertise
        - Former Federal Reserve consultant
        - Author of payment industry standards
        - 200+ bank assessments completed
        
        🏆 **Specializations:**
        - Real-time payment systems
        - Cross-border payment architecture
        - Regulatory compliance frameworks
        - Digital transformation strategy
        
        🔬 **Assessment Methodology:**
        - Evidence-based capability evaluation
        - Competitive positioning analysis
        - Operational reality validation
        - Strategic alignment assessment
        """)
    
    # Display results if available
    if f'specialist_assessment_{selected_bank}' in st.session_state:
        st.subheader(f"Specialist Assessment Results: {selected_bank}")
        
        results = st.session_state[f'specialist_assessment_{selected_bank}']
        
        # Calculate overall score
        total_score = sum(result['score'] for result in results.values())
        max_possible = len(results) * 1.0
        overall_percentage = (total_score / max_possible) * 100
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Maturity", f"{overall_percentage:.1f}%")
        with col2:
            st.metric("Total Score", f"{total_score:.1f}/{max_possible:.0f}")
        with col3:
            maturity_level = "Emerging" if overall_percentage >= 75 else "Leading" if overall_percentage >= 50 else "Advanced" if overall_percentage >= 25 else "Basic"
            st.metric("Maturity Level", maturity_level)
        
        # Detailed results
        if st.expander("View Detailed Assessment Results"):
            for qid, result in results.items():
                score_color = "🔴" if result['score'] < 0.25 else "🟡" if result['score'] < 0.5 else "🟢" if result['score'] < 0.75 else "🚀"
                st.write(f"{score_color} **{qid}**: {result['question']}")
                st.write(f"   Score: {result['score']:.2f} | {result['rationale']}")
                st.write("---")

# Add to main app navigation if needed
if __name__ == "__main__":
    render_specialist_agent_tab()