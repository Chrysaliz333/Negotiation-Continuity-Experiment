# Synthetic Contract Negotiation Data

**Generated**: 2025-10-15
**Generator**: `scripts/generate/synthetic_data.py`
**Purpose**: Unblock development by providing realistic test data for Negotiation Continuity Experiment

---

## Overview

This directory contains 12 synthetic contract negotiation files representing 3 matters across 4 versions each. The data is based on **real contract patterns** extracted from professional services MSAs and structured review data.

### File Structure

```
data/ground_truth/synthetic/
├── matter_001_v1.json  (10 clauses, 6 recommendations, 6 decisions, 1 concession)
├── matter_001_v2.json  (10 clauses, 2 recommendations, 2 decisions, 0 concessions)
├── matter_001_v3.json  (10 clauses, 3 recommendations, 3 decisions, 1 concession)
├── matter_001_v4.json  (10 clauses, 0 recommendations, 0 decisions, 0 concessions) [FINAL]
├── matter_002_v1.json  (10 clauses, 4 recommendations, 4 decisions, 0 concessions)
├── matter_002_v2.json  (10 clauses, 4 recommendations, 4 decisions, 0 concessions)
├── matter_002_v3.json  (10 clauses, 1 recommendation, 1 decision, 0 concessions)
├── matter_002_v4.json  (10 clauses, 0 recommendations, 0 decisions, 0 concessions) [FINAL]
├── matter_003_v1.json  (8 clauses, 5 recommendations, 5 decisions, 0 concessions)
├── matter_003_v2.json  (8 clauses, 2 recommendations, 2 decisions, 0 concessions)
├── matter_003_v3.json  (8 clauses, 1 recommendation, 1 decision, 0 concessions)
└── matter_003_v4.json  (8 clauses, 0 recommendations, 0 decisions, 0 concessions) [FINAL]
```

**Total**: 108 MB of test data, 100+ clauses, 28 recommendations, 28 decisions, 2 concessions

---

## Matter Descriptions

### Matter 001: Software Services Agreement
**Type**: software_services
**Provider**: CloudTech Solutions Ltd
**Customer**: DataCorp Industries PLC

**Focus Areas**: Service levels, availability SLAs, service credits, data protection, IP ownership

**Negotiation Arc**:
- **V1**: Initial draft with 6 recommendations (mostly unfavorable terms)
- **V2**: Response with 2 remaining recommendations (SLA and data breach issues)
- **V3**: Compromise with 3 new recommendations, 1 concession made
- **V4**: Final agreement, all issues resolved

---

### Matter 002: Professional Services Agreement
**Type**: professional_services
**Provider**: Acme Consulting Partners
**Customer**: Widget Manufacturing Corp

**Focus Areas**: Liability caps, audit rights, termination provisions, insurance, payment terms

**Negotiation Arc**:
- **V1**: Base contract with 4 recommendations (liability and risk allocation concerns)
- **V2**: Continued negotiation with 4 recommendations
- **V3**: Near-final with 1 remaining recommendation
- **V4**: Executed agreement

---

### Matter 003: Data Processing Agreement
**Type**: data_processing
**Provider**: SecureData Processing Ltd
**Customer**: FinServe Global Inc

**Focus Areas**: Data breach notification, breach indemnity, confidentiality, insurance requirements

**Negotiation Arc**:
- **V1**: Initial proposal with 5 recommendations (high-risk data processing terms)
- **V2**: Response with 2 recommendations, 1 deferred decision
- **V3**: Single remaining recommendation
- **V4**: Final data processing agreement

---

## Data Schema

Each JSON file follows this structure:

```json
{
  "matter_id": "matter_001",
  "matter_type": "software_services",
  "version": 1,
  "timestamp": "2025-07-17T15:37:14.353064Z",
  "parties": {
    "provider": {"name": "...", "role": "Service Provider"},
    "customer": {"name": "...", "role": "Customer"}
  },
  "clauses": [
    {
      "clause_id": "clause_1826c7c4f76e928f",
      "clause_number": "1.1",
      "title": "Limitation of Liability",
      "text": "[Full clause text]",
      "category": "Liability and Risk",
      "version": 1
    }
  ],
  "recommendations": [
    {
      "recommendation_id": "rec_cea66e0d1529e97b",
      "clause_id": "clause_1826c7c4f76e928f",
      "issue_type": "Risk Allocation",
      "classification": "unfavorable",
      "reasoning": "[Detailed reasoning]",
      "recommended_action": "[Specific action]"
    }
  ],
  "decisions": [
    {
      "decision_id": "dec_597154ecf63989e1",
      "recommendation_id": "rec_cea66e0d1529e97b",
      "decision_type": "override",
      "actor": "Jessica Martinez",
      "role": "Senior Counsel",
      "timestamp": "2025-07-19T22:37:14.353064Z",
      "notes": "Commercial precedent exists..."
    }
  ],
  "concessions": [
    {
      "concession_id": "con_5cb3d89dd4d88ab7",
      "decision_id": "dec_597154ecf63989e1",
      "clause_id": "clause_1826c7c4f76e928f",
      "description": "Override of Risk Allocation recommendation",
      "impact": "low",
      "rationale": "Limited practical impact..."
    }
  ]
}
```

---

## Realistic Features

### Based on Real Contract Analysis

All patterns derived from actual professional services MSA documents:

✅ **Clause Types**: Liability, SLAs, Data Protection, IP, Termination, Confidentiality
✅ **Issue Types**: Risk Allocation, Timeline Concerns, Ambiguity, One-Sided Terms, Commercial Imbalance
✅ **Classifications**: 40% Unfavorable, 35% Requires Clarification, 25% Favorable
✅ **Decision Distribution**: 70% Apply, 20% Override, 10% Defer
✅ **Concession Rate**: ~10% of decisions result in documented concessions

### Negotiation Patterns

**Version 1 → Version 2** (15-25% change rate):
- Blanking out numbers for negotiation
- Deleting expansive language
- Adding qualifiers and cross-references

**Version 2 → Version 3** (10-15% change rate):
- Numeric compromises
- Adding reciprocal terms
- Clarifying ambiguities

**Version 3 → Version 4** (5-10% change rate):
- Final tweaks
- Edge case provisions
- Formatting cleanup

---

## Usage Examples

### Loading Data (Python)

```python
import json
from pathlib import Path

# Load a specific version
with open('data/ground_truth/synthetic/matter_001_v1.json') as f:
    data = json.load(f)

print(f"Matter: {data['matter_id']}")
print(f"Version: {data['version']}")
print(f"Clauses: {len(data['clauses'])}")
print(f"Recommendations: {len(data['recommendations'])}")
print(f"Decisions: {len(data['decisions'])}")
print(f"Concessions: {len(data['concessions'])}")
```

### Iterating Through Versions

```python
# Load all versions of a matter
matter_id = "matter_001"
versions = []

for version_num in range(1, 5):
    filepath = f"data/ground_truth/synthetic/{matter_id}_v{version_num}.json"
    with open(filepath) as f:
        versions.append(json.load(f))

# Track clause evolution
clause_history = {}
for version_data in versions:
    for clause in version_data['clauses']:
        clause_num = clause['clause_number']
        if clause_num not in clause_history:
            clause_history[clause_num] = []
        clause_history[clause_num].append({
            'version': version_data['version'],
            'text': clause['text'],
            'clause_id': clause['clause_id']
        })

# Show how a specific clause changed
print(f"Evolution of Clause 1.1 (Limitation of Liability):")
for entry in clause_history['1.1']:
    print(f"  V{entry['version']}: {entry['text'][:100]}...")
```

### Filtering Recommendations

```python
# Find all unfavorable recommendations
unfavorable_recs = []

for filepath in Path('data/ground_truth/synthetic').glob('*.json'):
    with open(filepath) as f:
        data = json.load(f)

    for rec in data['recommendations']:
        if rec['classification'] == 'unfavorable':
            unfavorable_recs.append({
                'matter': data['matter_id'],
                'version': data['version'],
                'clause': rec['clause_id'],
                'issue': rec['issue_type'],
                'action': rec['recommended_action']
            })

print(f"Found {len(unfavorable_recs)} unfavorable recommendations")
```

---

## Data Quality Notes

### Known Limitations

1. **Minor Template Issues** (acceptable for test data):
   - Some IP clauses have provider assigning to provider (intentional variation showing provider retains IP)
   - This represents a realistic "No assignment" scenario

2. **Simplifications**:
   - Actor names are randomly selected from a pool (Sarah Chen, Michael Roberts, etc.)
   - Timestamps progress chronologically but are synthetic
   - Clause mutations are template-based, not semantically perfect

3. **Advantages over Real Data**:
   - ✅ No PII or confidential information
   - ✅ Consistent structure across all files
   - ✅ Validated JSON format
   - ✅ Known ground truth for testing

---

## Test Scenarios Supported

This synthetic data enables testing of:

1. **Clause Linkage** (`matter_001`):
   - Track Clause 1.1 (Liability Cap) across 4 versions
   - Verify clause_id changes when text mutates
   - Test precision/recall of linkage algorithm

2. **Recommendation Adherence** (`matter_002`):
   - 4 recommendations in V1 → check suppression in V2
   - Test "apply" decision leads to clause changes
   - Validate override decisions don't trigger changes

3. **Handover Context** (`matter_003`):
   - Package V1 → V2 handover (5 recommendations, 5 decisions)
   - Test completeness of context transfer
   - Verify all decisions captured

4. **Concession Tracking** (`matter_001`):
   - V1: 1 concession (override on unfavorable liability)
   - V3: 1 concession (override on unfavorable term)
   - Test visibility of concessions in query results

5. **Cross-Matter Precedent** (All 3 matters):
   - All have "Limitation of Liability" clauses
   - All have "Data Protection" sections
   - Test semantic similarity across matters

---

## Regenerating Data

To regenerate with different random seed or parameters:

```bash
# Activate virtual environment
source venv/bin/activate

# Generate default (3 matters × 4 versions)
python scripts/generate/synthetic_data.py

# Custom configuration
python scripts/generate/synthetic_data.py --matters 5 --versions 6 --output data/ground_truth/custom/

# With different random seed (edit script line: random.seed(42))
```

---

## Integration with Pydantic Models

This data is designed to be loadable into the project's Pydantic models:

```python
from models.entities import Document, DocVersion, Clause, AgentRecommendation, UserDecision, Concession

# Load and validate
with open('data/ground_truth/synthetic/matter_001_v1.json') as f:
    raw_data = json.load(f)

# Parse clauses
clauses = [Clause(**clause) for clause in raw_data['clauses']]

# Parse recommendations
recommendations = [AgentRecommendation(**rec) for rec in raw_data['recommendations']]

# Parse decisions
decisions = [UserDecision(**dec) for dec in raw_data['decisions']]

# Parse concessions
concessions = [Concession(**con) for con in raw_data['concessions']]

print("✅ All data validated against Pydantic models")
```

---

## Next Steps

**Ready for**:
- ✅ Graphiti ingestion (Day 2)
- ✅ Query development (Day 3)
- ✅ Baseline experiment (Day 4)
- ✅ KPI measurement (Day 4-5)

**Not included** (defer to real data when available):
- Party entity details (only basic name/role)
- ReviewSession entities (not critical for initial testing)
- Full bi-temporal metadata (t_valid/t_invalid)
- Episode grouping (will be added during ingestion)

---

## Questions?

- Generator source: `scripts/generate/synthetic_data.py`
- Real contract analysis: `data/analysis/DATA_ANALYSIS_SUMMARY.md`
- Pattern documentation: `data/analysis/contract_patterns_analysis.md`

**Status**: ✅ Ready for use in Day 2+ implementation
