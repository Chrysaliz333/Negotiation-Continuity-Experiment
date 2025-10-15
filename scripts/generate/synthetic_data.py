#!/usr/bin/env python3
"""
Synthetic Contract Negotiation Data Generator

Generates realistic contract negotiation scenarios with multiple versions,
recommendations, decisions, and concessions based on patterns from real contracts.

Usage:
    python synthetic_data.py --matters 3 --versions 4 --output data/ground_truth/synthetic/
"""

import argparse
import json
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


# Seed for reproducibility
random.seed(42)


@dataclass
class Party:
    """Contract party"""
    name: str
    role: str  # "Service Provider" or "Customer"


@dataclass
class Clause:
    """Contract clause"""
    clause_id: str
    clause_number: str
    title: str
    text: str
    category: str
    version: int


@dataclass
class Recommendation:
    """Agent recommendation for clause modification"""
    recommendation_id: str
    clause_id: str
    issue_type: str
    classification: str  # "favorable", "requires_clarification", "unfavorable"
    reasoning: str
    recommended_action: str


@dataclass
class Decision:
    """User decision on recommendation"""
    decision_id: str
    recommendation_id: str
    decision_type: str  # "apply", "override", "defer"
    actor: str
    role: str
    timestamp: str
    notes: str


@dataclass
class Concession:
    """Concession made during negotiation"""
    concession_id: str
    decision_id: str
    clause_id: str
    description: str
    impact: str  # "low", "medium", "high"
    rationale: str


# ============================================================================
# CLAUSE TEMPLATES - Based on real Professional Services MSA
# ============================================================================

CLAUSE_TEMPLATES = {
    "liability_cap": {
        "title": "Limitation of Liability",
        "category": "Liability and Risk",
        "base_text": "{provider}'s aggregate liability to {customer} under this Agreement, whether arising in contract, tort (including negligence), or otherwise, shall not exceed in any consecutive 12-month period the greater of: (a) {percentage}% of the total fees paid or payable by {customer} to {provider} during such 12-month period; or (b) {amount}.",
        "variations": {
            "percentage": [100, 125, 150, 175, 200],
            "amount": ["£1,000,000", "£2,000,000", "£3,500,000", "£5,000,000"],
        },
        "negotiation_intensity": "high",
    },

    "liability_carveouts": {
        "title": "Unlimited Liability Carve-Outs",
        "category": "Liability and Risk",
        "base_text": "Nothing in this Agreement shall limit or exclude either Party's liability for: (a) death or personal injury caused by its negligence; (b) fraud or fraudulent misrepresentation; (c) {carveout_items}.",
        "variations": {
            "carveout_items": [
                "gross negligence; (d) breach of confidentiality; (e) breach of data protection obligations; (f) infringement of Intellectual Property Rights; (g) regulatory penalties",
                "gross negligence; (d) breach of data protection obligations; (e) infringement of Intellectual Property Rights",
                "willful misconduct; (d) breach of data protection obligations",
                "willful misconduct only",
            ],
        },
        "negotiation_intensity": "high",
    },

    "sla_availability": {
        "title": "Service Level - Availability",
        "category": "Service Levels",
        "base_text": "{provider} shall maintain {system} availability of {percentage}% during Business Hours, measured monthly. Availability calculations shall exclude scheduled maintenance windows not exceeding {maintenance_hours} hours per month with {notice_days} Business Days' advance notice.",
        "variations": {
            "percentage": ["95.0", "99.0", "99.5", "99.9"],
            "system": ["Critical Services", "Standard Services", "the Services"],
            "maintenance_hours": ["4", "6", "8"],
            "notice_days": ["3", "5", "7", "10"],
        },
        "negotiation_intensity": "high",
    },

    "service_credits": {
        "title": "Service Credits",
        "category": "Service Levels",
        "base_text": "For each {increment}% shortfall below target availability, {customer} shall receive service credits equal to {credit_rate}% of monthly fees for the affected Services. Total service credits in any calendar month shall not exceed {cap}% of monthly fees.",
        "variations": {
            "increment": ["0.1", "0.5", "1.0"],
            "credit_rate": ["1", "2", "3", "5"],
            "cap": ["15", "20", "25", "30"],
        },
        "negotiation_intensity": "high",
    },

    "data_breach_notification": {
        "title": "Data Breach Notification",
        "category": "Data Protection",
        "base_text": "{provider} must promptly notify {customer} within {hours} hours of discovery of any actual or suspected security incident or Personal Data breach. {provider} must cooperate in all investigations and notify Data Subjects and regulators as required by law.",
        "variations": {
            "hours": ["4", "12", "24", "48", "72"],
        },
        "negotiation_intensity": "high",
    },

    "data_breach_liability": {
        "title": "Data Breach Indemnity",
        "category": "Data Protection",
        "base_text": "{provider} shall indemnify, defend, and hold harmless {customer} from and against any losses, damages, costs, and expenses arising from any Personal Data breach caused by {provider} or its subcontractors{liability_qualifier}.",
        "variations": {
            "liability_qualifier": [
                "",
                ", subject to the liability cap in Section 4.1",
                ", capped at 150% of annual fees except for willful misconduct",
                ", capped at 125% of annual fees",
            ],
        },
        "negotiation_intensity": "high",
    },

    "termination_convenience": {
        "title": "Termination for Convenience",
        "category": "Term and Termination",
        "base_text": "{party} may terminate this Agreement for convenience upon {days} days' prior written notice to the other Party{termination_fee}.",
        "variations": {
            "party": ["Either Party", "{customer}", "No Party"],
            "days": ["30", "60", "90", "120", "180"],
            "termination_fee": [
                "",
                ", subject to payment of a termination fee equal to {fee_amount}",
            ],
            "fee_amount": ["three months' fees", "six months' fees", "remaining contract value"],
        },
        "negotiation_intensity": "medium",
    },

    "audit_rights": {
        "title": "Audit Rights",
        "category": "Compliance",
        "base_text": "{customer} shall have the right to conduct audits of {provider}'s performance and compliance {frequency} upon {notice_days} Business Days' advance notice. Such audit rights shall survive termination for a period of {tail_period}.",
        "variations": {
            "frequency": ["at any time", "up to twice per year", "once per year"],
            "notice_days": ["5", "10", "15", "30"],
            "tail_period": ["six (6) months", "one (1) year", "eighteen (18) months", "two (2) years"],
        },
        "negotiation_intensity": "medium",
    },

    "ip_ownership": {
        "title": "Intellectual Property Ownership",
        "category": "Intellectual Property",
        "base_text": "All Deliverables, work product, and Intellectual Property created by {provider} under this Agreement shall be owned by {ip_owner}. {provider} hereby assigns all rights, title, and interest in such IP to {ip_owner}{background_ip}.",
        "variations": {
            "ip_owner": ["{customer}", "{provider}", "the Parties jointly"],
            "background_ip": [
                "",
                ", excluding {provider}'s Background IP and pre-existing materials",
                ". {provider} retains ownership of Background IP and grants {customer} a perpetual, royalty-free license",
            ],
        },
        "negotiation_intensity": "medium",
    },

    "confidentiality_term": {
        "title": "Confidentiality Obligations",
        "category": "Confidentiality",
        "base_text": "Each Party shall maintain the confidentiality of the other Party's Confidential Information and use it solely for purposes of this Agreement. These obligations shall survive termination for a period of {years} years{exceptions}.",
        "variations": {
            "years": ["2", "3", "5", "7"],
            "exceptions": [
                "",
                ", except for information that (a) is publicly available, (b) is independently developed, or (c) is required by law to be disclosed",
            ],
        },
        "negotiation_intensity": "low",
    },

    "payment_terms": {
        "title": "Payment Terms",
        "category": "Fees and Payment",
        "base_text": "{customer} shall pay all undisputed invoices within {days} days of receipt. Late payments shall accrue interest at {rate}% per annum{dispute_rights}.",
        "variations": {
            "days": ["15", "30", "45", "60"],
            "rate": ["1.5", "2.0", "3.0", "5.0"],
            "dispute_rights": [
                "",
                ". {customer} may dispute invoices in good faith within {dispute_days} days",
            ],
            "dispute_days": ["10", "15", "30"],
        },
        "negotiation_intensity": "medium",
    },

    "insurance_requirements": {
        "title": "Insurance Requirements",
        "category": "Insurance",
        "base_text": "{provider} shall maintain the following insurance coverage throughout the term: (a) Professional Indemnity Insurance of at least {pi_amount}; (b) Cyber Liability Insurance of at least {cyber_amount}; (c) General Liability Insurance of at least {gl_amount}.",
        "variations": {
            "pi_amount": ["£1,000,000", "£2,000,000", "£5,000,000"],
            "cyber_amount": ["£1,000,000", "£2,000,000", "£5,000,000"],
            "gl_amount": ["£1,000,000", "£2,000,000", "£5,000,000"],
        },
        "negotiation_intensity": "low",
    },
}


# ============================================================================
# ISSUE TYPES AND RECOMMENDATIONS
# ============================================================================

ISSUE_TYPES = {
    "risk_allocation": {
        "name": "Risk Allocation",
        "typical_classification": "unfavorable",
        "reasoning_templates": [
            "The {clause_aspect} exposes {party} to {risk_type} beyond reasonable commercial expectations. This creates significant financial risk that is disproportionate to the contract value.",
            "The allocation of {risk_type} is heavily weighted against {party}, with insufficient protections or caps in place.",
            "The {clause_aspect} lacks reciprocal obligations, creating a one-sided risk allocation that could result in {consequence}.",
        ],
        "action_templates": [
            "Propose reducing {metric} to {target_value} to align with industry standards and contract value.",
            "Add reciprocal {obligation_type} to balance risk allocation between parties.",
            "Introduce a cap on {risk_type} at {target_value} to limit maximum exposure.",
        ],
    },

    "timeline_concern": {
        "name": "Timeline Concern",
        "typical_classification": "unfavorable",
        "reasoning_templates": [
            "The {timeline} requirement is operationally challenging and may be impossible to meet in practice, particularly given {constraint}.",
            "The {timeline} does not provide sufficient time for {process}, which typically requires {realistic_timeline} under industry best practices.",
        ],
        "action_templates": [
            "Extend {timeline} from {current} to {proposed} to allow for realistic operational response.",
            "Clarify that {timeline} begins from {trigger_event} rather than {current_trigger}, providing more workable timeframe.",
        ],
    },

    "ambiguity": {
        "name": "Ambiguity",
        "typical_classification": "requires_clarification",
        "reasoning_templates": [
            "The term '{term}' is undefined and subject to interpretation, which could lead to disputes regarding {scope}.",
            "The clause lacks clarity on {aspect}, making it difficult to determine compliance obligations or measure performance.",
            "The phrase '{phrase}' is vague and could be interpreted differently by each Party, creating uncertainty around {obligation}.",
        ],
        "action_templates": [
            "Define '{term}' explicitly in the Definitions section to provide clarity and avoid disputes.",
            "Add specific criteria or metrics for determining {aspect} (e.g., {example_criteria}).",
            "Replace '{vague_phrase}' with objective standard such as '{specific_standard}'.",
        ],
    },

    "one_sided_term": {
        "name": "One-Sided Term",
        "typical_classification": "unfavorable",
        "reasoning_templates": [
            "The clause imposes {obligation} on {party} without any corresponding obligation on {counter_party}, creating an unbalanced commercial relationship.",
            "Only {party} has {obligation_type}, while {counter_party} has no equivalent responsibility, which is commercially unreasonable.",
        ],
        "action_templates": [
            "Add reciprocal {obligation} for {counter_party} to create balanced obligations.",
            "Introduce mutual {right} for both Parties to ensure fairness.",
        ],
    },

    "commercial_imbalance": {
        "name": "Commercial Imbalance",
        "typical_classification": "unfavorable",
        "reasoning_templates": [
            "The {commercial_term} is significantly more onerous than market standards for comparable agreements, potentially impacting {business_aspect}.",
            "The {metric} of {value} exceeds industry benchmarks (typically {benchmark}) by {percentage}%, creating undue commercial burden.",
        ],
        "action_templates": [
            "Adjust {commercial_term} to {market_value} to align with industry standards.",
            "Introduce {balancing_mechanism} to offset the impact of {onerous_term}.",
        ],
    },
}


ACTOR_NAMES = [
    ("Sarah Chen", "Senior Associate"),
    ("Michael Roberts", "Partner"),
    ("Emily Thompson", "Associate"),
    ("David Kumar", "Counsel"),
    ("Jessica Martinez", "Senior Counsel"),
    ("James Wilson", "Associate"),
    ("Rachel Kim", "Partner"),
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_id(prefix: str, *components: str) -> str:
    """Generate canonical ID using SHA256 hash"""
    content = "|".join(str(c) for c in components)
    hash_digest = hashlib.sha256(content.encode()).hexdigest()[:16]
    return f"{prefix}_{hash_digest}"


def weighted_choice(choices: List[Any], weights: List[float]) -> Any:
    """Make weighted random choice"""
    return random.choices(choices, weights=weights, k=1)[0]


def format_text(template: str, **kwargs) -> str:
    """Format template with variable substitution"""
    text = template
    for key, value in kwargs.items():
        if isinstance(value, dict):
            # Handle nested substitution
            for subkey, subvalue in value.items():
                text = text.replace(f"{{{key}.{subkey}}}", str(subvalue))
        else:
            text = text.replace(f"{{{key}}}", str(value))

    # Second pass: substitute any remaining provider/customer placeholders in variations
    if "provider" in kwargs:
        text = text.replace("{provider}", str(kwargs["provider"]))
    if "customer" in kwargs:
        text = text.replace("{customer}", str(kwargs["customer"]))

    return text


# ============================================================================
# CLAUSE GENERATION
# ============================================================================

def generate_clause(
    clause_template_key: str,
    clause_number: str,
    version: int,
    provider_name: str,
    customer_name: str,
    variation_overrides: Dict[str, Any] = None
) -> Clause:
    """Generate a single clause from template"""

    template = CLAUSE_TEMPLATES[clause_template_key]

    # Select variations (use overrides if provided, otherwise random)
    selected_vars = {}
    for var_name, var_options in template.get("variations", {}).items():
        if variation_overrides and var_name in variation_overrides:
            selected_vars[var_name] = variation_overrides[var_name]
        else:
            selected_vars[var_name] = random.choice(var_options)

    # Format text
    text = format_text(
        template["base_text"],
        provider=provider_name,
        customer=customer_name,
        **selected_vars
    )

    clause_id = generate_id("clause", clause_number, text[:50])

    return Clause(
        clause_id=clause_id,
        clause_number=clause_number,
        title=template["title"],
        text=text,
        category=template["category"],
        version=version,
    )


def mutate_clause_for_version(
    base_clause: Clause,
    version: int,
    mutation_type: str,
    provider_name: str,
    customer_name: str,
) -> Clause:
    """Mutate a clause for a new version based on negotiation patterns"""

    text = base_clause.text

    if mutation_type == "blank_numbers":
        # Replace numbers with [BLANK] for negotiation
        import re
        text = re.sub(r'\b\d+(\.\d+)?%', '[BLANK]%', text, count=1)
        text = re.sub(r'£[\d,]+', '£[BLANK]', text, count=1)
        text = re.sub(r'\b\d+\s+(days?|hours?|months?|years?)', '[BLANK] \\1', text, count=1)

    elif mutation_type == "delete_expansive":
        # Remove expansive language
        text = text.replace("cascading effects and derivative losses extending beyond direct contractual performance", "[DELETED]")
        text = text.replace("any and all", "any")
        text = text.replace("including without limitation", "including")

    elif mutation_type == "add_qualifier":
        # Add qualifiers
        if "shall" in text and "material" not in text:
            text = text.replace("shall", "shall, subject to reasonable efforts,", 1)
        if "liable for" in text and "direct" not in text:
            text = text.replace("liable for", "liable for direct", 1)

    elif mutation_type == "numeric_compromise":
        # Adjust numbers (compromise between versions)
        import re
        # Reduce percentages by ~20%
        percentages = re.findall(r'(\d+)%', text)
        if percentages:
            old_pct = int(percentages[0])
            new_pct = int(old_pct * 0.8)  # 20% reduction
            text = text.replace(f"{old_pct}%", f"{new_pct}%", 1)

    elif mutation_type == "add_reciprocal":
        # Add reciprocal obligations
        if customer_name in text and "Each Party" not in text:
            text = f"Each Party shall have reciprocal obligations. " + text

    # Generate new clause with mutated text
    clause_id = generate_id("clause", base_clause.clause_number, text[:50])

    return Clause(
        clause_id=clause_id,
        clause_number=base_clause.clause_number,
        title=base_clause.title,
        text=text,
        category=base_clause.category,
        version=version,
    )


# ============================================================================
# RECOMMENDATION GENERATION
# ============================================================================

def should_generate_recommendation(
    clause_template_key: str,
    version: int,
) -> bool:
    """Determine if recommendation should be generated for this clause"""

    intensity = CLAUSE_TEMPLATES[clause_template_key]["negotiation_intensity"]

    # High intensity clauses: 80% chance in v1, 40% in v2, 20% in v3
    # Medium intensity: 40% in v1, 20% in v2, 10% in v3
    # Low intensity: 10% in v1, 5% in v2-v4

    probabilities = {
        "high": {1: 0.8, 2: 0.4, 3: 0.2, 4: 0.05},
        "medium": {1: 0.4, 2: 0.2, 3: 0.1, 4: 0.05},
        "low": {1: 0.1, 2: 0.05, 3: 0.05, 4: 0.0},
    }

    prob = probabilities[intensity].get(version, 0.0)
    return random.random() < prob


def generate_recommendation(
    clause: Clause,
    matter_id: str,
    version: int,
) -> Recommendation:
    """Generate a recommendation for a clause"""

    # Select issue type weighted by typical classification
    issue_type_key = weighted_choice(
        list(ISSUE_TYPES.keys()),
        weights=[0.3, 0.25, 0.2, 0.15, 0.1],  # Favor risk_allocation
    )

    issue_type_data = ISSUE_TYPES[issue_type_key]

    # Determine classification (weighted toward typical)
    if issue_type_data["typical_classification"] == "unfavorable":
        classification = weighted_choice(
            ["unfavorable", "requires_clarification", "favorable"],
            weights=[0.6, 0.3, 0.1]
        )
    elif issue_type_data["typical_classification"] == "requires_clarification":
        classification = weighted_choice(
            ["requires_clarification", "unfavorable", "favorable"],
            weights=[0.5, 0.3, 0.2]
        )
    else:
        classification = "favorable"

    # Generate reasoning and action from templates
    reasoning_template = random.choice(issue_type_data["reasoning_templates"])
    action_template = random.choice(issue_type_data["action_templates"])

    # Fill in template placeholders with clause-specific content
    reasoning = format_text(
        reasoning_template,
        clause_aspect=clause.title,
        party="the Service Provider",
        risk_type="liability exposure",
        consequence="significant unbudgeted costs",
        constraint="operational limitations",
        process="proper investigation and notification",
        timeline="notification period",
        realistic_timeline="24-48 hours",
        term="reasonable efforts",
        scope="performance obligations",
        aspect="compliance standards",
        phrase="promptly notify",
        obligation="notification requirements",
        counter_party="the Customer",
        commercial_term="liability cap",
        business_aspect="risk management",
        metric="cap",
        value="150%",
        percentage="50",
        benchmark="100% of annual fees",
    )

    action = format_text(
        action_template,
        metric="liability cap",
        target_value="100% of annual fees or £2M",
        obligation_type="audit rights",
        risk_type="unlimited liability",
        timeline="notification period",
        current="4 hours",
        proposed="24 hours",
        trigger_event="actual knowledge by responsible personnel",
        current_trigger="discovery by any employee",
        term="reasonable efforts",
        aspect="compliance standards",
        example_criteria="ISO 27001 certification",
        vague_phrase="promptly notify",
        specific_standard="notify within 24 hours",
        obligation="indemnification",
        counter_party="Customer",
        right="audit rights",
        commercial_term="service credit cap",
        market_value="15-20%",
        balancing_mechanism="volume-based fee discounts",
        onerous_term="high credit cap",
    )

    rec_id = generate_id("rec", matter_id, str(version), clause.clause_id)

    return Recommendation(
        recommendation_id=rec_id,
        clause_id=clause.clause_id,
        issue_type=issue_type_data["name"],
        classification=classification,
        reasoning=reasoning,
        recommended_action=action,
    )


# ============================================================================
# DECISION GENERATION
# ============================================================================

def generate_decision(
    recommendation: Recommendation,
    matter_id: str,
    version: int,
    base_timestamp: datetime,
) -> Decision:
    """Generate a user decision on a recommendation"""

    # Decision type distribution: 70% apply, 20% override, 10% defer
    decision_type = weighted_choice(
        ["apply", "override", "defer"],
        weights=[0.7, 0.2, 0.1]
    )

    # Select actor
    actor_name, actor_role = random.choice(ACTOR_NAMES)

    # Generate notes based on decision type
    if decision_type == "apply":
        notes_options = [
            f"Agreed - {recommendation.recommended_action[:80]}...",
            f"Accept recommendation. {recommendation.issue_type} is significant risk.",
            "Approved as recommended by legal team.",
            f"Risk level justifies this change. Proceeding with modification.",
        ]
    elif decision_type == "override":
        notes_options = [
            "Commercial precedent exists with other customers at these terms.",
            f"Acceptable risk given fee structure and contract value.",
            f"Industry standard for {recommendation.issue_type} - override recommendation.",
            "Business team confirms this is market standard. No change needed.",
            "Already addressed in separate side letter agreement.",
        ]
    else:  # defer
        notes_options = [
            "Pending additional legal review before final decision.",
            "Need to consult with business stakeholders. Deferring for now.",
            "Awaiting vendor response to preliminary discussion.",
            "Require more information about operational impact.",
        ]

    notes = random.choice(notes_options)

    # Generate timestamp (within a few days of base)
    timestamp = base_timestamp + timedelta(hours=random.randint(1, 72))

    dec_id = generate_id("dec", matter_id, str(version), recommendation.recommendation_id)

    return Decision(
        decision_id=dec_id,
        recommendation_id=recommendation.recommendation_id,
        decision_type=decision_type,
        actor=actor_name,
        role=actor_role,
        timestamp=timestamp.isoformat() + "Z",
        notes=notes,
    )


# ============================================================================
# CONCESSION GENERATION
# ============================================================================

def should_generate_concession(decision: Decision, recommendation: Recommendation) -> bool:
    """Determine if a decision results in a concession"""

    # Concessions occur when:
    # 1. Override an unfavorable recommendation (accepting bad terms)
    # 2. Partially apply a recommendation but not fully (compromise that still exposes risk)

    if decision.decision_type == "override" and recommendation.classification == "unfavorable":
        return random.random() < 0.5  # 50% of unfavorable overrides = concessions

    return False


def generate_concession(
    decision: Decision,
    recommendation: Recommendation,
    clause: Clause,
    matter_id: str,
    version: int,
) -> Concession:
    """Generate a concession record"""

    # Determine impact
    impact = weighted_choice(
        ["low", "medium", "high"],
        weights=[0.3, 0.5, 0.2]
    )

    # Generate description
    descriptions = [
        f"Accepted {clause.category} terms despite legal recommendation to modify.",
        f"Override of {recommendation.issue_type} recommendation - retaining current clause language.",
        f"Conceded on {clause.title} to maintain commercial momentum.",
        f"Business decision to accept {recommendation.classification} terms in {clause.category}.",
    ]

    description = random.choice(descriptions)

    # Rationale based on impact
    if impact == "high":
        rationales = [
            "Critical to closing deal - customer unwilling to negotiate further on this point.",
            "Strategic relationship value outweighs legal risk in this specific clause.",
        ]
    elif impact == "medium":
        rationales = [
            "Acceptable risk given overall contract value and relationship importance.",
            "Mitigated through other contractual protections and insurance coverage.",
        ]
    else:  # low
        rationales = [
            "Limited practical impact based on historical experience.",
            "Low probability of this clause being invoked in practice.",
        ]

    rationale = random.choice(rationales)

    con_id = generate_id("con", matter_id, str(version), decision.decision_id)

    return Concession(
        concession_id=con_id,
        decision_id=decision.decision_id,
        clause_id=clause.clause_id,
        description=description,
        impact=impact,
        rationale=rationale,
    )


# ============================================================================
# MATTER GENERATION
# ============================================================================

def generate_matter(
    matter_id: str,
    matter_type: str,
    provider_name: str,
    customer_name: str,
    num_versions: int = 4,
) -> List[Dict[str, Any]]:
    """
    Generate a complete matter with multiple versions.

    Returns list of version dictionaries (one per version).
    """

    # Define which clauses to include for this matter type
    if matter_type == "software_services":
        clause_keys = [
            "liability_cap", "liability_carveouts", "sla_availability", "service_credits",
            "data_breach_notification", "data_breach_liability", "termination_convenience",
            "ip_ownership", "confidentiality_term", "payment_terms",
        ]
    elif matter_type == "professional_services":
        clause_keys = [
            "liability_cap", "liability_carveouts", "service_credits",
            "data_breach_notification", "audit_rights", "termination_convenience",
            "ip_ownership", "confidentiality_term", "payment_terms", "insurance_requirements",
        ]
    else:  # data_processing
        clause_keys = [
            "liability_cap", "data_breach_notification", "data_breach_liability",
            "audit_rights", "termination_convenience", "confidentiality_term",
            "payment_terms", "insurance_requirements",
        ]

    versions_data = []
    base_clauses = {}
    base_timestamp = datetime.now() - timedelta(days=90)  # Start 90 days ago

    for version in range(1, num_versions + 1):
        print(f"  Generating version {version}...")

        version_data = {
            "matter_id": matter_id,
            "matter_type": matter_type,
            "version": version,
            "timestamp": (base_timestamp + timedelta(days=(version-1)*14)).isoformat() + "Z",
            "parties": {
                "provider": {"name": provider_name, "role": "Service Provider"},
                "customer": {"name": customer_name, "role": "Customer"},
            },
            "clauses": [],
            "recommendations": [],
            "decisions": [],
            "concessions": [],
        }

        # Generate or mutate clauses
        for idx, clause_key in enumerate(clause_keys, start=1):
            clause_number = f"{idx}.{idx}"

            if version == 1:
                # Base version - generate from template
                clause = generate_clause(
                    clause_key, clause_number, version,
                    provider_name, customer_name
                )
                base_clauses[clause_key] = clause
            else:
                # Later versions - potentially mutate based on previous recommendations
                prev_version_data = versions_data[-1]

                # Check if there were recommendations for this clause in previous version
                prev_clause = next((c for c in prev_version_data["clauses"]
                                  if c["clause_number"] == clause_number), None)

                if prev_clause:
                    prev_recs = [r for r in prev_version_data["recommendations"]
                               if r["clause_id"] == prev_clause["clause_id"]]

                    if prev_recs:
                        # There were recommendations - apply mutations based on decisions
                        prev_decisions = [d for d in prev_version_data["decisions"]
                                        if d["recommendation_id"] in [r["recommendation_id"] for r in prev_recs]]

                        # If any "apply" decisions, mutate the clause
                        if any(d["decision_type"] == "apply" for d in prev_decisions):
                            mutation_types = ["numeric_compromise", "add_qualifier", "add_reciprocal"]
                            mutation = random.choice(mutation_types)

                            prev_clause_obj = Clause(**{k: v for k, v in prev_clause.items()})
                            clause = mutate_clause_for_version(
                                prev_clause_obj, version, mutation,
                                provider_name, customer_name
                            )
                        else:
                            # No apply decisions - keep previous version
                            clause = Clause(**{k: v for k, v in prev_clause.items()})
                            clause.version = version
                    else:
                        # No recommendations - keep previous version
                        clause = Clause(**{k: v for k, v in prev_clause.items()})
                        clause.version = version
                else:
                    # Shouldn't happen, but fallback
                    clause = base_clauses[clause_key]

            version_data["clauses"].append(asdict(clause))

            # Generate recommendations for this clause
            if should_generate_recommendation(clause_key, version):
                rec = generate_recommendation(clause, matter_id, version)
                version_data["recommendations"].append(asdict(rec))

                # Generate decision for this recommendation
                decision = generate_decision(rec, matter_id, version, base_timestamp)
                version_data["decisions"].append(asdict(decision))

                # Possibly generate concession
                if should_generate_concession(decision, rec):
                    concession = generate_concession(decision, rec, clause, matter_id, version)
                    version_data["concessions"].append(asdict(concession))

        versions_data.append(version_data)

    return versions_data


# ============================================================================
# MAIN GENERATION
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic contract negotiation data")
    parser.add_argument("--matters", type=int, default=3, help="Number of matters to generate")
    parser.add_argument("--versions", type=int, default=4, help="Number of versions per matter")
    parser.add_argument("--output", type=str, default="data/ground_truth/synthetic/",
                       help="Output directory")

    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    # Define matter scenarios
    matters = [
        {
            "matter_id": "matter_001",
            "matter_type": "software_services",
            "provider": "CloudTech Solutions Ltd",
            "customer": "DataCorp Industries PLC",
        },
        {
            "matter_id": "matter_002",
            "matter_type": "professional_services",
            "provider": "Acme Consulting Partners",
            "customer": "Widget Manufacturing Corp",
        },
        {
            "matter_id": "matter_003",
            "matter_type": "data_processing",
            "provider": "SecureData Processing Ltd",
            "customer": "FinServe Global Inc",
        },
    ]

    print(f"Generating {args.matters} matters with {args.versions} versions each...")
    print(f"Output directory: {output_path}")
    print()

    for idx, matter_config in enumerate(matters[:args.matters], start=1):
        print(f"Matter {idx}/{args.matters}: {matter_config['matter_id']} ({matter_config['matter_type']})")
        print(f"  Provider: {matter_config['provider']}")
        print(f"  Customer: {matter_config['customer']}")

        versions_data = generate_matter(
            matter_config["matter_id"],
            matter_config["matter_type"],
            matter_config["provider"],
            matter_config["customer"],
            args.versions,
        )

        # Save each version to separate JSON file
        for version_data in versions_data:
            filename = f"{matter_config['matter_id']}_v{version_data['version']}.json"
            filepath = output_path / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, indent=2, ensure_ascii=False)

            print(f"    ✓ Saved {filename} ({len(version_data['clauses'])} clauses, "
                  f"{len(version_data['recommendations'])} recommendations, "
                  f"{len(version_data['decisions'])} decisions, "
                  f"{len(version_data['concessions'])} concessions)")

        print()

    print(f"✅ Generation complete! Created {args.matters * args.versions} files in {output_path}")

    # Print summary statistics
    total_files = args.matters * args.versions
    print("\nSummary:")
    print(f"  Total files: {total_files}")
    print(f"  Matters: {args.matters}")
    print(f"  Versions per matter: {args.versions}")
    print(f"  Output directory: {output_path.absolute()}")


if __name__ == "__main__":
    main()
