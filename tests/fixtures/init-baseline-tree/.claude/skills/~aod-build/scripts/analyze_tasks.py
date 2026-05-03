#!/usr/bin/env python3
"""
Analyze tasks.md and extract completion metrics.

Usage:
    python analyze_tasks.py <path-to-tasks.md>

Output:
    JSON with task counts, progress percentage, phase breakdown, task range
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Any


def parse_tasks_file(file_path: str) -> Dict[str, Any]:
    """Parse tasks.md and extract metrics."""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract feature ID from path (e.g., "001-my-feature")
    feature_id = Path(file_path).parent.name

    # Count tasks
    completed_tasks = len(re.findall(r'^\s*- \[X\] T\d+', content, re.MULTILINE))
    total_tasks = len(re.findall(r'^\s*- \[[X ]\] T\d+', content, re.MULTILINE))

    # Calculate progress
    progress_percentage = round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0.0

    # Extract phases
    phases = []
    phase_pattern = r'^## (Phase \d+:[^#\n]+)'
    phase_matches = list(re.finditer(phase_pattern, content, re.MULTILINE))

    for i, match in enumerate(phase_matches):
        phase_name = match.group(1).strip()
        phase_start = match.end()

        # Find the end of this phase (start of next phase or end of file)
        if i + 1 < len(phase_matches):
            phase_end = phase_matches[i + 1].start()
        else:
            phase_end = len(content)

        phase_content = content[phase_start:phase_end]

        # Count tasks in this phase
        phase_completed = len(re.findall(r'^\s*- \[X\] T\d+', phase_content, re.MULTILINE))
        phase_total = len(re.findall(r'^\s*- \[[X ]\] T\d+', phase_content, re.MULTILINE))

        # Determine status
        if phase_total == 0:
            status = "empty"
        elif phase_completed == phase_total:
            status = "complete"
        elif phase_completed > 0:
            status = "partial"
        else:
            status = "pending"

        phases.append({
            "name": phase_name,
            "total": phase_total,
            "completed": phase_completed,
            "status": status,
            "percentage": round((phase_completed / phase_total * 100), 2) if phase_total > 0 else 0.0
        })

    # Find task range (first and last completed task)
    completed_task_ids = re.findall(r'^\s*- \[X\] (T\d+)', content, re.MULTILINE)

    if completed_task_ids:
        first_task = completed_task_ids[0]
        last_task = completed_task_ids[-1]
        task_range = f"{first_task}-{last_task}"
    else:
        task_range = "T000-T000"

    # Find next pending task
    next_task_match = re.search(r'^\s*- \[ \] (T\d+)', content, re.MULTILINE)
    next_task = next_task_match.group(1) if next_task_match else None

    # Build result
    result = {
        "feature_id": feature_id,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": total_tasks - completed_tasks,
        "progress_percentage": progress_percentage,
        "phases": phases,
        "task_range": task_range,
        "next_task": next_task,
        "first_completed_task": completed_task_ids[0] if completed_task_ids else None,
        "last_completed_task": completed_task_ids[-1] if completed_task_ids else None
    }

    return result


def format_phases_table(phases: List[Dict[str, Any]]) -> str:
    """Format phases as a markdown table."""

    if not phases:
        return "No phases found."

    lines = []
    lines.append("| Phase | Status | Tasks | Progress |")
    lines.append("|-------|--------|-------|----------|")

    for phase in phases:
        status_emoji = {
            "complete": "✅",
            "partial": "🔄",
            "pending": "⏳",
            "empty": "➖"
        }.get(phase["status"], "❓")

        lines.append(
            f"| {phase['name']} | {status_emoji} {phase['status'].title()} | "
            f"{phase['completed']}/{phase['total']} | {phase['percentage']}% |"
        )

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_tasks.py <path-to-tasks.md>", file=sys.stderr)
        sys.exit(1)

    tasks_file = sys.argv[1]

    if not Path(tasks_file).exists():
        print(f"Error: File not found: {tasks_file}", file=sys.stderr)
        sys.exit(1)

    try:
        result = parse_tasks_file(tasks_file)

        # Print JSON output
        print(json.dumps(result, indent=2))

        # Print summary to stderr (won't pollute JSON output)
        print(f"\n✓ Found {result['total_tasks']} total tasks", file=sys.stderr)
        print(f"✓ Found {result['completed_tasks']} completed tasks ({result['progress_percentage']}%)", file=sys.stderr)
        print(f"✓ Task range: {result['task_range']}", file=sys.stderr)
        if result['next_task']:
            print(f"✓ Next task: {result['next_task']}", file=sys.stderr)
        print(f"✓ Phases analyzed: {len(result['phases'])}", file=sys.stderr)

    except Exception as e:
        print(f"Error analyzing tasks file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
