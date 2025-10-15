#!/usr/bin/env python3
"""
Compare two contract versions to identify changes.
Used to inform synthetic data generation patterns.
"""

import sys
from pathlib import Path
from docx import Document
import difflib
from typing import List, Dict, Tuple


def extract_text(docx_path: Path) -> List[str]:
    """Extract all paragraph text from DOCX."""
    doc = Document(docx_path)
    return [para.text for para in doc.paragraphs if para.text.strip()]


def compare_documents(base_path: Path, round1_path: Path) -> Dict:
    """
    Compare two contract versions and identify changes.

    Returns:
        Dictionary with added, removed, and modified sections
    """
    base_paragraphs = extract_text(base_path)
    round1_paragraphs = extract_text(round1_path)

    # Use difflib to find differences
    differ = difflib.Differ()
    diff = list(differ.compare(base_paragraphs, round1_paragraphs))

    changes = {
        "added": [],
        "removed": [],
        "modified": [],
        "stats": {
            "base_paragraphs": len(base_paragraphs),
            "round1_paragraphs": len(round1_paragraphs),
            "total_changes": 0,
        }
    }

    i = 0
    while i < len(diff):
        line = diff[i]

        if line.startswith('- '):
            # Content removed
            removed_text = line[2:]
            changes["removed"].append(removed_text)
            changes["stats"]["total_changes"] += 1

        elif line.startswith('+ '):
            # Content added
            added_text = line[2:]
            changes["added"].append(added_text)
            changes["stats"]["total_changes"] += 1

        elif line.startswith('? '):
            # Indicates character-level differences (metadata)
            pass

        i += 1

    return changes


def identify_clause_changes(changes: Dict) -> List[Dict]:
    """
    Identify which clauses were affected by changes.

    Returns:
        List of clause-level change descriptions
    """
    clause_changes = []

    # Look for section headers in added/removed content
    for removed in changes["removed"]:
        # Check if this is a clause header
        if any([
            removed.strip().startswith(tuple(f"{i}." for i in range(1, 100))),
            "Section" in removed[:30],
            "[Heading" in removed,
        ]):
            clause_changes.append({
                "type": "removed",
                "clause": removed[:100],
                "full_text": removed,
            })

    for added in changes["added"]:
        if any([
            added.strip().startswith(tuple(f"{i}." for i in range(1, 100))),
            "Section" in added[:30],
            "[Heading" in added,
        ]):
            clause_changes.append({
                "type": "added",
                "clause": added[:100],
                "full_text": added,
            })

    return clause_changes


def find_modified_sections(base_path: Path, round1_path: Path) -> List[Dict]:
    """
    Find sections that appear in both but have been modified.
    Uses fuzzy matching to identify similar content.
    """
    base_paragraphs = extract_text(base_path)
    round1_paragraphs = extract_text(round1_path)

    modifications = []

    # Use SequenceMatcher to find close matches
    matcher = difflib.SequenceMatcher(None, base_paragraphs, round1_paragraphs)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            # Content was modified
            base_section = '\n'.join(base_paragraphs[i1:i2])
            round1_section = '\n'.join(round1_paragraphs[j1:j2])

            # Only report if sections are somewhat similar (modified, not completely different)
            similarity = difflib.SequenceMatcher(None, base_section, round1_section).ratio()

            if similarity > 0.5:  # At least 50% similar
                modifications.append({
                    "base": base_section[:200] + "..." if len(base_section) > 200 else base_section,
                    "round1": round1_section[:200] + "..." if len(round1_section) > 200 else round1_section,
                    "similarity": f"{similarity*100:.1f}%",
                    "location": f"Base lines {i1}-{i2}, Round1 lines {j1}-{j2}",
                })

    return modifications


def print_change_summary(changes: Dict, clause_changes: List[Dict], modifications: List[Dict]):
    """Print readable summary of changes."""
    print(f"\n{'='*80}")
    print("CONTRACT COMPARISON SUMMARY")
    print(f"{'='*80}\n")

    print("STATISTICS:")
    print(f"  Base document paragraphs: {changes['stats']['base_paragraphs']}")
    print(f"  Round 1 document paragraphs: {changes['stats']['round1_paragraphs']}")
    print(f"  Total line-level changes: {changes['stats']['total_changes']}")
    print(f"  Clause-level changes: {len(clause_changes)}")
    print(f"  Modified sections: {len(modifications)}")

    print(f"\n{'─'*80}")
    print("REMOVED CONTENT:")
    print(f"{'─'*80}\n")
    for i, removed in enumerate(changes["removed"][:10], 1):  # Show first 10
        print(f"{i}. {removed[:150]}...")
        print()

    if len(changes["removed"]) > 10:
        print(f"... and {len(changes['removed']) - 10} more removed items\n")

    print(f"{'─'*80}")
    print("ADDED CONTENT:")
    print(f"{'─'*80}\n")
    for i, added in enumerate(changes["added"][:10], 1):  # Show first 10
        print(f"{i}. {added[:150]}...")
        print()

    if len(changes["added"]) > 10:
        print(f"... and {len(changes['added']) - 10} more added items\n")

    if clause_changes:
        print(f"{'─'*80}")
        print("CLAUSE-LEVEL CHANGES:")
        print(f"{'─'*80}\n")
        for change in clause_changes[:20]:  # Show first 20
            print(f"[{change['type'].upper()}] {change['clause']}")
            print()

    if modifications:
        print(f"{'─'*80}")
        print("MODIFIED SECTIONS (TOP 10):")
        print(f"{'─'*80}\n")
        for i, mod in enumerate(modifications[:10], 1):
            print(f"{i}. Similarity: {mod['similarity']}, Location: {mod['location']}")
            print(f"   BASE: {mod['base']}")
            print(f"   ROUND1: {mod['round1']}")
            print()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compare_contracts.py <base.docx> <round1.docx>")
        sys.exit(1)

    base_path = Path(sys.argv[1])
    round1_path = Path(sys.argv[2])

    if not base_path.exists() or not round1_path.exists():
        print("Error: One or both files not found")
        sys.exit(1)

    # Compare documents
    changes = compare_documents(base_path, round1_path)
    clause_changes = identify_clause_changes(changes)
    modifications = find_modified_sections(base_path, round1_path)

    # Print summary
    print_change_summary(changes, clause_changes, modifications)
