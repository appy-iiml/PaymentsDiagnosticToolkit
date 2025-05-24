import pandas as pd

# Option descriptions for maturity levels
OPTION_DESCRIPTIONS = {
    "Basic": {
        "description": "Manual processes with limited automation. Basic functionality meets minimum requirements.",
        "value": 0.00
    },
    "Advanced": {
        "description": "Some automation implemented. Processes are documented and standardized.",
        "value": 0.33
    },
    "Leading": {
        "description": "Highly automated with digital workflows. Best practices implemented across the organization.",
        "value": 0.66
    },
    "Emerging": {
        "description": "Cutting-edge technology adoption. AI/ML integration and real-time processing capabilities.",
        "value": 1.00
    }
}

def load_process_details():
    """
    Load the complete process details for all 12 stages of payment processing
    
    Returns:
    - List of dictionaries containing process information
    """
    
    process_data = [
        # Stage 1: Payment Initiation & Data Capture
        {
            "qid": "1A",
            "stage": "Payment Initiation & Data Capture",
            "process": "Channel Setup & Session Management",
            "description": "Establishment and management of secure communication channels for payment initiation",
            "basic": "Basic web portal or mobile app with standard login. Limited channel options.",
            "advanced": "Multi-channel support (web, mobile, API) with session management and basic security.",
            "leading": "Omni-channel experience with seamless handoffs, advanced session management, and biometric authentication.",
            "emerging": "AI-powered channel optimization, predictive session management, and zero-touch authentication."
        },
        {
            "qid": "1B",
            "stage": "Payment Initiation & Data Capture",
            "process": "Data Input Validation & UX",
            "description": "User experience design and real-time validation of payment data entry",
            "basic": "Basic form validation with manual error checking. Standard HTML forms.",
            "advanced": "Real-time field validation with user-friendly error messages and guided input.",
            "leading": "Intelligent form completion with auto-suggestions, contextual help, and adaptive UX.",
            "emerging": "AI-powered input prediction, voice/gesture input, and personalized UX optimization."
        },
        {
            "qid": "1C",
            "stage": "Payment Initiation & Data Capture",
            "process": "Bulk Payment Processing",
            "description": "Handling of bulk payment files and batch processing capabilities",
            "basic": "Manual file upload with basic CSV/Excel support. Limited validation.",
            "advanced": "Automated file processing with multiple format support and batch validation.",
            "leading": "Intelligent bulk processing with error handling, parallel processing, and real-time status updates.",
            "emerging": "AI-driven file optimization, predictive error detection, and automated reconciliation."
        },
        {
            "qid": "1D",
            "stage": "Payment Initiation & Data Capture",
            "process": "Data Enrichment & Standardization",
            "description": "Enhancement and standardization of payment data for downstream processing",
            "basic": "Manual data entry with basic field mapping. Limited data validation.",
            "advanced": "Automated data enrichment with reference data lookup and field standardization.",
            "leading": "Real-time data enhancement with external data sources, ML-based data quality checks.",
            "emerging": "AI-powered data augmentation, predictive data completion, and autonomous data governance."
        },
        
        # Stage 2: Authentication & Identity Validation
        {
            "qid": "2A",
            "stage": "Authentication & Identity Validation",
            "process": "Multi-Factor Authentication",
            "description": "Implementation of robust authentication mechanisms for payment authorization",
            "basic": "Username/password with basic SMS OTP. Limited authentication factors.",
            "advanced": "Multi-factor authentication with email/SMS verification and security questions.",
            "leading": "Biometric authentication, hardware tokens, and adaptive authentication based on risk.",
            "emerging": "AI-driven behavioral authentication, continuous authentication, and zero-trust security."
        },
        {
            "qid": "2B",
            "stage": "Authentication & Identity Validation",
            "process": "Identity Verification & KYC",
            "description": "Customer identity verification and Know Your Customer compliance processes",
            "basic": "Manual document verification with basic identity checks.",
            "advanced": "Automated document scanning with basic OCR and identity database lookups.",
            "leading": "AI-powered identity verification with facial recognition, document authenticity checks.",
            "emerging": "Real-time biometric verification, blockchain identity, and zero-knowledge proofs."
        },
        {
            "qid": "2C",
            "stage": "Authentication & Identity Validation",
            "process": "Risk-Based Authentication",
            "description": "Dynamic authentication requirements based on transaction risk assessment",
            "basic": "Static authentication rules with manual risk assessment.",
            "advanced": "Rule-based risk scoring with automated authentication step-up.",
            "leading": "ML-based risk assessment with dynamic authentication requirements and behavioral analysis.",
            "emerging": "AI-driven continuous risk assessment with real-time adaptive authentication."
        },
        {
            "qid": "2D",
            "stage": "Authentication & Identity Validation",
            "process": "Session Security & Management",
            "description": "Secure session handling and protection against session-based attacks",
            "basic": "Basic session management with timeout controls.",
            "advanced": "Secure session handling with encryption and session monitoring.",
            "leading": "Advanced session protection with anomaly detection and automated session management.",
            "emerging": "AI-powered session security with predictive threat detection and zero-trust session handling."
        },
        
        # Stage 3: Pre-Submission Validation
        {
            "qid": "3A",
            "stage": "Pre-Submission Validation",
            "process": "Business Rules Engine",
            "description": "Automated validation of payment requests against business rules and policies",
            "basic": "Static rule checking with manual configuration. Limited rule complexity.",
            "advanced": "Configurable business rules engine with basic workflow automation.",
            "leading": "Advanced rules engine with machine learning integration and dynamic rule adaptation.",
            "emerging": "AI-powered rule optimization with self-learning capabilities and predictive rule suggestions."
        },
        {
            "qid": "3B",
            "stage": "Pre-Submission Validation",
            "process": "Data Quality & Completeness Checks",
            "description": "Comprehensive validation of data quality and completeness before processing",
            "basic": "Basic field validation with manual quality checks.",
            "advanced": "Automated data quality checks with comprehensive validation rules.",
            "leading": "ML-based data quality assessment with anomaly detection and auto-correction.",
            "emerging": "AI-driven data quality optimization with predictive data validation and autonomous data healing."
        },
        {
            "qid": "3C",
            "stage": "Pre-Submission Validation",
            "process": "Preliminary Fraud Screening",
            "description": "Initial fraud detection and risk assessment before payment submission",
            "basic": "Basic blacklist checking with manual fraud review.",
            "advanced": "Rule-based fraud detection with automated screening and alert generation.",
            "leading": "ML-based fraud detection with real-time scoring and adaptive thresholds.",
            "emerging": "AI-powered fraud prevention with behavioral analysis, graph analytics, and predictive modeling."
        },
        {
            "qid": "3D",
            "stage": "Pre-Submission Validation",
            "process": "Regulatory & Compliance Pre-Check",
            "description": "Initial compliance screening against regulatory requirements",
            "basic": "Manual compliance checking with basic regulatory rules.",
            "advanced": "Automated compliance screening with regulatory rule engine.",
            "leading": "Advanced compliance checking with real-time regulatory updates and ML-based assessment.",
            "emerging": "AI-driven regulatory compliance with predictive compliance scoring and autonomous regulatory adaptation."
        },
        
        # Stage 4: Payment Orchestration & Routing
        {
            "qid": "4A",
            "stage": "Payment Orchestration & Routing",
            "process": "Intelligent Payment Routing",
            "description": "Optimal routing of payments based on cost, speed, and success probability",
            "basic": "Static routing rules with manual configuration. Limited routing options.",
            "advanced": "Dynamic routing with basic optimization algorithms and multiple payment rails.",
            "leading": "AI-powered routing optimization with real-time performance monitoring and adaptive routing.",
            "emerging": "Self-learning routing engine with predictive analytics and autonomous route optimization."
        },
        {
            "qid": "4B",
            "stage": "Payment Orchestration & Routing",
            "process": "Cut-off Management & Scheduling",
            "description": "Management of payment cut-off times and optimal scheduling for processing",
            "basic": "Manual cut-off management with static schedules.",
            "advanced": "Automated cut-off handling with configurable schedules and notifications.",
            "leading": "Intelligent scheduling with optimization algorithms and real-time adjustments.",
            "emerging": "AI-driven cut-off optimization with predictive scheduling and autonomous timing decisions."
        },
        {
            "qid": "4C",
            "stage": "Payment Orchestration & Routing",
            "process": "Fee Calculation & Optimization",
            "description": "Dynamic fee calculation and optimization for payment processing",
            "basic": "Static fee structure with manual calculation.",
            "advanced": "Automated fee calculation with configurable fee structures.",
            "leading": "Dynamic fee optimization with market-based pricing and customer segmentation.",
            "emerging": "AI-powered fee optimization with real-time market analysis and personalized pricing."
        },
        {
            "qid": "4D",
            "stage": "Payment Orchestration & Routing",
            "process": "Exception Handling & Repair",
            "description": "Automated handling of payment exceptions and repair processes",
            "basic": "Manual exception handling with basic error logging.",
            "advanced": "Automated exception detection with workflow-based repair processes.",
            "leading": "Intelligent exception handling with ML-based root cause analysis and auto-repair.",
            "emerging": "AI-driven exception prevention with predictive failure detection and autonomous healing."
        },
        
        # Stage 5: Risk, Fraud & Compliance
        {
            "qid": "5A",
            "stage": "Risk, Fraud & Compliance",
            "process": "Advanced Fraud Detection",
            "description": "Sophisticated fraud detection using machine learning and behavioral analysis",
            "basic": "Rule-based fraud detection with basic pattern matching.",
            "advanced": "Advanced rule engine with basic machine learning models.",
            "leading": "Real-time ML-based fraud detection with behavioral analytics and graph analysis.",
            "emerging": "AI-powered fraud prevention with deep learning, ensemble models, and explainable AI."
        },
        {
            "qid": "5B",
            "stage": "Risk, Fraud & Compliance",
            "process": "Sanctions Screening",
            "description": "Comprehensive screening against sanctions lists and watch lists",
            "basic": "Basic name matching against static sanctions lists.",
            "advanced": "Automated sanctions screening with fuzzy matching and regular updates.",
            "leading": "Advanced screening with ML-enhanced matching and real-time list updates.",
            "emerging": "AI-powered sanctions detection with entity resolution and predictive screening."
        },
        {
            "qid": "5C",
            "stage": "Risk, Fraud & Compliance",
            "process": "AML & Transaction Monitoring",
            "description": "Anti-money laundering monitoring and suspicious activity detection",
            "basic": "Basic transaction monitoring with manual review processes.",
            "advanced": "Automated AML monitoring with configurable scenarios and alert generation.",
            "leading": "Advanced AML with ML-based pattern detection and intelligent case management.",
            "emerging": "AI-driven AML with behavioral analytics, network analysis, and predictive risk assessment."
        },
        {
            "qid": "5D",
            "stage": "Risk, Fraud & Compliance",
            "process": "Risk Assessment & Scoring",
            "description": "Comprehensive risk assessment and scoring for payment transactions",
            "basic": "Basic risk scoring with static rules and manual assessment.",
            "advanced": "Automated risk scoring with configurable models and real-time assessment.",
            "leading": "Advanced risk modeling with ML algorithms and adaptive scoring mechanisms.",
            "emerging": "AI-powered risk intelligence with predictive analytics and autonomous risk management."
        },
        
        # Stage 6: Final Authorisation & Approval
        {
            "qid": "6A",
            "stage": "Final Authorisation & Approval",
            "process": "Multi-Level Approval Workflow",
            "description": "Hierarchical approval processes based on transaction value and risk",
            "basic": "Manual approval processes with basic workflow management.",
            "advanced": "Automated workflow with configurable approval hierarchies and notifications.",
            "leading": "Intelligent workflow optimization with ML-based approval routing and decision support.",
            "emerging": "AI-driven approval optimization with predictive approval modeling and autonomous decision-making."
        },
        {
            "qid": "6B",
            "stage": "Final Authorisation & Approval",
            "process": "Final Compliance Check",
            "description": "Last-mile compliance verification before payment execution",
            "basic": "Manual compliance verification with basic checklist approach.",
            "advanced": "Automated compliance checking with comprehensive rule validation.",
            "leading": "Advanced compliance verification with real-time regulatory updates and ML-based assessment.",
            "emerging": "AI-powered compliance assurance with predictive compliance modeling and autonomous verification."
        },
        {
            "qid": "6C",
            "stage": "Final Authorisation & Approval",
            "process": "Dual Control & Segregation",
            "description": "Implementation of dual control mechanisms and segregation of duties",
            "basic": "Basic dual control with manual verification processes.",
            "advanced": "Automated dual control with role-based access and audit trails.",
            "leading": "Advanced segregation with dynamic controls and ML-based anomaly detection.",
            "emerging": "AI-enhanced dual control with behavioral monitoring and predictive control optimization."
        },
        {
            "qid": "6D",
            "stage": "Final Authorisation & Approval",
            "process": "Final Risk Validation",
            "description": "Ultimate risk assessment before payment execution",
            "basic": "Basic risk validation with manual oversight.",
            "advanced": "Automated risk validation with comprehensive risk models.",
            "leading": "Advanced risk validation with real-time risk assessment and adaptive thresholds.",
            "emerging": "AI-powered risk validation with predictive risk modeling and autonomous risk decisions."
        },
        
        # Stage 7: Message Generation & Transformation
        {
            "qid": "7A",
            "stage": "Message Generation & Transformation",
            "process": "Message Format Transformation",
            "description": "Conversion of payment instructions into appropriate message formats",
            "basic": "Manual message formatting with basic template systems.",
            "advanced": "Automated message transformation with configurable format templates.",
            "leading": "Intelligent message transformation with format optimization and validation.",
            "emerging": "AI-powered message generation with adaptive formatting and predictive optimization."
        },
        {
            "qid": "7B",
            "stage": "Message Generation & Transformation",
            "process": "Protocol Translation & Mapping",
            "description": "Translation between different payment protocols and message standards",
            "basic": "Manual protocol mapping with static translation rules.",
            "advanced": "Automated protocol translation with configurable mapping rules.",
            "leading": "Intelligent protocol translation with adaptive mapping and format optimization.",
            "emerging": "AI-driven protocol translation with self-learning mapping and predictive format selection."
        },
        {
            "qid": "7C",
            "stage": "Message Generation & Transformation",
            "process": "Message Validation & Integrity",
            "description": "Validation of message integrity and compliance with format standards",
            "basic": "Basic message validation with manual integrity checks.",
            "advanced": "Automated message validation with comprehensive format checking.",
            "leading": "Advanced validation with ML-based anomaly detection and auto-correction capabilities.",
            "emerging": "AI-powered message integrity with predictive validation and autonomous message healing."
        },
        {
            "qid": "7D",
            "stage": "Message Generation & Transformation",
            "process": "Message Repair & Error Handling",
            "description": "Automated repair of message formatting errors and handling of transformation failures",
            "basic": "Manual message repair with basic error handling.",
            "advanced": "Automated error detection with workflow-based repair processes.",
            "leading": "Intelligent message repair with ML-based error prediction and auto-correction.",
            "emerging": "AI-driven message healing with predictive error prevention and autonomous repair."
        },
        
        # Stage 8: Transmission, Clearing & ACK
        {
            "qid": "8A",
            "stage": "Transmission, Clearing & ACK",
            "process": "Secure Message Transmission",
            "description": "Secure transmission of payment messages to clearing networks",
            "basic": "Basic secure transmission with standard encryption protocols.",
            "advanced": "Advanced transmission security with multiple encryption layers and monitoring.",
            "leading": "Intelligent transmission with adaptive security and real-time threat detection.",
            "emerging": "AI-powered transmission security with predictive threat prevention and quantum-safe encryption."
        },
        {
            "qid": "8B",
            "stage": "Transmission, Clearing & ACK",
            "process": "Clearing Network Integration",
            "description": "Integration with various clearing networks and payment rails",
            "basic": "Basic integration with limited clearing networks.",
            "advanced": "Multi-network integration with automated routing and failover capabilities.",
            "leading": "Intelligent network selection with performance optimization and adaptive routing.",
            "emerging": "AI-driven network optimization with predictive routing and autonomous network management."
        },
        {
            "qid": "8C",
            "stage": "Transmission, Clearing & ACK",
            "process": "Acknowledgment Processing",
            "description": "Processing of acknowledgments and status updates from clearing networks",
            "basic": "Manual processing of acknowledgments with basic status tracking.",
            "advanced": "Automated acknowledgment processing with status monitoring and exception handling.",
            "leading": "Intelligent acknowledgment processing with ML-based pattern recognition and predictive status analysis.",
            "emerging": "AI-powered status intelligence with predictive acknowledgment processing and autonomous status management."
        },
        {
            "qid": "8D",
            "stage": "Transmission, Clearing & ACK",
            "process": "Performance Monitoring & SLA Management",
            "description": "Real-time monitoring of transmission performance and SLA compliance",
            "basic": "Basic performance monitoring with manual SLA tracking.",
            "advanced": "Automated performance monitoring with SLA alerting and reporting.",
            "leading": "Advanced performance analytics with predictive SLA management and optimization.",
            "emerging": "AI-driven performance optimization with predictive analytics and autonomous SLA management."
        },
        
        # Stage 9: Settlement & Funds Movement
        {
            "qid": "9A",
            "stage": "Settlement & Funds Movement",
            "process": "Settlement Processing",
            "description": "Processing of settlement instructions and funds movement coordination",
            "basic": "Manual settlement processing with basic fund transfer capabilities.",
            "advanced": "Automated settlement with real-time processing and exception handling.",
            "leading": "Intelligent settlement optimization with ML-based timing and liquidity management.",
            "emerging": "AI-powered settlement with predictive optimization and autonomous funds management."
        },
        {
            "qid": "9B",
            "stage": "Settlement & Funds Movement",
            "process": "Liquidity Management",
            "description": "Optimization of liquidity across accounts and payment rails",
            "basic": "Manual liquidity management with basic account monitoring.",
            "advanced": "Automated liquidity optimization with real-time monitoring and alerting.",
            "leading": "Advanced liquidity management with ML-based forecasting and optimization algorithms.",
            "emerging": "AI-driven liquidity intelligence with predictive analytics and autonomous liquidity optimization."
        },
        {
            "qid": "9C",
            "stage": "Settlement & Funds Movement",
            "process": "Cross-Border Settlement",
            "description": "Management of cross-border settlement processes and currency conversion",
            "basic": "Manual cross-border processing with basic currency conversion.",
            "advanced": "Automated cross-border settlement with real-time FX rates and compliance checking.",
            "leading": "Intelligent cross-border optimization with ML-based FX optimization and corridor selection.",
            "emerging": "AI-powered cross-border intelligence with predictive FX management and autonomous corridor optimization."
        },
        {
            "qid": "9D",
            "stage": "Settlement & Funds Movement",
            "process": "Settlement Risk Management",
            "description": "Management of settlement risk and mitigation strategies",
            "basic": "Basic settlement risk monitoring with manual risk assessment.",
            "advanced": "Automated settlement risk management with real-time monitoring and mitigation strategies.",
            "leading": "Advanced risk management with ML-based risk prediction and adaptive mitigation.",
            "emerging": "AI-driven settlement risk intelligence with predictive analytics and autonomous risk management."
        },
        
        # Stage 10: Reconciliation & Exceptions
        {
            "qid": "10A",
            "stage": "Reconciliation & Exceptions",
            "process": "Automated Reconciliation",
            "description": "Automated matching and reconciliation of payment transactions",
            "basic": "Manual reconciliation with basic matching algorithms.",
            "advanced": "Automated reconciliation with intelligent matching and exception reporting.",
            "leading": "Advanced reconciliation with ML-based matching and predictive exception detection.",
            "emerging": "AI-powered reconciliation with deep learning matching and autonomous exception resolution."
        },
        {
            "qid": "10B",
            "stage": "Reconciliation & Exceptions",
            "process": "Exception Investigation & Resolution",
            "description": "Investigation and resolution of reconciliation exceptions and breaks",
            "basic": "Manual exception investigation with basic workflow management.",
            "advanced": "Automated exception detection with workflow-based investigation and resolution.",
            "leading": "Intelligent exception handling with ML-based root cause analysis and automated resolution.",
            "emerging": "AI-driven exception intelligence with predictive exception prevention and autonomous resolution."
        },
        {
            "qid": "10C",
            "stage": "Reconciliation & Exceptions",
            "process": "Nostro/Vostro Account Management",
            "description": "Management and reconciliation of correspondent banking relationships",
            "basic": "Manual nostro account management with basic reconciliation.",
            "advanced": "Automated nostro management with real-time monitoring and reconciliation.",
            "leading": "Intelligent account management with ML-based optimization and predictive analytics.",
            "emerging": "AI-powered account intelligence with predictive management and autonomous optimization."
        },
        {
            "qid": "10D",
            "stage": "Reconciliation & Exceptions",
            "process": "Customer Communication & Updates",
            "description": "Communication of payment status and exception information to customers",
            "basic": "Manual customer communication with basic notification systems.",
            "advanced": "Automated customer notifications with real-time status updates and exception alerts.",
            "leading": "Intelligent customer communication with personalized messaging and proactive notifications.",
            "emerging": "AI-powered customer engagement with predictive communication and autonomous customer service."
        },
        
        # Stage 11: Reporting, Analytics & Notifications
        {
            "qid": "11A",
            "stage": "Reporting, Analytics & Notifications",
            "process": "Real-Time Analytics & Dashboards",
            "description": "Real-time analytics and dashboard capabilities for payment monitoring",
            "basic": "Basic reporting with static dashboards and manual data extraction.",
            "advanced": "Automated reporting with interactive dashboards and real-time data visualization.",
            "leading": "Advanced analytics with ML-based insights and predictive dashboard capabilities.",
            "emerging": "AI-powered analytics with autonomous insight generation and predictive dashboard optimization."
        },
        {
            "qid": "11B",
            "stage": "Reporting, Analytics & Notifications",
            "process": "Customer Self-Service Reporting",
            "description": "Self-service reporting capabilities for customers and stakeholders",
            "basic": "Basic customer portal with limited reporting capabilities.",
            "advanced": "Comprehensive self-service portal with configurable reports and data export.",
            "leading": "Intelligent self-service with ML-based report recommendations and advanced analytics.",
            "emerging": "AI-powered self-service with autonomous report generation and predictive insights."
        },
        {
            "qid": "11C",
            "stage": "Reporting, Analytics & Notifications",
            "process": "Predictive Analytics & Insights",
            "description": "Advanced analytics for trend prediction and business intelligence",
            "basic": "Basic trend analysis with manual insight generation.",
            "advanced": "Automated trend analysis with configurable predictive models.",
            "leading": "Advanced predictive analytics with ML algorithms and automated insight generation.",
            "emerging": "AI-driven predictive intelligence with deep learning models and autonomous business insights."
        },
        {
            "qid": "11D",
            "stage": "Reporting, Analytics & Notifications",
            "process": "Stakeholder Notifications & Alerts",
            "description": "Intelligent notification system for stakeholders and decision makers",
            "basic": "Basic email notifications with manual alert configuration.",
            "advanced": "Automated notification system with configurable alerting rules and multi-channel delivery.",
            "leading": "Intelligent notification system with ML-based alert prioritization and personalized delivery.",
            "emerging": "AI-powered notification intelligence with predictive alerting and autonomous stakeholder engagement."
        },
        
        # Stage 12: Audit, Archival & Compliance
        {
            "qid": "12A",
            "stage": "Audit, Archival & Compliance",
            "process": "Comprehensive Audit Trail",
            "description": "Complete audit trail maintenance and compliance with regulatory requirements",
            "basic": "Basic audit logging with manual trail management.",
            "advanced": "Automated audit trail with comprehensive logging and search capabilities.",
            "leading": "Advanced audit management with ML-based anomaly detection and intelligent trail analysis.",
            "emerging": "AI-powered audit intelligence with predictive compliance monitoring and autonomous audit management."
        },
        {
            "qid": "12B",
            "stage": "Audit, Archival & Compliance",
            "process": "Data Archival & Retrieval",
            "description": "Long-term data archival and efficient retrieval mechanisms",
            "basic": "Basic data archival with manual retrieval processes.",
            "advanced": "Automated archival with indexed search and efficient retrieval mechanisms.",
            "leading": "Intelligent archival with ML-based data lifecycle management and optimized retrieval.",
            "emerging": "AI-driven archival intelligence with predictive data management and autonomous archival optimization."
        },
        {
            "qid": "12C",
            "stage": "Audit, Archival & Compliance",
            "process": "Regulatory Reporting",
            "description": "Automated generation and submission of regulatory reports",
            "basic": "Manual regulatory reporting with basic template systems.",
            "advanced": "Automated regulatory reporting with configurable templates and submission workflows.",
            "leading": "Intelligent regulatory reporting with ML-based data validation and adaptive reporting.",
            "emerging": "AI-powered regulatory intelligence with predictive compliance reporting and autonomous regulatory management."
        },
        {
            "qid": "12D",
            "stage": "Audit, Archival & Compliance",
            "process": "Compliance Monitoring & Management",
            "description": "Continuous compliance monitoring and proactive management",
            "basic": "Manual compliance monitoring with basic checklist approach.",
            "advanced": "Automated compliance monitoring with real-time alerting and exception management.",
            "leading": "Advanced compliance management with ML-based monitoring and predictive compliance assessment.",
            "emerging": "AI-driven compliance intelligence with predictive monitoring and autonomous compliance management."
        }
    ]
    
    return process_data
