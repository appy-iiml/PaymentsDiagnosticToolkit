import pandas as pd

# This file contains the data for business outcomes and maturity descriptions

# Define option descriptions
OPTION_DESCRIPTIONS = {
    "Basic": {
        "value": 0,
        "description": "Minimal functionality, often manual processes, requiring significant user effort and offering limited capabilities."
    },
    "Advanced": {
        "value": 0.33,
        "description": "Standard industry functionality with some automation and integration, providing reliable but not exceptional service."
    },
    "Leading": {
        "value": 0.66,
        "description": "Above average capabilities with significant automation, integration, and optimization, offering competitive advantage."
    },
    "Emerging": {
        "value": 1.0,
        "description": "Cutting-edge, innovative capabilities leveraging AI, machine learning, and advanced technologies to deliver exceptional service."
    }
}

# Convert process details into dataframe
def load_process_details():
    data = [
        # Stage 1: Payment Initiation & Data Capture
        {
            "qid": "1A", "stage": "Payment Initiation & Data Capture", 
            "process": "Channel Access & Log-In",
            "description": "Provides the customer or corporate user with secure entry points to initiate payments—mobile app, web portal, POS, wallet or ERP/TMS integration, bulk-file upload or APIs/host-to-host.",
            "basic": "• Multiple siloed channels with separate credentials (e.g. branch login, web login, mobile login).\n• No single-sign-on; users must reauthenticate per channel.\n• Slow password/PIN flows, little automation in session management.",
            "advanced": "• Centralized IAM with single-sign-on across channels.\n• Persistent sessions via secure cookies or device trust.\n• Basic adaptive MFA (e.g. step-up for high-value payments).",
            "leading": "• Fully unified CIAM platform: SSO, OAuth2/OIDC, device fingerprinting.\n• Contextual authentication (risk-based MFA triggered automatically).\n• API-first design so third-party apps (ERP, fintech partners) share the same login flow.",
            "emerging": "• Passwordless with behavioral biometrics.\n• AI-driven fraud prevention in login (behavioral biometrics, continuous authentication).\n• Decentralized identity (DID) using verifiable credentials for corporate users.",
        },
        {
            "qid": "1B", "stage": "Payment Initiation & Data Capture", 
            "process": "Payment Setup",
            "description": "The screen or API call where payer enters or uploads the payment details: retail single-payment UI or corporate bulk file (e.g. payroll).",
            "basic": "• Manual UI form for single payment with limited reuse of payees.\n• Corporate uses flat-file templates via SFTP.\n• No intelligent defaults; all fields must be typed.",
            "advanced": "• Pre-populated beneficiary lists, autocomplete of recurring payees.\n• Corporate B2B portal supports CSV/ISO 20022 XML upload with template validation.\n• \"Save as draft\" workflows for approval queues.",
            "leading": "• Guided UI with next-best-action suggestions (AI-driven) for payees/amounts.\n• Bulk template import via API, with dynamic loading of corporate ACH/RTGS parameters.\n• Auto-grouping of bulk payments by payee or category for faster entry.",
            "emerging": "• Conversational-UI or voice-driven payment setup.\n• Zero-touch invoice-to-pay: AI ingests PDF invoices, auto-creates payment batches.\n• Real-time integrations with ERP to auto-trigger payments on invoice receipt.",
        },
        {
            "qid": "1C", "stage": "Payment Initiation & Data Capture", 
            "process": "Data Entry & Input Validation",
            "description": "Ensures the data entered is syntactically & semantically correct—format checks (IBAN, BIC), mandatory fields, and optional real-time lookups (account status, card BIN).",
            "basic": "• Basic form validation with generic error messages.\n• Manual correction loops with full page refresh.\n• No contextual help or inline validation.",
            "advanced": "• Inline validation with field-specific error messages.\n• Format detection & normalization (e.g. auto-format card numbers).\n• Address verification against postal database.",
            "leading": "• Dynamic validation based on payment type & destination country.\n• Beneficiary name & account validation in real-time.\n• PAN/CVV validation against card BIN database.",
            "emerging": "• AI-powered predictive field completion & error correction.\n• Real-time IBAN lookup with beneficiary confirmation API.\n• ML anomaly detection to flag unusual payment characteristics.",
        },
        {
            "qid": "1D", "stage": "Payment Initiation & Data Capture", 
            "process": "Submission & Order Creation",
            "description": "Captures the completed payment order, creates the payment record, and hands off to downstream processing—confirms submission & provides reference number.",
            "basic": "• Batch processing with end-of-day execution.\n• No real-time feedback or status tracking.\n• Manual record creation & tracking.",
            "advanced": "• Real-time order creation with immediate confirmation.\n• Digital receipt with unique reference number.\n• Payment status tracking in customer portal.",
            "leading": "• Event streaming architecture with guaranteed order capture.\n• Multi-channel payment status notifications.\n• Payment history searchable by multiple parameters (date, amount, payee).",
            "emerging": "• Zero-latency distributed ledger recording.\n• Blockchain-based immutable payment record.\n• Full payment lifecycle visibility with real-time status changes.",
        },
        
        # Stage 2: Authentication & Identity Validation
        {
            "qid": "2A", "stage": "Authentication & Identity Validation", 
            "process": "Primary Authentication",
            "description": "Confirms the identity of the payment initiator through username/password challenge, biometrics, passkeys, or other credentials.",
            "basic": "• Simple username/password authentication.\n• No biometric options, only PIN/password.\n• Long session timeout requiring frequent re-auth.",
            "advanced": "• Industry-standard 2FA (SMS OTP, email links).\n• Basic biometric options (fingerprint, face).\n• Security questions for high-risk actions.",
            "leading": "• FIDO2/WebAuthn support with token-based auth.\n• Multiple biometric options on all channels.\n• Intelligent session management based on risk.",
            "emerging": "• Passwordless with passkeys for all channels.\n• Behavioral biometrics as primary auth factor.\n• Continuous authentication throughout payment journey.",
        },
        {
            "qid": "2B", "stage": "Authentication & Identity Validation", 
            "process": "Multi-Factor Authentication",
            "description": "Adds additional verification factors when required by transaction risk, compliance requirements, or to ensure non-repudiation.",
            "basic": "• SMS one-time codes as only second factor.\n• No risk-based MFA triggers.\n• Blanket approach requiring same MFA for all payments.",
            "advanced": "• App-based authenticator options.\n• Basic risk rules trigger step-up auth.\n• Configurable MFA thresholds based on amount.",
            "leading": "• Multiple authenticator options (TOTP, push notifications).\n• Out-of-band verification through multiple channels.\n• Context-aware adaptive authentication.",
            "emerging": "• Presence-based silent authentication.\n• Biometric MFA with liveness detection.\n• AI-driven continuous risk assessment.",
        },
        {
            "qid": "2C", "stage": "Authentication & Identity Validation", 
            "process": "Corporate Authorization",
            "description": "For business accounts, validates the initiator has proper entitlements, mandate & signing authority, and enforces payment limits by role & amount.",
            "basic": "• Static role-based access control.\n• Manual entitlement verification.\n• No integration with corporate hierarchy data.",
            "advanced": "• Automated limit checks during initiation.\n• Pre-defined approval workflows.\n• Role-based dashboards & controls.",
            "leading": "• Dynamic mandate checking against corporate structure.\n• Real-time signature verification against mandate database.\n• Complex approval matrix support (multiple approvers by criteria).",
            "emerging": "• Decentralized identity verification with VC/blockchain.\n• Algorithm-based smart approval routing.\n• Integration with corporate governance systems.",
        },
        {
            "qid": "2D", "stage": "Authentication & Identity Validation", 
            "process": "Session Security",
            "description": "Prevents session hijacking, maintains secure payment context, and protects the authenticated state from theft or replay attacks.",
            "basic": "• Basic cookie-based sessions.\n• Short timeouts with full re-auth required.\n• No detection of session anomalies.",
            "advanced": "• Encrypted session tokens with regular rotation.\n• Session binding to IP address.\n• Automatic logout on inactivity.",
            "leading": "• Advanced device fingerprinting.\n• Certificate pinning for mobile apps.\n• Session continuity across channels.",
            "emerging": "• Zero trust architecture with continuous validation.\n• Real-time risk scoring of session behaviors.\n• Quantum-resistant session cryptography.",
        },
        
        # Stage 3: Pre-Submission Validation
        {
            "qid": "3A", "stage": "Pre-Submission Validation", 
            "process": "Format & Completeness Checks",
            "description": "Validates all required fields are present, properly formatted, and meet the criteria for the specific payment type, channel, and destination.",
            "basic": "• Basic required field validation.\n• Generic error messages.\n• Limited format validation (length, character type).",
            "advanced": "• Payment-type specific validation rules.\n• Clear error identification with correction guidance.\n• Format standardization before submission.",
            "leading": "• Dynamic field requirements based on payment context.\n• Real-time field-level validation for all inputs.\n• Format transformation & normalization.",
            "emerging": "• AI-based predictive validation of complex fields.\n• Metadata enrichment from multiple sources.\n• Semantic validation of payment purpose.",
        },
        {
            "qid": "3B", "stage": "Pre-Submission Validation", 
            "process": "Business Rule Enforcement",
            "description": "Checks payment against business policies like daily limits, duplicate detection, allowed destinations, frequency caps, and balance requirements.",
            "basic": "• Static hard-coded business rules.\n• Basic duplicate payment detection.\n• Manual balance checks.",
            "advanced": "• Centralized rules engine with versioning.\n• Automated funds availability verification.\n• Real-time limit monitoring.",
            "leading": "• Dynamic rules triggered by contextual factors.\n• ML-based duplicate detection (fuzzy matching).\n• Cross-channel rule consistency.",
            "emerging": "• Self-optimizing rules based on payment patterns.\n• Predictive cash flow verification.\n• Natural language policy definition.",
        },
        {
            "qid": "3C", "stage": "Pre-Submission Validation", 
            "process": "Preliminary Compliance Screening",
            "description": "Performs initial screening of payment against sanctions lists, high-risk countries, and suspicious patterns before committing to the payment flow.",
            "basic": "• Basic screening against outdated sanctions lists.\n• No real-time screening during payment initiation.\n• Binary pass/fail with manual review process.",
            "advanced": "• Daily-updated screening lists.\n• Real-time initial screening during payment entry.\n• Name matching with fuzzy logic.",
            "leading": "• API-connected sanctions screening service.\n• Risk-based screening depth based on payment profile.\n• Automated resolution of common false positives.",
            "emerging": "• AI entity resolution for screening.\n• Real-time cross-border regulatory updates.\n• Graph analysis for network relationship screening.",
        },
        {
            "qid": "3D", "stage": "Pre-Submission Validation", 
            "process": "User Feedback & Correction",
            "description": "Communicates validation results back to the user with actionable guidance on how to correct issues, estimate processing times, and next steps.",
            "basic": "• Generic error messaging without specifics.\n• Whole-form validation with multiple refreshes.\n• No guided resolution path.",
            "advanced": "• Field-specific error messages with clear instructions.\n• Inline validation without page refresh.\n• Estimated processing times displayed.",
            "leading": "• Contextual help with examples of correct input.\n• Multi-language support for error messages.\n• Interactive correction guidance.",
            "emerging": "• AI assistant proposing specific corrections.\n• Voice/natural language error explanations.\n• Predictive guidance before errors occur.",
        },
        
        # Stage 4: Payment Orchestration & Routing
        {
            "qid": "4A", "stage": "Payment Orchestration & Routing", 
            "process": "Payment Classification",
            "description": "Categorizes the payment by type, urgency, value tier, and customer segment to determine optimal processing path.",
            "basic": "• Fixed payment types with manual classification.\n• No priority tiers or urgency coding.\n• Limited routing options.",
            "advanced": "• Automated classification by payment attributes.\n• Basic priority flagging (standard/high).\n• Customer segment routing rules.",
            "leading": "• Dynamic classification based on multiple attributes.\n• Multiple urgency/priority tiers with SLAs.\n• Value-based routing optimization.",
            "emerging": "• ML-based classification predicting optimal route.\n• Real-time adaptive classification by market conditions.\n• Context-aware priority determination.",
        },
        {
            "qid": "4B", "stage": "Payment Orchestration & Routing", 
            "process": "Network Selection",
            "description": "Determines the optimal payment rail/network based on destination, cost, speed, and other factors—SWIFT, ACH, RTP, SEPA, etc.",
            "basic": "• Limited network options (1-2 rails).\n• Manual network selection by user.\n• No optimization for cost or speed.",
            "advanced": "• Multiple network options for major corridors.\n• Basic routing rules based on destination/amount.\n• Fee transparency for network options.",
            "leading": "• Comprehensive network coverage globally.\n• Dynamic routing based on multiple parameters.\n• Real-time network status monitoring.",
            "emerging": "• AI-optimized network selection algorithms.\n• Multi-rail payment splitting for optimization.\n• Blockchain/alternative rail integration.",
        },
        {
            "qid": "4C", "stage": "Payment Orchestration & Routing", 
            "process": "Route Optimization",
            "description": "Applies intelligence to route selection considering cost, speed, FX rates, intermediary banks, compliance requirements, and SLAs.",
            "basic": "• Fixed routes with no optimization.\n• Manual routing table updates.\n• No consideration of cost or time variations.",
            "advanced": "• Basic cost vs. speed routing rules.\n• Daily FX rate considerations.\n• Corridor-specific default routes.",
            "leading": "• Multi-factor routing algorithms (cost, time, certainty).\n• Real-time FX rate optimization.\n• SLA-driven route selection.",
            "emerging": "• Self-optimizing AI routing decisions.\n• Real-time market condition adaptation.\n• Predictive analytics for optimal timing.",
        },
        {
            "qid": "4D", "stage": "Payment Orchestration & Routing", 
            "process": "Processing Handoff",
            "description": "Transfers the validated, classified payment to the appropriate processing system with all necessary metadata and handling instructions.",
            "basic": "• Batch file transfers with frequent failures.\n• Limited metadata accompanying transfers.\n• Manual recovery processes for failed handoffs.",
            "advanced": "• Real-time API payment handoffs.\n• Required metadata validation before transfer.\n• Automated retry mechanisms for failures.",
            "leading": "• Event-driven architecture with guaranteed delivery.\n• Rich metadata for downstream optimization.\n• Circuit breakers and failover routing.",
            "emerging": "• Distributed ledger with smart contract handoffs.\n• Self-healing error recovery mechanisms.\n• Predictive scaling based on volume patterns.",
        },
        
        # Stage 5: Risk, Fraud & Compliance
        {
            "qid": "5A", "stage": "Risk, Fraud & Compliance", 
            "process": "Transaction Risk Scoring",
            "description": "Evaluates the payment for fraud risk using rules, machine learning, behavioral analytics, and historical patterns.",
            "basic": "• Simple rule-based scoring with high false positives.\n• Manual review for all flagged transactions.\n• No behavioral or pattern analysis.",
            "advanced": "• Statistical models with multiple risk indicators.\n• Behavioral profiling for major red flags.\n• Customer segmentation in risk models.",
            "leading": "• Machine learning models with continuous training.\n• Real-time behavioral analytics across channels.\n• Network analysis for mule detection.",
            "emerging": "• Deep learning with explainable AI for risk decisions.\n• Cross-bank collaborative models (federated learning).\n• Predictive risk scoring with preventative actions.",
        },
        {
            "qid": "5B", "stage": "Risk, Fraud & Compliance", 
            "process": "Sanctions & Watchlist Screening",
            "description": "Checks payment parties against comprehensive sanctions lists, PEP databases, and internal watchlists with appropriate resolution workflows.",
            "basic": "• Limited sanctions list coverage.\n• Basic name matching with high false positives.\n• Manual review of all screening hits.",
            "advanced": "• Comprehensive global sanctions coverage.\n• Fuzzy matching with configurable thresholds.\n• Automated review workflow with audit trails.",
            "leading": "• Real-time list updates from multiple authorities.\n• Advanced entity resolution with contextual data.\n• Risk-based screening intensity.",
            "emerging": "• AI-powered entity resolution and network analysis.\n• Real-time cross-border regulatory awareness.\n• Natural language processing for narrative screening.",
        },
        {
            "qid": "5C", "stage": "Risk, Fraud & Compliance", 
            "process": "AML Monitoring",
            "description": "Applies anti-money laundering analytics to detect suspicious patterns, structuring, layering, and other financial crime indicators.",
            "basic": "• Simple threshold monitoring (e.g., CTR amounts).\n• Isolated payment analysis without context.\n• High volumes of false positive alerts.",
            "advanced": "• Rule-based scenario detection.\n• Customer risk-based monitoring intensity.\n• Historical activity analysis.",
            "leading": "• Behavioral analytics with network analysis.\n• Machine learning anomaly detection.\n• Cross-channel pattern recognition.",
            "emerging": "• Graph analytics for complex network detection.\n• Collective intelligence across institutions.\n• Predictive typology identification.",
        },
        {
            "qid": "5D", "stage": "Risk, Fraud & Compliance", 
            "process": "Case Management & Resolution",
            "description": "Manages the investigation workflow for flagged payments, with case assignment, evidence collection, decision recording, and audit trails.",
            "basic": "• Manual case management & tracking.\n• Email-based investigation workflows.\n• Limited documentation and audit trails.",
            "advanced": "• Dedicated case management system.\n• Structured investigation workflows.\n• Comprehensive evidence & decision recording.",
            "leading": "• Risk-based case prioritization.\n• Automated evidence gathering.\n• ML-assisted decision recommendations.",
            "emerging": "• AI-driven investigation with suggested resolutions.\n• Cross-institutional collaborative investigation.\n• Predictive resource allocation.",
        },
        
        # Stage 6: Final Authorisation & Approval
        {
            "qid": "6A", "stage": "Final Authorisation & Approval", 
            "process": "Payment Confirmation",
            "description": "Presents the user with final payment details, including fees, timing, and execution path, requesting explicit confirmation.",
            "basic": "• Basic confirmation screen with limited details.\n• No fee or timing information disclosed.\n• Single confirmation step for all payments.",
            "advanced": "• Detailed confirmation with fees and timing estimates.\n• Summary of payment details for verification.\n• Digital receipt with reference number.",
            "leading": "• Dynamic fee calculation with transparency.\n• Multi-option confirmation (timing vs cost tradeoffs).\n• Channel-consistent confirmation experience.",
            "emerging": "• Predictive delivery time with confidence scoring.\n• Dynamic pricing based on SLA requirements.\n• Augmented reality visualization of payment flow.",
        },
        {
            "qid": "6B", "stage": "Final Authorisation & Approval", 
            "process": "Multi-Party Approval",
            "description": "For payments requiring additional authorization, manages the approval workflow, notification, tracking, and execution.",
            "basic": "• Email notification for approvals.\n• No delegation or backup approver options.\n• Manual tracking of approval status.",
            "advanced": "• In-app/mobile notifications for approvers.\n• Basic approval workflows with SLAs.\n• Automatic escalation for delayed approvals.",
            "leading": "• Dynamic approval routing based on rules.\n• Multi-level approval matrices with contingencies.\n• Approver substitution and delegation.",
            "emerging": "• AI-optimized approval routing minimizing delays.\n• Biometric approval from any device.\n• Smart contract-based approval consensus.",
        },
        {
            "qid": "6C", "stage": "Final Authorisation & Approval", 
            "process": "Pre-Execution Verification",
            "description": "Conducts final systemic verification before execution, including any real-time changes in risk, compliance, or technical availability.",
            "basic": "• No systematic reverification before execution.\n• Long gap between approval and execution.\n• Manual pre-release checks.",
            "advanced": "• Basic re-verification of key risk factors.\n• Funds availability re-check at execution.\n• Automated technical readiness checks.",
            "leading": "• Comprehensive real-time reverification.\n• Up-to-the-minute compliance screening.\n• Dynamic risk re-assessment.",
            "emerging": "• Continuous verification throughout lifecycle.\n• Real-time market condition assessment.\n• Predictive execution-window optimization.",
        },
        {
            "qid": "6D", "stage": "Final Authorisation & Approval", 
            "process": "Execution Commitment",
            "description": "Records the final commitment to execute the payment, creating immutable audit record and handoff to the execution layer.",
            "basic": "• Simple database record of authorization.\n• Limited audit trails of approval.\n• Manual handoff to execution systems.",
            "advanced": "• Digital signature of approval actions.\n• Comprehensive approval audit trails.\n• Automated handoff to execution layer.",
            "leading": "• Cryptographic proof of authorization.\n• Tamper-evident approval records.\n• Guaranteed execution commitment.",
            "emerging": "• Blockchain-recorded authorization.\n• Zero-knowledge proof verification.\n• Smart contract execution triggers.",
        },
        
        # Stage 7: Message Generation & Transformation
        {
            "qid": "7A", "stage": "Message Generation & Transformation", 
            "process": "Message Formatting",
            "description": "Transforms the internal payment representation into the required message format for the target network (ISO 20022, MT, proprietary).",
            "basic": "• Limited message format support.\n• Hardcoded message templates.\n• Manual format selection.",
            "advanced": "• Support for major standard formats.\n• Template-based generation with validation.\n• Automated format selection by rail.",
            "leading": "• Comprehensive format library with versioning.\n• Dynamic message construction from components.\n• Format coexistence handling (MT/MX).",
            "emerging": "• AI-assisted message optimization.\n• Self-healing format correction.\n• Intelligent handling of format changes/updates.",
        },
        {
            "qid": "7B", "stage": "Message Generation & Transformation", 
            "process": "Data Enrichment",
            "description": "Adds required data elements not provided in the original payment, maps codes, and applies transformations required by the target network.",
            "basic": "• Minimal data enrichment capabilities.\n• Static code tables with manual updates.\n• Limited field transformations.",
            "advanced": "• Rule-based data enrichment.\n• Regular code table updates.\n• Standard field transformations for major networks.",
            "leading": "• API-based real-time data enrichment.\n• Intelligent code mapping with fallbacks.\n• Rich payment purpose classification.",
            "emerging": "• Machine learning data prediction/enrichment.\n• Self-updating code cross-references.\n• Semantic understanding of payment context.",
        },
        {
            "qid": "7C", "stage": "Message Generation & Transformation", 
            "process": "Field Handling & Truncation",
            "description": "Manages field length limitations, character set restrictions, and unmapped fields between different message formats.",
            "basic": "• Simple truncation without notification.\n• Character set errors requiring manual fixes.\n• Information loss during conversion.",
            "advanced": "• Rules-based intelligent truncation.\n• Character set translation for major alphabets.\n• Handling of unmapped fields in comments.",
            "leading": "• Context-aware field abbreviation.\n• Comprehensive character set handling.\n• Field splitting with semantic preservation.",
            "emerging": "• AI-optimized information preservation.\n• Natural language summarization for length limits.\n• Perfect information fidelity across formats.",
        },
        {
            "qid": "7D", "stage": "Message Generation & Transformation", 
            "process": "Validation & Error Handling",
            "description": "Ensures the generated message is valid, handles formatting errors, and manages the correction workflow for invalid messages.",
            "basic": "• Basic syntax validation only.\n• Manual error correction process.\n• No pre-validation before submission.",
            "advanced": "• Network-specific validation rules.\n• Automated error queues with notifications.\n• Standard error resolution workflows.",
            "leading": "• Pre-validation against network simulators.\n• Self-service error correction portal.\n• Automated correction of common errors.",
            "emerging": "• AI-based predictive error prevention.\n• Self-healing message correction.\n• Immediate feedback loops from networks.",
        },
        
        # Stage 8: Transmission, Clearing & ACK
        {
            "qid": "8A", "stage": "Transmission, Clearing & ACK", 
            "process": "Network Connectivity",
            "description": "Establishes and maintains secure, reliable connections to payment networks, including session management, encryption, and authentication.",
            "basic": "• Batch file exchange with limited hours.\n• FTP/SFTP with basic encryption.\n• Single network connection path.",
            "advanced": "• 24x7 connection with monitoring.\n• Industry-standard encryption protocols.\n• Automated session management.",
            "leading": "• Real-time API connectivity.\n• Multiple connection paths with failover.\n• Advanced encryption with perfect forward secrecy.",
            "emerging": "• Quantum-resistant encryption.\n• Self-healing network connections.\n• Adaptive connectivity optimization.",
        },
        {
            "qid": "8B", "stage": "Transmission, Clearing & ACK", 
            "process": "Message Queuing & Processing",
            "description": "Manages the flow of outgoing and incoming messages, including throttling, prioritization, retries, and exception handling.",
            "basic": "• Simple FIFO message queuing.\n• Limited capacity with batch processing.\n• Manual intervention for queue issues.",
            "advanced": "• Priority-based message queuing.\n• Automated retry mechanisms.\n• Queue monitoring with alerts.",
            "leading": "• Dynamic queue management by type/priority.\n• Guaranteed message delivery patterns.\n• Auto-scaling processing capacity.",
            "emerging": "• ML-optimized queue management.\n• Predictive capacity scaling.\n• Self-tuning processing parameters.",
        },
        {
            "qid": "8C", "stage": "Transmission, Clearing & ACK", 
            "process": "Correspondent & Intermediary Handling",
            "description": "Manages relationships with correspondent banks, nostro accounts, and intermediaries required for payment clearing and settlement.",
            "basic": "• Limited correspondent network.\n• Manual nostro reconciliation.\n• Static routing through intermediaries.",
            "advanced": "• Broad correspondent coverage.\n• Daily nostro position monitoring.\n• Relationship management dashboard.",
            "leading": "• Dynamic correspondent selection.\n• Real-time nostro monitoring & forecasting.\n• SLA monitoring across correspondents.",
            "emerging": "• AI-optimized correspondent selection.\n• Blockchain-based nostro-vostro management.\n• Real-time intermediary performance analysis.",
        },
        {
            "qid": "8D", "stage": "Transmission, Clearing & ACK", 
            "process": "Acknowledgment Handling",
            "description": "Processes network acknowledgments, positive/negative responses, and status updates, triggering appropriate actions based on message status.",
            "basic": "• Manual tracking of acknowledgments.\n• Delayed processing of status messages.\n• Limited visibility into clearing status.",
            "advanced": "• Automated acknowledgment processing.\n• Status updates reflected in customer channels.\n• Scheduled reconciliation of outstanding items.",
            "leading": "• Real-time ACK/NACK processing.\n• Event-driven status updates across channels.\n• Proactive notification of clearing issues.",
            "emerging": "• Predictive NACK resolution.\n• Machine learning for status interpretation.\n• End-to-end real-time tracking.",
        },
        
        # Stage 9: Settlement & Funds Movement
        {
            "qid": "9A", "stage": "Settlement & Funds Movement", 
            "process": "Settlement Initiation",
            "description": "Triggers the actual movement of funds between accounts, either in-house, through central bank, or correspondent banking networks.",
            "basic": "• End-of-day batch settlement cycles.\n• Manual settlement initiation.\n• Limited settlement methods.",
            "advanced": "• Multiple intraday settlement cycles.\n• Automated settlement triggering.\n• Support for major settlement mechanisms.",
            "leading": "• Near-real-time settlement initiation.\n• Dynamic settlement method selection.\n• Comprehensive audit trails.",
            "emerging": "• Continuous 24x7 real-time settlement.\n• Blockchain/DLT settlement capabilities.\n• Settlement method optimization.",
        },
        {
            "qid": "9B", "stage": "Settlement & Funds Movement", 
            "process": "Beneficiary Crediting",
            "description": "Completes the payment by crediting the beneficiary account, either internal or external, and confirming final delivery.",
            "basic": "• Next-day crediting for most payments.\n• No real-time credit confirmation.\n• Manual handling of credit failures.",
            "advanced": "• Same-day crediting for standard payments.\n• Status tracking of external credits.\n• Automated handling of credit exceptions.",
            "leading": "• Real-time crediting for supported networks.\n• Payment completion confirmation for all types.\n• SLA monitoring for credit timing.",
            "emerging": "• Instant global crediting capabilities.\n• Blockchain proof of credit completion.\n• Predictive credit timing by corridor.",
        },
        {
            "qid": "9C", "stage": "Settlement & Funds Movement", 
            "process": "Liquidity Management",
            "description": "Manages funding sources, liquidity positions, and optimizes the timing and routing of settlements to maximize efficiency.",
            "basic": "• Basic daily liquidity position reporting.\n• Manual funding of settlement accounts.\n• No intraday liquidity optimization.",
            "advanced": "• Intraday liquidity monitoring tools.\n• Scheduled funding of settlement accounts.\n• Basic threshold alerting.",
            "leading": "• Real-time liquidity dashboard & forecasting.\n• Dynamic funding allocation across accounts.\n• Payment flow reshaping for liquidity.",
            "emerging": "• ML-powered liquidity prediction engines.\n• Self-optimizing payment release algorithms.\n• Cross-currency liquidity optimization.",
        },
        {
            "qid": "9D", "stage": "Settlement & Funds Movement", 
            "process": "Finality & Irrevocability",
            "description": "Establishes the legal finality of payments, manages the irrevocability points, and handles any related disputes or recalls.",
            "basic": "• Unclear finality timeframes.\n• Paper-based payment recall process.\n• Manual dispute investigation.",
            "advanced": "• Documented finality policies by rail.\n• Structured recall/return workflows.\n• Digital dispute management.",
            "leading": "• Real-time finality status tracking.\n• API-based payment recall capabilities.\n• Automated funds repatriation for returns.",
            "emerging": "• Smart contract-enforced finality.\n• Immutable proof of settlement finality.\n• AI-assisted dispute resolution.",
        },
        
        # Stage 10: Reconciliation & Exceptions
        {
            "qid": "10A", "stage": "Reconciliation & Exceptions", 
            "process": "Transaction Reconciliation",
            "description": "Matches and reconciles payment records across systems, networks, and accounts to ensure completeness and accuracy.",
            "basic": "• Manual reconciliation processes.\n• Batch processing with T+1 visibility.\n• High exception rates requiring investigation.",
            "advanced": "• Automated matching algorithms.\n• Intraday reconciliation cycles.\n• Exception queues with workflow.",
            "leading": "• Real-time continuous reconciliation.\n• Machine learning match optimization.\n• Self-healing exception management.",
            "emerging": "• Blockchain-enabled perfect reconciliation.\n• Predictive exception prevention.\n• Autonomous reconciliation across networks.",
        },
        {
            "qid": "10B", "stage": "Reconciliation & Exceptions", 
            "process": "Account Posting & Statements",
            "description": "Updates customer accounts with finalized transactions and generates accurate, timely account statements and confirmations.",
            "basic": "• End-of-day batch posting.\n• Monthly paper statements only.\n• Limited transaction descriptions.",
            "advanced": "• Intraday posting cycles.\n• Electronic statement delivery options.\n• Enriched transaction descriptions.",
            "leading": "• Real-time posting to customer accounts.\n• Customizable statement formats & frequency.\n• Transaction categorization & tagging.",
            "emerging": "• Instant push notifications for all activity.\n• Interactive visual transaction history.\n• AI-enhanced transaction insights.",
        },
        {
            "qid": "10C", "stage": "Reconciliation & Exceptions", 
            "process": "Exception & Returns Handling",
            "description": "Manages payment exceptions like repairs, returns, cancellations, and recalls through defined workflows to resolution.",
            "basic": "• Manual exception handling processes.\n• Email/phone communication for issues.\n• Long resolution timeframes.",
            "advanced": "• Structured exception handling workflows.\n• Digital tracking of exceptions.\n• SLA monitoring for resolution times.",
            "leading": "• Automated resolution of common exceptions.\n• Customer self-service exception portal.\n• Real-time exception status visibility.",
            "emerging": "• AI-powered exception categorization & routing.\n• Predictive exception identification.\n• Autonomous resolution of standard cases.",
        },
        {
            "qid": "10D", "stage": "Reconciliation & Exceptions", 
            "process": "Investigations & Disputes",
            "description": "Provides tools and processes to investigate payment issues, manage disputes, and collaborate with other banks on resolutions.",
            "basic": "• Manual investigation processes.\n• Paper/email-based dispute handling.\n• No customer visibility into status.",
            "advanced": "• Case management system for investigations.\n• Documented dispute resolution procedures.\n• Customer status notifications.",
            "leading": "• Digital collaboration platform with counterparties.\n• Real-time case tracking dashboards.\n• Proactive funds recovery processes.",
            "emerging": "• AI-assisted root cause analysis.\n• Predictive case triage & prioritization.\n• Interbank blockchain investigation networks.",
        },
        
        # Stage 11: Reporting, Analytics & Notifications
        {
            "qid": "11A", "stage": "Reporting, Analytics & Notifications", 
            "process": "Payment Notifications",
            "description": "Delivers timely, informative alerts and notifications about payment events and status changes across appropriate channels.",
            "basic": "• Limited email notifications only.\n• Generic message templates.\n• Daily batch notification delivery.",
            "advanced": "• Multi-channel notification options.\n• Customizable notification preferences.\n• Intraday notification triggers.",
            "leading": "• Real-time push notifications.\n• Rich interactive alert content.\n• Context-aware delivery channel selection.",
            "emerging": "• AI-personalized notification content & timing.\n• Conversational alerts with action capabilities.\n• Predictive notifications before events occur.",
        },
        {
            "qid": "11B", "stage": "Reporting, Analytics & Notifications", 
            "process": "Reporting & Statements",
            "description": "Generates comprehensive reports, statements, and dashboards for customers, internal users, and regulators.",
            "basic": "• Standard fixed-format reports.\n• Monthly/quarterly generation cycles.\n• Manual report distribution.",
            "advanced": "• Custom report builder options.\n• Scheduled automated distribution.\n• Multiple export format options.",
            "leading": "• Self-service analytics portals.\n• Real-time data in all reports.\n• Interactive visualization dashboards.",
            "emerging": "• AI-generated report insights & summaries.\n• Natural language query for report generation.\n• Predictive trend reporting.",
        },
        {
            "qid": "11C", "stage": "Reporting, Analytics & Notifications", 
            "process": "Analytics & Insights",
            "description": "Provides business intelligence, analytics tools, and actionable insights based on payment data and patterns.",
            "basic": "• Basic transaction volume reporting.\n• Descriptive statistics only.\n• Manual data extraction for analysis.",
            "advanced": "• Business intelligence dashboards.\n• Trend analysis with visualizations.\n• Self-service data exploration.",
            "leading": "• Advanced analytics with pattern detection.\n• Peer benchmarking capabilities.\n• Recommendation engines for optimization.",
            "emerging": "• AI-driven predictive analytics.\n• Natural language insights generation.\n• Autonomous optimization suggestions.",
        },
        {
            "qid": "11D", "stage": "Reporting, Analytics & Notifications", 
            "process": "Status Tracking & Visibility",
            "description": "Enables real-time tracking of payment status across the lifecycle with appropriate visibility for all stakeholders.",
            "basic": "• Limited status visibility (initiated, completed).\n• Manual status checks via customer service.\n• No in-flight tracking.",
            "advanced": "• Online status tracking portal.\n• Major milestone visibility.\n• Payment history search capabilities.",
            "leading": "• Real-time end-to-end status visibility.\n• Cross-border payment tracking.\n• API status access for corporate systems.",
            "emerging": "• Global payment tracker with all intermediaries.\n• Predictive delivery time updates.\n• Immutable distributed status ledger.",
        },
        
        # Stage 12: Audit & Compliance
        {
            "qid": "12A", "stage": "Audit & Compliance", 
            "process": "Audit Trail & Logging",
            "description": "Captures comprehensive, tamper-evident logs of all actions, decisions, and events throughout the payment lifecycle.",
            "basic": "• Basic database transaction logs.\n• Limited duration of log retention.\n• No centralized audit repository.",
            "advanced": "• Structured audit logging framework.\n• Centralized secure audit repository.\n• Standard retention policies by data type.",
            "leading": "• Immutable audit trail with cryptographic verification.\n• Complete action attribution and chain of custody.\n• Advanced log search and correlation tools.",
            "emerging": "• Blockchain-based distributed audit ledger.\n• Zero-knowledge proof verification of integrity.\n• AI-assisted anomaly detection in audit trails.",
        },
        {
            "qid": "12B", "stage": "Audit & Compliance", 
            "process": "Record Retention & Archival",
            "description": "Securely stores payment records, supporting documents, and audit trails in compliance with legal and regulatory requirements.",
            "basic": "• Basic file storage with minimal indexing.\n• Manual archival processes.\n• Slow retrieval times for historical data.",
            "advanced": "• Digital archive with metadata indexing.\n• Automated archival based on rules.\n• Self-service search for common retrievals.",
            "leading": "• Full-text searchable compliance repository.\n• Lifecycle data management policies.\n• Rapid retrieval SLAs for all archives.",
            "emerging": "• AI-powered contextual search and retrieval.\n• Quantum-resistant long-term archival.\n• Smart contract-enforced retention policies.",
        },
        {
            "qid": "12C", "stage": "Audit & Compliance", 
            "process": "Regulatory Reporting",
            "description": "Generates and submits required regulatory reports accurately and on time—AML, sanctions, cross-border, statistical, etc.",
            "basic": "• Manual report compilation process.\n• Limited report types supported.\n• High compliance overhead.",
            "advanced": "• Automated regulatory report generation.\n• Validation before submission.\n• Digital submission to major regulators.",
            "leading": "• Continuous compliance monitoring.\n• Real-time regulatory reporting capacity.\n• Exception handling with audit trails.",
            "emerging": "• AI-assisted regulatory interpretation.\n• Automated regulatory update implementation.\n• Regtech API integration with authorities.",
        },
        {
            "qid": "12D", "stage": "Audit & Compliance", 
            "process": "Forensics & Investigation Support",
            "description": "Provides tools and data to support internal/external audits, investigations, disputes, and litigation related to payments.",
            "basic": "• Manual evidence gathering process.\n• Lengthy response time to audit requests.\n• Limited search capabilities.",
            "advanced": "• Digital evidence management system.\n• Standard audit response procedures.\n• Forensic data extraction tools.",
            "leading": "• Self-service audit portal for internal teams.\n• Advanced investigation tools with visualization.\n• Chain of custody documentation.",
            "emerging": "• AI-assisted investigation pattern matching.\n• Natural language forensic data exploration.\n• Predictive compliance issue identification.",
        }
    ]
    return data

def load_business_outcomes():
    """Load the business outcomes with their descriptions and KPIs."""
    data = [
        {
            "outcome": "Increased Customer Satisfaction",
            "description": "Improving the overall customer experience and satisfaction with payment services",
            "kpis": ["Net Promoter Score (NPS)", "Customer Effort Score", "Abandonment Rate", "User Satisfaction Rating"]
        },
        {
            "outcome": "Reduced Payment Processing Time",
            "description": "Decreasing the time required to process payments from initiation to completion",
            "kpis": ["Average Processing Time", "STP Rate", "Payment Velocity", "Time to Beneficiary Credit"]
        },
        {
            "outcome": "Enhanced Fraud Prevention",
            "description": "Strengthening defenses against payment fraud and unauthorized transactions",
            "kpis": ["Fraud Rate (bps)", "False Positive Rate", "Fraud Detection Rate", "Fraud Loss Ratio"]
        },
        {
            "outcome": "Improved Regulatory Compliance",
            "description": "Ensuring adherence to all applicable regulations and compliance requirements",
            "kpis": ["Compliance Violation Rate", "Regulatory Fine Exposure", "Screening Effectiveness", "Audit Findings"]
        },
        {
            "outcome": "Operational Cost Reduction",
            "description": "Lowering the cost of payment operations through efficiency and automation",
            "kpis": ["Cost per Transaction", "Manual Intervention Rate", "Exception Handling Cost", "Staff Efficiency Ratio"]
        },
        {
            "outcome": "Increased Straight-Through Processing",
            "description": "Maximizing the percentage of payments that process without manual intervention",
            "kpis": ["STP Rate", "First-Time Success Rate", "Repair Rate", "Manual Review Percentage"]
        },
        {
            "outcome": "Better Liquidity Management",
            "description": "Optimizing the use of funds and reducing liquidity costs for payment operations",
            "kpis": ["Intraday Liquidity Usage", "Funding Efficiency", "Nostro Utilization", "Liquidity Cost per Payment"]
        },
        {
            "outcome": "Enhanced Data Analytics Capability",
            "description": "Improving the ability to derive insights and value from payment data",
            "kpis": ["Data Availability", "Reporting Timeliness", "Analytics User Adoption", "Data-Driven Decision Rate"]
        }
    ]
    return data