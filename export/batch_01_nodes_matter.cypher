// Negotiation Continuity Knowledge Graph
// Export for FalkorDB Cloud Import
// ======================================================================

// Matter Nodes
// ----------------------------------------------------------------------
CREATE (:Matter {matter_id: "matter_001", matter_type: "software_services", version: 1, timestamp: "2025-07-17T15:37:14.353064Z"})
CREATE (:Matter {matter_id: "matter_001", matter_type: "software_services", version: 2, timestamp: "2025-07-31T15:37:14.353064Z"})
CREATE (:Matter {matter_id: "matter_001", matter_type: "software_services", version: 3, timestamp: "2025-08-14T15:37:14.353064Z"})
CREATE (:Matter {matter_id: "matter_001", matter_type: "software_services", version: 4, timestamp: "2025-08-28T15:37:14.353064Z"})
CREATE (:Matter {matter_id: "matter_002", matter_type: "professional_services", version: 1, timestamp: "2025-07-17T15:37:14.354941Z"})
CREATE (:Matter {matter_id: "matter_002", matter_type: "professional_services", version: 2, timestamp: "2025-07-31T15:37:14.354941Z"})
CREATE (:Matter {matter_id: "matter_002", matter_type: "professional_services", version: 3, timestamp: "2025-08-14T15:37:14.354941Z"})
CREATE (:Matter {matter_id: "matter_002", matter_type: "professional_services", version: 4, timestamp: "2025-08-28T15:37:14.354941Z"})
CREATE (:Matter {matter_id: "matter_003", matter_type: "data_processing", version: 1, timestamp: "2025-07-17T15:37:14.356173Z"})
CREATE (:Matter {matter_id: "matter_003", matter_type: "data_processing", version: 2, timestamp: "2025-07-31T15:37:14.356173Z"})
CREATE (:Matter {matter_id: "matter_003", matter_type: "data_processing", version: 3, timestamp: "2025-08-14T15:37:14.356173Z"})
CREATE (:Matter {matter_id: "matter_003", matter_type: "data_processing", version: 4, timestamp: "2025-08-28T15:37:14.356173Z"})

// Party Nodes
// ----------------------------------------------------------------------
CREATE (:Party {name: "CloudTech Solutions Ltd", role: "Service Provider", matter_id: "matter_001"})
CREATE (:Party {name: "DataCorp Industries PLC", role: "Customer", matter_id: "matter_001"})
CREATE (:Party {name: "CloudTech Solutions Ltd", role: "Service Provider", matter_id: "matter_001"})
CREATE (:Party {name: "DataCorp Industries PLC", role: "Customer", matter_id: "matter_001"})
CREATE (:Party {name: "CloudTech Solutions Ltd", role: "Service Provider", matter_id: "matter_001"})
CREATE (:Party {name: "DataCorp Industries PLC", role: "Customer", matter_id: "matter_001"})
CREATE (:Party {name: "CloudTech Solutions Ltd", role: "Service Provider", matter_id: "matter_001"})
CREATE (:Party {name: "DataCorp Industries PLC", role: "Customer", matter_id: "matter_001"})
CREATE (:Party {name: "Acme Consulting Partners", role: "Service Provider", matter_id: "matter_002"})
CREATE (:Party {name: "Widget Manufacturing Corp", role: "Customer", matter_id: "matter_002"})
CREATE (:Party {name: "Acme Consulting Partners", role: "Service Provider", matter_id: "matter_002"})
CREATE (:Party {name: "Widget Manufacturing Corp", role: "Customer", matter_id: "matter_002"})
CREATE (:Party {name: "Acme Consulting Partners", role: "Service Provider", matter_id: "matter_002"})
CREATE (:Party {name: "Widget Manufacturing Corp", role: "Customer", matter_id: "matter_002"})
CREATE (:Party {name: "Acme Consulting Partners", role: "Service Provider", matter_id: "matter_002"})
CREATE (:Party {name: "Widget Manufacturing Corp", role: "Customer", matter_id: "matter_002"})
CREATE (:Party {name: "SecureData Processing Ltd", role: "Service Provider", matter_id: "matter_003"})
CREATE (:Party {name: "FinServe Global Inc", role: "Customer", matter_id: "matter_003"})
CREATE (:Party {name: "SecureData Processing Ltd", role: "Service Provider", matter_id: "matter_003"})
CREATE (:Party {name: "FinServe Global Inc", role: "Customer", matter_id: "matter_003"})
CREATE (:Party {name: "SecureData Processing Ltd", role: "Service Provider", matter_id: "matter_003"})
CREATE (:Party {name: "FinServe Global Inc", role: "Customer", matter_id: "matter_003"})
CREATE (:Party {name: "SecureData Processing Ltd", role: "Service Provider", matter_id: "matter_003"})
CREATE (:Party {name: "FinServe Global Inc", role: "Customer", matter_id: "matter_003"})

// Clause Nodes
// ----------------------------------------------------------------------
CREATE (:Clause {clause_id: "clause_1826c7c4f76e928f", clause_number: "1.1", title: "Limitation of Liability", category: "Liability and Risk", text_preview: "CloudTech Solutions Ltd's aggregate liability to DataCorp Industries PLC under this Agreement, whether arising in contract, tort (including negligence), or otherwise, shall not exceed in any consecuti...", version: 1, matter_id: "matter_001"})
CREATE (:Clause {clause_id: "clause_b0b523f60287d9ff", clause_number: "2.2", title: "Unlimited Liability Carve-Outs", category: "Liability and Risk", text_preview: "Nothing in this Agreement shall limit or exclude either Party's liability for: (a) death or personal injury caused by its negligence; (b) fraud or fraudulent misrepresentation; (c) gross negligence; (...", version: 1, matter_id: "matter_001"})
