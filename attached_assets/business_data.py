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
            "basic": "• Front-end only does simple field-format checks.\n• Validation limited to client-side (e.g. numeric, length).\n• No live lookups—errors surface later in batch.",
            "advanced": "• Server-side validation service for IBAN/MICR checks.\n• Real-time account existence lookups via core banking API.\n• Card BIN & expiry checks in real time for card-based flows.",
            "leading": "• Centralized data-validation microservice with live reference data (SWIFT BIC directory, national clearing tables).\n• Inline suggestions (\"Did you mean…?\") for payee names.\n• Auto-correction of common typos and address standardization.",
            "emerging": "• GenAI-powered free-text parsing: unstructured input automatically normalized.\n• Real-time watchlist & sanctions integration at data-entry time.\n• Self-learning validation rules that adapt to new patterns.",
        },
        {
            "qid": "1D", "stage": "Payment Initiation & Data Capture", 
            "process": "Submission & Preliminary Capture",
            "description": "Routes the sanitized payment request into the bank's front-end queue or middleware, marking it as \"pending initiation\" and locking resources for downstream processing.",
            "basic": "• Simple HTTP post to a middleware queue.\n• Batch-only submissions: payments sit in overnight queues.\n• No user feedback until next day or email confirmation.",
            "advanced": "• Real-time REST/Gateway submission to a payment hub.\n• Immediate user confirmation (\"Pending Initiation\") in UI.\n• Basic resiliency—automatic retry on intermittent failures.",
            "leading": "• Event-driven pipeline (Kafka/EventBridge) delivering to microservices.\n• Transaction deduplication & idempotency built in to avoid double-submits.\n• Live \"pending\" dashboard with status updates pushed to user.",
            "emerging": "• Intelligent orchestration: payment is deferred or triggered based on real-time cash-flow optimization.\n• Blockchain-backed mempool: requests posted to a distributed ledger for tamper-proof capture.\n• Self-healing submission with automated rerouting.",
        },
        # Stage 2: Authentication & Identity Validation
        {
            "qid": "2A", "stage": "Authentication & Identity Validation", 
            "process": "User Credential Verification",
            "description": "Verifying the payer's identity via credentials at channel entry.",
            "basic": "• Separate credentials per channel (web, mobile, branch), often weak password/PIN.\n• No device binding—credentials can be shared.\n• Manual unlock resets.",
            "advanced": "• Centralized IAM with SSO across channels.\n• Device-trust tokens or remembered devices.\n• Basic password policies.",
            "leading": "• CIAM with OAuth2/OpenID Connect, biometric login (fingerprint/face) across channels.\n• Phishing-resistant tokens (FIDO2/WebAuthn).\n• Adaptive lockout policies based on risk.",
            "emerging": "• Decentralized identity (DID) with verifiable credentials.\n• Continuous authentication via behavioral biometrics.\n• Zero-knowledge proof authentication.",
        },
        {
            "qid": "2B", "stage": "Authentication & Identity Validation", 
            "process": "Multi-Factor & Risk-Based Checks",
            "description": "Additional verification factors triggered by risk or policy, beyond the primary credential.",
            "basic": "• Static MFA (SMS OTP) applied uniformly.\n• No risk scoring—every login requires second factor.\n• High user friction.",
            "advanced": "• Adaptive MFA: skip MFA for trusted devices/sessions; step-up for new devices.\n• App-push or hardware tokens instead of SMS.\n• Basic geo-fencing rules.",
            "leading": "• Risk engine using device-fingerprint, IP reputation, transaction context to dynamically require MFA.\n• Passwordless options (biometric via mobile app).\n• Phishing-resistant WebAuthn across devices.",
            "emerging": "• AI-driven continuous risk scoring, continuous authentication.\n• Invisible MFA (risk signals only).\n• Behavior-based anomaly detection in real-time.",
        },
        {
            "qid": "2C", "stage": "Authentication & Identity Validation", 
            "process": "Corporate Role & Limit Checks",
            "description": "Ensuring the user's role and transaction limits are enforced before proceeding.",
            "basic": "• Manual role assignments in static groups; limits enforced by policy but in separate systems.\n• No real-time sync with HR or authorization systems.",
            "advanced": "• Role-based access control (RBAC) managed in centralized IAM.\n• Limits check integrated into the payment UI (per-transaction limit pop-up warnings).\n• Real-time sync with LDAP/AD.",
            "leading": "• Attribute-based access control (ABAC): roles, departments, risk scores, transaction context determine approval flows.\n• Integrated with corporate HCM for automatic revocations.\n• Dynamic limits that adjust by behavior.",
            "emerging": "• Policy-as-code engines (OPA, etc.) governing entitlements.\n• Smart-contract enforcement of multi-sig thresholds on DLT.\n• Continuous authorization based on risk signals.",
        },
        {
            "qid": "2D", "stage": "Authentication & Identity Validation", 
            "process": "Session Creation",
            "description": "Establishing a secure, tracked user session after authentication.",
            "basic": "• Basic web session cookie with fixed timeout (e.g. 15 min).\n• Limited logging of session events.\n• No idle-timeout variation.",
            "advanced": "• Secure cookie flags (HttpOnly, Secure), configurable session lifetimes by channel.\n• Session logs forwarded to SIEM.\n• Idle timeout resets on activity.",
            "leading": "• Contextual sessions (device, geolocation, transaction type) with dynamic timeout.\n• Session continuation across channels (e.g. start on mobile, continue on web).\n• Real-time session monitoring & anomaly alerts.",
            "emerging": "• Zero-trust continuous session validation.\n• Frictionless session handover via NFTs or secure tokens in decentralized architectures.\n• AI-driven session risk scoring.",
        },
        # Stage 3: Pre-Submission Validation
        {
            "qid": "3A", "stage": "Pre-Submission Validation", 
            "process": "Data Completeness Checks",
            "description": "Verify all required fields are present and correctly formatted (e.g., beneficiary name, account number, currency, amount).",
            "basic": "• UI-only checks (non-empty, numeric).\n• Fields typed manually; errors catch at batch time.\n• No contextual hints.",
            "advanced": "• Shared validation service for formats (IBAN, SWIFT BIC).\n• Inline lookup for account existence.\n• Mandatory-field prompts with auto-focus on errors.",
            "leading": "• Centralized validation micro-service with schema versioning.\n• Real-time lookups against master data (customer directory, sanctions list).\n• Self-learning suggestions (e.g., correct payee name).",
            "emerging": "• GenAI free-text parsing and auto-correction (\"John Acme\" → \"Acme Corp.\").\n• Contextual validation (e.g., amount vs. customer's typical behavior).\n• Predictive field completion based on past behavior.",
        },
        {
            "qid": "3B", "stage": "Pre-Submission Validation", 
            "process": "Business Rule Enforcement",
            "description": "Enforce bank policies: transaction limits, daily caps, corporate spending rules, duplicate-payment detection.",
            "basic": "• Hard-coded limits in front-end or core.\n• Duplicate detection only by exact reference match.\n• No tiered limits.",
            "advanced": "• Configurable rule engine (limits, caps, velocity).\n• Fuzzy duplicate detection (reference+amount+payee).\n• Separate retail vs. corporate profiles.",
            "leading": "• Policy-as-code with GUI for business users to update rules.\n• Real-time business-day cut-off checks, dynamic aggregation of daily volumes.\n• Multi-factor duplicate detection with AI scoring.",
            "emerging": "• Autonomous policy generation via ML on historical exceptions.\n• Context-aware caps that adjust by client risk profile & cash-flow forecasts.\n• Self-optimizing rules that adapt to emerging patterns.",
        },
        {
            "qid": "3C", "stage": "Pre-Submission Validation", 
            "process": "Preliminary AML/Watchlist",
            "description": "First-line screening checks against watchlists, blacklists, or sanctions before routing the payment.",
            "basic": "• Simple keyword blacklist check.\n• No fuzzy matching for name variants.\n• Only full matches are flagged.",
            "advanced": "• Daily-updated regulatory sanctions lists.\n• Basic fuzzy matching for name variants.\n• Automatic blocking for exact matches.",
            "leading": "• Real-time AML scoring against ML models.\n• Advanced name-matching algorithms (Levenshtein, phonetic).\n• Risk-based routing for review vs. straight-through processing.",
            "emerging": "• AI-driven entity resolution across multiple data sources.\n• Cloud-scale matching against terabytes of risk data.\n• Self-tuning models that adapt to emerging threats.",
        },
        {
            "qid": "3D", "stage": "Pre-Submission Validation", 
            "process": "Error Handling & User Feedback",
            "description": "Mechanism to return human-readable, actionable errors to the end user or corporate system.",
            "basic": "• Generic error messages (e.g., \"system error\").\n• No field-specific error handling.\n• Overnight batch error reports.",
            "advanced": "• Field-level error messages with validation rules.\n• Immediate UI feedback on errors.\n• Suggested corrections for common issues.",
            "leading": "• Intelligent error aggregation with prioritization.\n• Context-aware suggestions based on historical patterns.\n• Real-time dashboards for error tracking.",
            "emerging": "• GenAI-powered natural language error explanations.\n• Predictive error correction before submission.\n• Auto-resolution for common errors based on historical fixes.",
        },
        # Stage 4: Payment Orchestration
        {
            "qid": "4A", "stage": "Payment Orchestration", 
            "process": "Payment Classification",
            "description": "Categorizing payments by type, value, urgency, and routing requirements.",
            "basic": "• Manual payment classification by user.\n• No dynamic routing logic.\n• No differentiation between high/low value.",
            "advanced": "• Automated sorting by payment attributes (amount, beneficiary country).\n• Basic prioritization (standard, urgent).\n• Payment type recognition (salary, supplier, tax).",
            "leading": "• ML-based classification with high accuracy.\n• Full multi-rail routing capability.\n• STP eligibility scoring.",
            "emerging": "• Predictive classification based on historical patterns.\n• Dynamic categorization using document context (e.g., invoice).\n• Self-optimizing routing that learns from outcomes.",
        },
        {
            "qid": "4B", "stage": "Payment Orchestration", 
            "process": "Rail & Network Selection",
            "description": "Determining optimal payment network, considering cost, time, coverage, and information-carrying capability.",
            "basic": "• Single payment rail per country/currency.\n• Inefficient manual correspondent selection.\n• No alternative routing.",
            "advanced": "• Multiple rails with rule-based selection.\n• Basic cost vs. speed optimization.\n• Preferred correspondent bank selection.",
            "leading": "• Dynamic scoring across all available rails.\n• Real-time availability check with circuit-breaker pattern.\n• Cost, speed, and risk-balanced routing.",
            "emerging": "• AI-powered routing optimizing across 10+ parameters.\n• Real-time cost-prediction models per transaction profile.\n• Dynamic market conditions influence on routing (e.g., FX rates).",
        },
        {
            "qid": "4C", "stage": "Payment Orchestration", 
            "process": "Route Optimization",
            "description": "Advanced selection of routing path, intermediaries, and execution timing.",
            "basic": "• Static routing tables.\n• No optimization for cost or speed.\n• Manual entry of routing instructions.",
            "advanced": "• Rules-based routing by currency, country, amount.\n• Preferred correspondent relationships configured.\n• Basic FX integration.",
            "leading": "• Dynamic routing algorithm with multiple optimization goals.\n• Real-time network status monitoring influencing route selection.\n• Full liquidity and FX rate-aware routing.",
            "emerging": "• ML/AI models predicting optimal routes per transaction profile.\n• Real-time global liquidity optimization across correspondent network.\n• Predictive cut-off management with dynamic timing.",
        },
        {
            "qid": "4D", "stage": "Payment Orchestration", 
            "process": "Event Hand-off",
            "description": "Transitions the validated, classified payment into the processing pipeline.",
            "basic": "• Basic queue submission.\n• No reliable event status tracking.\n• Manual re-submission for failures.",
            "advanced": "• Middleware messaging service.\n• Delivery acknowledgments.\n• Basic retry logic for failures.",
            "leading": "• Event-driven architecture with guaranteed delivery.\n• Comprehensive event logging with correlation IDs.\n• Circuit breakers for downstream system failures.",
            "emerging": "• Distributed event mesh with zero message loss.\n• Self-healing pipeline with automatic rerouting.\n• ML-based anomaly detection in event flow.",
        },
        # Stage 5: Risk & Compliance
        {
            "qid": "5A", "stage": "Risk & Compliance", 
            "process": "Transaction Risk Scoring",
            "description": "Real-time evaluation of transaction risk against multiple risk vectors.",
            "basic": "• Manual risk review of large transactions.\n• No systematic risk scoring.\n• Rule-based holdback thresholds only.",
            "advanced": "• Automated scoring against basic risk rules.\n• Risk-based routing to manual review queues.\n• Integration with basic customer risk ratings.",
            "leading": "• Machine learning risk models with multiple data inputs.\n• Real-time scoring with 95%+ straight-through processing.\n• Visual risk analytics for fraud teams.",
            "emerging": "• AI-powered transaction risk models with 1000+ signals.\n• Self-learning algorithms adapting to emerging threats.\n• Collective intelligence across bank network for threat detection.",
        },
        {
            "qid": "5B", "stage": "Risk & Compliance", 
            "process": "Sanctions & Watchlist Screening",
            "description": "Detailed checking of all parties against official sanctions lists, PEP lists, and internal watchlists.",
            "basic": "• Basic exact-match checking against primary sanctions lists.\n• Manual screening of flagged transactions.\n• Weekly or monthly sanctions list updates.",
            "advanced": "• Fuzzy matching algorithms for name variants.\n• Daily list updates from regulatory sources.\n• Screening of all transaction fields, not just names.",
            "leading": "• Advanced entity resolution across multiple data sources.\n• Real-time list updates and re-screening capability.\n• Risk-based screening intensity with minimal false positives.",
            "emerging": "• AI-powered entity matching with semantic understanding.\n• Predictive screening based on network analysis and pattern recognition.\n• Collective intelligence from cross-bank consortium data.",
        },
        {
            "qid": "5C", "stage": "Risk & Compliance", 
            "process": "AML Monitoring",
            "description": "Anti-Money Laundering checks examining transaction patterns, unusual behaviors, and compliance with regulations.",
            "basic": "• Manual AML review of flagged transactions.\n• Static rule thresholds causing high false positives.\n• Overnight batch AML processing only.",
            "advanced": "• Real-time rules engine for common AML scenarios.\n• Integration with KYC/customer risk data.\n• ML-assisted alert triage for investigators.",
            "leading": "• Advanced behavioral analytics detecting anomalies in real-time.\n• Network analysis identifying hidden relationships between entities.\n• Adaptive learning from investigator actions.",
            "emerging": "• AI-driven holistic customer risk assessment across all channels and products.\n• Predictive pattern recognition identifying emerging typologies.\n• Graph analytics mapping entire suspicious networks.",
        },
        {
            "qid": "5D", "stage": "Risk & Compliance", 
            "process": "Case Management",
            "description": "Managing alerts, investigations, and resolution of flagged transactions.",
            "basic": "• Manual case creation and workflow.\n• No prioritization of alerts.\n• Basic documentation of investigation steps.",
            "advanced": "• Digital case management system.\n• Risk-based queue prioritization.\n• Standardized investigation procedures.",
            "leading": "• AI-assisted investigation with recommended actions.\n• Automated evidence gathering and analysis.\n• Full audit trail with decision justification capture.",
            "emerging": "• Autonomous case resolution for common scenarios.\n• Predictive resource allocation based on case complexity.\n• Cognitive assistant summarizing case details and suggesting next steps.",
        },
        # Stage 6: Final Authorisation
        {
            "qid": "6A", "stage": "Final Authorisation", 
            "process": "User Confirmation",
            "description": "Final approval step for the payment initiator, showing all details and fees.",
            "basic": "• Simple confirmation screen with basic details.\n• No clear fee disclosure.\n• No summary of important payment info.",
            "advanced": "• Detailed confirmation with all transaction data.\n• Clear fee and exchange rate disclosure.\n• Digital receipt generation.",
            "leading": "• Interactive confirmation with edit capability.\n• Visual transaction journey timeline.\n• Real-time SLA and delivery time estimates.",
            "emerging": "• Predictive confirmation with impact analysis on account balance.\n• Virtual assistant summarizing key transaction details.\n• Multi-language, accessibility-optimized confirmation options.",
        },
        {
            "qid": "6B", "stage": "Final Authorisation", 
            "process": "Multi-Party Approval",
            "description": "Additional approvals required from other parties (e.g., second manager approval or joint account holder).",
            "basic": "• Email notification for secondary approvals.\n• Manual tracking of approval status.\n• No delegation capabilities.",
            "advanced": "• Digital approval workflow with notifications.\n• Approval hierarchy enforcement.\n• Basic delegation for vacations/absences.",
            "leading": "• Mobile app push approvals with biometrics.\n• Dynamic authority matrix based on transaction context.\n• Real-time approval status tracking.",
            "emerging": "• Smart contract-based approval with consensus mechanism.\n• AI-recommended approval routing based on availability and urgency.\n• Continuous behavioral authentication during approval process.",
        },
        {
            "qid": "6C", "stage": "Final Authorisation", 
            "process": "Final Validation",
            "description": "Last check for errors, issues or risk factors before commitment.",
            "basic": "• No systematic final validation.\n• Last-minute checks rely on user diligence.\n• No cutoff time warnings.",
            "advanced": "• Pre-release automated check of key fields.\n• Transaction duplicate detection.\n• Cutoff time warnings with countdown.",
            "leading": "• Comprehensive validation service checking all potential issues.\n• Real-time funds sufficiency verification.\n• Dynamic risk re-scoring at submission moment.",
            "emerging": "• Predictive validation identifying potential future issues.\n• Autonomous correction of common errors before execution.\n• Behavioral risk analysis at final submission.",
        },
        {
            "qid": "6D", "stage": "Final Authorisation", 
            "process": "Payment Commitment",
            "description": "Irrevocable commitment of the payment into the processing layer.",
            "basic": "• Simple database status update.\n• No cryptographic protection.\n• Limited immutability controls.",
            "advanced": "• Digitally signed transaction receipt.\n• Immutable audit trail of commitment.\n• Real-time commitment confirmation.",
            "leading": "• Multi-signature digital commitment.\n• Blockchain-inspired immutable record.\n• Non-repudiation evidence capture.",
            "emerging": "• Zero-knowledge proof commitments for privacy.\n• Smart-contract based irrevocable commitment.\n• Quantum-resistant cryptographic protection.",
        },
        # Stage 7: Message Transformation
        {
            "qid": "7A", "stage": "Message Transformation", 
            "process": "Format Conversion",
            "description": "Converting the internal payment format to external network-specific formats (SWIFT MT, ISO 20022, etc.).",
            "basic": "• Basic template-based message formatting.\n• Manual handling of format exceptions.\n• Limited format support (e.g., MT only).",
            "advanced": "• Configurable mapping engine for multiple formats.\n• Validation against schema definitions.\n• Support for MT and basic ISO 20022 formats.",
            "leading": "• Full multi-format transformation service.\n• Complete ISO 20022 support with extensions.\n• Automatic schema version detection and handling.",
            "emerging": "• AI-assisted message transformation learning from patterns.\n• Self-adapting to new message formats and standards.\n• Network-specific optimizations automatically applied.",
        },
        {
            "qid": "7B", "stage": "Message Transformation", 
            "process": "Data Enrichment",
            "description": "Adding supplementary information to the payment message beyond what was explicitly provided.",
            "basic": "• No automated enrichment.\n• Manual addition of missing data.\n• Minimal regulatory information.",
            "advanced": "• Basic reference data lookup (BIC from IBAN, etc.).\n• Standard regulatory code insertion.\n• Enrichment from customer reference data.",
            "leading": "• Comprehensive enrichment from multiple sources.\n• ML-based purpose code classification.\n• Auto-correction of formatting issues in free-text fields.",
            "emerging": "• Predictive enrichment based on payment context and history.\n• Natural language processing of payment references.\n• Semantic understanding of payment purpose.",
        },
        {
            "qid": "7C", "stage": "Message Transformation", 
            "process": "Truncation & Special Handling",
            "description": "Managing field-length limitations, character restrictions, and special cases.",
            "basic": "• Simple truncation without notification.\n• Character stripping causing data loss.\n• Manual handling of special cases.",
            "advanced": "• Intelligent truncation preserving critical information.\n• Character transliteration for unsupported symbols.\n• Detection and handling of common special cases.",
            "leading": "• Semantic-aware truncation preserving meaning.\n• Multi-part message handling for oversize data.\n• Comprehensive special case library with automated handling.",
            "emerging": "• AI-powered compression of meaning into limited space.\n• Self-learning from truncation outcomes and issues.\n• Predictive detection of potential transliteration problems.",
        },
        {
            "qid": "7D", "stage": "Message Transformation", 
            "process": "Error Handling",
            "description": "Managing transformation failures and validation issues.",
            "basic": "• Generic error messages.\n• Manual repair of failed messages.\n• No root cause tracking.",
            "advanced": "• Specific error codes with resolution guidance.\n• Semi-automated repair suggestions.\n• Categorization of error types.",
            "leading": "• Intelligent error detection with automatic repair.\n• Learning system improving from past errors.\n• Visual repair workbench for complex issues.",
            "emerging": "• Self-healing error correction based on past resolutions.\n• Natural language explanation of errors and solutions.\n• Predictive avoidance of known error conditions.",
        },
        # Stage 8: Clearing & Acknowledgment
        {
            "qid": "8A", "stage": "Clearing & Acknowledgment", 
            "process": "Network Transmission",
            "description": "Sending the payment instruction to external clearing networks or correspondent banks.",
            "basic": "• Batch-based file transmission on schedule.\n• No real-time transmission capability.\n• Manual network status monitoring.",
            "advanced": "• Near-real-time message transmission.\n• Basic API connectivity to clearing networks.\n• Automated retry for failed transmissions.",
            "leading": "• Real-time API transmission with instant confirmation.\n• Multi-channel connectivity (API, MQ, file).\n• Intelligent routing based on network availability.",
            "emerging": "• Mesh network with peer-to-peer transmission options.\n• Self-optimizing transmission timing for cost/speed balance.\n• Predictive capacity management across channels.",
        },
        {
            "qid": "8B", "stage": "Clearing & Acknowledgment", 
            "process": "Queue Management",
            "description": "Managing the flow, prioritization, and processing of payments.",
            "basic": "• First-in-first-out queuing only.\n• No prioritization capabilities.\n• Manual queue monitoring and adjustment.",
            "advanced": "• Basic prioritization by payment type and value.\n• Configurable throttling and flow control.\n• Active queue monitoring with alerts.",
            "leading": "• Dynamic queue management with multiple algorithms.\n• Real-time balancing across processing resources.\n• Automatic intervention for bottlenecks.",
            "emerging": "• AI-driven predictive queue optimization.\n• Self-tuning processing allocation based on patterns.\n• Anomaly detection preventing potential congestion.",
        },
        {
            "qid": "8C", "stage": "Clearing & Acknowledgment", 
            "process": "Correspondent Handling",
            "description": "Interactions with correspondent banks when direct clearing access is unavailable.",
            "basic": "• Static correspondent routing tables.\n• Manual nostro account balance monitoring.\n• Basic reconciliation of correspondent activity.",
            "advanced": "• Rules-based correspondent selection.\n• Daily nostro balance forecasting.\n• Automated reconciliation of correspondent statements.",
            "leading": "• Dynamic correspondent selection based on multiple factors.\n• Real-time nostro monitoring and management.\n• SLA tracking of correspondent performance.",
            "emerging": "• ML-powered nostro optimization across the network.\n• Predictive modeling of correspondent behavior and performance.\n• Auto-switching between correspondents based on capacity and pricing.",
        },
        {
            "qid": "8D", "stage": "Clearing & Acknowledgment", 
            "process": "Acknowledgment Processing",
            "description": "Receiving and processing acknowledgments or rejections from clearing networks.",
            "basic": "• Manual checking of acknowledgment status.\n• Overnight processing of response files.\n• No real-time feedback to users.",
            "advanced": "• Automated matching of acknowledgments to payments.\n• Same-day processing of responses.\n• Basic status updates to originator.",
            "leading": "• Real-time processing of network acknowledgments.\n• Immediate notification of originator for rejections.\n• Automated repair suggestions for rejected payments.",
            "emerging": "• Predictive acknowledgment issues before they occur.\n• ML-based analysis of rejection patterns for systemic improvements.\n• Natural language explanation of complex reject reasons.",
        },
        # Stage 9: Settlement
        {
            "qid": "9A", "stage": "Settlement", 
            "process": "Liquidity Management",
            "description": "Managing fund positions and ensuring settlement account sufficiency.",
            "basic": "• Daily funding of settlement accounts.\n• Manual liquidity movements.\n• Basic beginning-of-day position forecasting.",
            "advanced": "• Intraday funding based on schedules.\n• Semi-automated liquidity transfers.\n• Standard forecasting models for positions.",
            "leading": "• Real-time liquidity monitoring and automated funding.\n• Dynamic threshold management.\n• Multiple scenario modeling for liquidity needs.",
            "emerging": "• AI-powered predictive liquidity optimization.\n• Self-adjusting funding algorithm learning from patterns.\n• Integration with cross-asset collateral optimization.",
        },
        {
            "qid": "9B", "stage": "Settlement", 
            "process": "Settlement Execution",
            "description": "Final movement of funds between financial institutions.",
            "basic": "• End-of-day net settlement only.\n• Manual reconciliation of settlement positions.\n• Limited settlement window options.",
            "advanced": "• Multiple intraday settlement windows.\n• Automated reconciliation of settled positions.\n• Active management of settlement risks.",
            "leading": "• Real-time gross settlement capability.\n• Continuous settlement position monitoring.\n• Advanced collateral management for settlement efficiency.",
            "emerging": "• Blockchain/DLT-based settlement mechanisms.\n• Self-optimizing settlement timing based on cost/speed tradeoff.\n• AI-driven settlement failure prediction and prevention.",
        },
        {
            "qid": "9C", "stage": "Settlement", 
            "process": "Intraday Management",
            "description": "Active management of positions and liquidity throughout the business day.",
            "basic": "• Beginning and end-of-day position monitoring only.\n• Manual intervention for shortfalls.\n• No real-time position visibility.",
            "advanced": "• Scheduled intraday position checking.\n• Threshold-based alerting for action.\n• Basic forecasting of end-of-day positions.",
            "leading": "• Real-time position monitoring with continuous forecasting.\n• Automated balancing across accounts and currencies.\n• Dynamic prioritization of payments based on liquidity impact.",
            "emerging": "• AI-driven predictive liquidity management.\n• Autonomous intraday rebalancing of positions.\n• Integrated cross-currency liquidity optimization.",
        },
        {
            "qid": "9D", "stage": "Settlement", 
            "process": "Finality & Legal Completion",
            "description": "Establishing the irrevocable, legally binding completion of the payment.",
            "basic": "• Paper-based settlement confirmation.\n• Manual tracking of finality status.\n• Standard settlement terms with counterparties.",
            "advanced": "• Digital settlement confirmation with time-stamps.\n• Automated tracking of settlement status.\n• Standardized legal agreements for major counterparties.",
            "leading": "• Cryptographically secured settlement evidence.\n• Real-time finality notification to all parties.\n• Comprehensive legal framework with digital enforcement.",
            "emerging": "• Blockchain-based immutable settlement proof.\n• Smart contracts automatically executing settlement terms.\n• Self-sovereign identity verification of all settlement parties.",
        },
        # Stage 10: Reconciliation
        {
            "qid": "10A", "stage": "Reconciliation", 
            "process": "Internal Matching",
            "description": "Matching transactions across internal systems to ensure consistency.",
            "basic": "• Daily batch reconciliation processes.\n• Manual investigation of breaks.\n• Limited matching criteria (reference number only).",
            "advanced": "• Multiple intraday reconciliation runs.\n• Semi-automated matching with human review.\n• Multiple matching criteria with confidence scores.",
            "leading": "• Real-time continuous reconciliation.\n• ML-assisted auto-matching of complex cases.\n• Pattern recognition for systematic break identification.",
            "emerging": "• AI-powered predictive matching learning from past patterns.\n• Autonomous resolution of common reconciliation issues.\n• Self-improving matching algorithms continuously optimizing.",
        },
        {
            "qid": "10B", "stage": "Reconciliation", 
            "process": "Statement Generation",
            "description": "Creating customer statements and transaction records.",
            "basic": "• Daily batch statement processing.\n• Limited format options (PDF, paper).\n• Basic transaction descriptions.",
            "advanced": "• Intraday statement updates.\n• Multiple digital formats (CSV, MT940, PDF).\n• Enhanced transaction narratives with merchant data.",
            "leading": "• Real-time statement updates across channels.\n• Comprehensive format library including ISO 20022 camt.\n• Rich transaction context with categorization.",
            "emerging": "• Predictive transaction categorization and analysis.\n• Natural language summaries of financial activity.\n• ML-driven insights embedded in statements.",
        },
        {
            "qid": "10C", "stage": "Reconciliation", 
            "process": "Exception Handling",
            "description": "Managing unmatched items, returns, and other exceptions.",
            "basic": "• Manual exception review and resolution.\n• Basic sorting of exception types.\n• No automation in resolution.",
            "advanced": "• Workflow-based exception handling.\n• Prioritized exception queues by type and age.\n• Semi-automated resolution for common cases.",
            "leading": "• ML-assisted exception categorization and resolution.\n• Predictive analysis of exception root causes.\n• Automated resolution for majority of common exceptions.",
            "emerging": "• AI-driven autonomous exception management.\n• Self-learning from resolution patterns.\n• Predictive exception prevention based on historical analysis.",
        },
        {
            "qid": "10D", "stage": "Reconciliation", 
            "process": "Investigations & Disputes",
            "description": "Handling customer inquiries about payment status, missing payments, or disputes.",
            "basic": "• Manual investigation process.\n• Paper-based documentation.\n• Long resolution timeframes (days/weeks).",
            "advanced": "• Digital case management system.\n• Standardized investigation procedures.\n• Moderate resolution times (1-2 days).",
            "leading": "• Automated investigation data gathering.\n• Real-time payment tracking information for customers.\n• Swift resolution times (hours).",
            "emerging": "• AI-powered autonomous investigations.\n• Predictive issue identification before customer inquiry.\n• Immutable audit trail with distributed verification.",
        },
        # Stage 11: Reporting & Analytics
        {
            "qid": "11A", "stage": "Reporting & Analytics", 
            "process": "Transaction Notification",
            "description": "Immediate notification to customers about payment events.",
            "basic": "• Batch email notifications only.\n• Limited notification events (completion only).\n• Generic message templates.",
            "advanced": "• Real-time push notifications via multiple channels.\n• Several notification triggers (initiated, cleared, rejected).\n• Basic customization of notification content.",
            "leading": "• Comprehensive omni-channel notification system.\n• Full payment lifecycle event notifications.\n• Rich content with transaction context and next steps.",
            "emerging": "• Predictive notifications based on customer preferences.\n• AI-personalized content and channel selection.\n• Context-aware notification timing optimization.",
        },
        {
            "qid": "11B", "stage": "Reporting & Analytics", 
            "process": "Statement & History",
            "description": "Providing historical views of payment activity.",
            "basic": "• Monthly PDF statements only.\n• Limited search capabilities.\n• Basic transaction details only.",
            "advanced": "• Digital statement portal with search.\n• Multiple download formats.\n• Enhanced transaction data with merchant information.",
            "leading": "• Interactive payment history with advanced filtering.\n• Real-time updates to history across channels.\n• Comprehensive metadata and contextual information.",
            "emerging": "• Predictive categorization and tagging of transactions.\n• Natural language search of payment history.\n• ML-driven insights on spending patterns and anomalies.",
        },
        {
            "qid": "11C", "stage": "Reporting & Analytics", 
            "process": "Business Intelligence",
            "description": "Analytical capabilities for payment data.",
            "basic": "• Static predefined reports only.\n• Minimal aggregation capabilities.\n• Manual data extraction for analysis.",
            "advanced": "• Self-service reporting portal.\n• Standard dashboards and visualizations.\n• Scheduled report distribution.",
            "leading": "• Real-time analytics dashboards.\n• Drill-down and ad hoc analysis capability.\n• Advanced visualizations and trend analysis.",
            "emerging": "• AI-powered payment flow insights and recommendations.\n• Predictive analytics forecasting future patterns.\n• Natural language query interface for business users.",
        },
        {
            "qid": "11D", "stage": "Reporting & Analytics", 
            "process": "Payment Tracking",
            "description": "Providing visibility into the current status of in-flight payments.",
            "basic": "• Manual status lookup on request.\n• Limited tracking data (sent, completed only).\n• No proactive updates.",
            "advanced": "• Self-service tracking portal.\n• Multiple status points tracked.\n• Basic notifications for status changes.",
            "leading": "• Real-time payment tracker with complete journey visibility.\n• SWIFT gpi or equivalent integration.\n• Proactive alerting for delays or issues.",
            "emerging": "• Predictive delivery time estimation with confidence intervals.\n• IoT-like distributed tracking across correspondent network.\n• ML-based delay prediction and proactive intervention.",
        },
        # Stage 12: Audit & Compliance
        {
            "qid": "12A", "stage": "Audit & Compliance", 
            "process": "Audit Trail",
            "description": "Comprehensive record of all actions, decisions, and events.",
            "basic": "• Basic logging of main transaction events.\n• Manual extraction of audit data.\n• Limited retention periods.",
            "advanced": "• Detailed event logging across the payment lifecycle.\n• Searchable audit repository.\n• Extended retention compliant with regulations.",
            "leading": "• Immutable audit trail with cryptographic verification.\n• Full context capture including user, system, and decision points.\n• Real-time audit data streaming with alerting.",
            "emerging": "• Blockchain/DLT-based distributed audit ledger.\n• AI-powered anomaly detection in audit patterns.\n• Self-verifying audit trail with zero-knowledge proofs.",
        },
        {
            "qid": "12B", "stage": "Audit & Compliance", 
            "process": "Record Retention",
            "description": "Storing and managing payment records for legal and compliance purposes.",
            "basic": "• Basic document management system.\n• Manual archiving processes.\n• Limited search and retrieval capabilities.",
            "advanced": "• Digital archive with metadata tagging.\n• Automated retention policy enforcement.\n• Full-text search of archived records.",
            "leading": "• Intelligent archiving with context preservation.\n• ML-based classification for appropriate retention.\n• Advanced search with relationship mapping.",
            "emerging": "• Self-sovereign data with distributed storage and encryption.\n• AI-powered retrieval with semantic understanding.\n• Quantum-resistant long-term archive security.",
        },
        {
            "qid": "12C", "stage": "Audit & Compliance", 
            "process": "Regulatory Reporting",
            "description": "Generating and submitting required regulatory reports.",
            "basic": "• Manual report compilation.\n• Basic validation before submission.\n• Limited regulatory coverage.",
            "advanced": "• Automated report generation from templates.\n• Comprehensive validation rules.\n• Coverage of major regulatory requirements.",
            "leading": "• Continuous compliance monitoring and reporting.\n• Real-time regulatory data lake.\n• Automated submission to regulatory portals.",
            "emerging": "• AI-driven regulatory intelligence predicting requirement changes.\n• Integrated compliance-as-code in payment flows.\n• Regulatory sandbox with scenario testing.",
        },
        {
            "qid": "12D", "stage": "Audit & Compliance", 
            "process": "Forensics & Investigation",
            "description": "Capability to research historical transactions for audit or investigation.",
            "basic": "• Manual gathering of transaction data.\n• Basic search by primary identifiers only.\n• Limited context available for review.",
            "advanced": "• Dedicated investigation tools and interfaces.\n• Multiple search dimensions (date, amount, party).\n• Standard investigation templates and procedures.",
            "leading": "• Network analysis visualization of related transactions.\n• Pattern-matching algorithms for case comparisons.\n• Full context preservation including peripheral systems.",
            "emerging": "• AI-powered investigation assistant with recommended paths.\n• Predictive pattern recognition of suspicious flows.\n• Autonomous preliminary investigation with human validation.",
        }
    ]
    
    # Create DataFrame from the data list
    return pd.DataFrame(data)

def load_business_outcomes():
    """Load the business outcomes with their descriptions and KPIs."""
    data = [
        {
            "outcome": "Increased Customer Satisfaction",
            "description": "Enhancing the overall payment experience for customers through faster, more reliable, and user-friendly payment services.",
            "kpis": [
                "Customer satisfaction scores",
                "Net Promoter Score (NPS)",
                "Reduced customer complaints",
                "Increased customer retention",
                "Higher digital channel adoption"
            ]
        },
        {
            "outcome": "Reduced Payment Processing Time",
            "description": "Decreasing the time required to process payments from initiation to settlement, improving efficiency and customer experience.",
            "kpis": [
                "Average payment processing time",
                "Percentage of real-time payments",
                "End-to-end payment completion time",
                "Same-day settlement rate",
                "Cut-off time performance"
            ]
        },
        {
            "outcome": "Enhanced Fraud Prevention",
            "description": "Strengthening security measures to detect and prevent fraudulent payment activities, protecting both the institution and customers.",
            "kpis": [
                "Fraud detection rate",
                "False positive rate",
                "Fraud losses as percentage of payment volume",
                "Fraud prevention savings",
                "Time to detect fraudulent patterns"
            ]
        },
        {
            "outcome": "Improved Regulatory Compliance",
            "description": "Ensuring all payment processes adhere to relevant regulations, standards, and reporting requirements.",
            "kpis": [
                "Compliance violation incidents",
                "Regulatory reporting accuracy",
                "Time to implement regulatory changes",
                "Audit findings",
                "Regulatory fine avoidance"
            ]
        },
        {
            "outcome": "Operational Cost Reduction",
            "description": "Lowering the costs associated with payment processing through automation, optimization, and increased efficiency.",
            "kpis": [
                "Cost per payment transaction",
                "Manual intervention rate",
                "Staff productivity metrics",
                "Infrastructure cost reduction",
                "Return on investment for automation"
            ]
        },
        {
            "outcome": "Increased Straight-Through Processing",
            "description": "Maximizing the percentage of payments that process automatically without manual intervention, reducing costs and errors.",
            "kpis": [
                "STP rate",
                "Manual repair rate",
                "Exception handling time",
                "First-time payment success rate",
                "Automated validation success rate"
            ]
        },
        {
            "outcome": "Better Liquidity Management",
            "description": "Optimizing cash positioning and funding to ensure sufficient liquidity for settlement while minimizing idle balances.",
            "kpis": [
                "Intraday liquidity usage efficiency",
                "Funding costs",
                "Liquidity buffer optimization",
                "Nostro account efficiency",
                "Payment timing optimization"
            ]
        },
        {
            "outcome": "Enhanced Data Analytics Capability",
            "description": "Leveraging payment data for business intelligence, customer insights, and strategic decision-making.",
            "kpis": [
                "Data quality index",
                "Analytics adoption by business users",
                "Data-driven decision rate",
                "Time to insight",
                "Revenue from data-enhanced services"
            ]
        }
    ]
    
    # Create DataFrame from the data list
    return pd.DataFrame(data)