#!/usr/bin/env python3
"""
Generate checkpoint report from template.

Usage:
    python generate_checkpoint.py \
        --tasks-file specs/001-my-feature/tasks.md \
        --output-dir specs/001-my-feature \
        --description "Phase1-2-Complete"
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


def load_analysis(tasks_file: str) -> Dict[str, Any]:
    """Run analyze_tasks.py and load JSON output."""

    script_dir = Path(__file__).parent
    analyze_script = script_dir / "analyze_tasks.py"

    result = subprocess.run(
        ["python3", str(analyze_script), tasks_file],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Error running analyze_tasks.py: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    return json.loads(result.stdout)


def detect_checkpoint_number(output_dir: str) -> str:
    """Auto-detect next checkpoint number by looking at existing checkpoints."""

    output_path = Path(output_dir)
    if not output_path.exists():
        return "01"

    existing = list(output_path.glob("CHECKPOINT-*.md"))

    if not existing:
        return "01"

    # Extract numbers from existing checkpoints
    numbers = []
    for file in existing:
        match = re.match(r'CHECKPOINT-(\d+)', file.name)
        if match:
            numbers.append(int(match.group(1)))

    if not numbers:
        return "01"

    next_num = max(numbers) + 1
    return f"{next_num:02d}"


def prompt_user_input() -> Dict[str, Any]:
    """Prompt user for checkpoint context."""

    print("\n" + "="*60)
    print("📝 Checkpoint Context Collection")
    print("="*60 + "\n")

    # Executive summary
    print("Executive Summary (2-3 sentences about what was completed):")
    print("Example: Implementation paused after completing the foundation and MVP core...")
    exec_summary = input("> ").strip()

    # Key achievements
    print("\nKey achievements (3-5 bullet points, one per line):")
    print("Enter each achievement on a new line. Press Enter twice when done.")
    achievements = []
    while True:
        line = input("> ").strip()
        if not line and achievements:
            break
        if line:
            # Add bullet point if not present
            if not line.startswith("-"):
                line = f"- {line}"
            achievements.append(line)

    # Files created summary
    print("\nFiles created/modified summary (brief overview):")
    print("Example: 65+ files including backend services, routes, configuration...")
    files_summary = input("> ").strip()

    # Knowledge base entries
    print("\nNumber of knowledge base entries captured (enter number or '0'):")
    kb_count_str = input("> ").strip()
    kb_count = int(kb_count_str) if kb_count_str.isdigit() else 0

    kb_entries = []
    for i in range(kb_count):
        print(f"\n--- Knowledge Base Entry {i+1}/{kb_count} ---")

        print("Title:")
        title = input("> ").strip()

        if title.lower() == 'skip':
            continue

        print("Problem (1-2 sentences):")
        problem = input("> ").strip()

        print("Solution (2-3 sentences):")
        solution = input("> ").strip()

        print("Time saved (e.g., '30 minutes', '2 hours'):")
        time_saved = input("> ").strip()

        kb_entries.append({
            "title": title,
            "problem": problem,
            "solution": solution,
            "time_saved": time_saved
        })

    return {
        "executive_summary": exec_summary,
        "achievements": achievements,
        "files_summary": files_summary,
        "kb_entries": kb_entries
    }


def format_phases_table(phases: List[Dict[str, Any]]) -> str:
    """Format phases as markdown table."""

    if not phases:
        return "No phases found."

    lines = []
    lines.append("| Phase | Tasks | Status | Notes |")
    lines.append("|-------|-------|--------|-------|")

    for phase in phases:
        status_emoji = {
            "complete": "✅",
            "partial": "⏸️",
            "pending": "⏳",
            "empty": "➖"
        }.get(phase["status"], "❓")

        percentage = phase["percentage"]
        status_display = f"{status_emoji} {percentage:.0f}%"

        # Generate notes based on status
        if phase["status"] == "complete":
            notes = "Complete"
        elif phase["status"] == "partial":
            notes = f"{phase['completed']}/{phase['total']} tasks"
        else:
            notes = "Not started"

        lines.append(
            f"| **{phase['name']}** | {phase['completed']}/{phase['total']} | "
            f"{status_display} | {notes} |"
        )

    return "\n".join(lines)


def format_kb_entries(entries: List[Dict[str, str]]) -> str:
    """Format knowledge base entries."""

    if not entries:
        return "_No knowledge base entries documented for this checkpoint._"

    lines = []
    lines.append(f"**{len(entries)} critical learnings documented:**\n")

    for i, entry in enumerate(entries, 1):
        lines.append(f"### {i}. {entry['title']}")
        lines.append(f"**Problem**: {entry['problem']}")
        lines.append(f"**Solution**: {entry['solution']}")
        lines.append(f"**Saves**: {entry['time_saved']}\n")

    return "\n".join(lines)


def generate_checkpoint(
    analysis: Dict[str, Any],
    user_input: Dict[str, Any],
    checkpoint_num: str,
    description: str,
    output_dir: str,
    template_file: str
) -> str:
    """Generate checkpoint report from template."""

    # Load template
    with open(template_file, 'r', encoding='utf-8') as f:
        template = f.read()

    # Build phases table
    phases_table = format_phases_table(analysis['phases'])

    # Build KB entries section
    kb_section = format_kb_entries(user_input['kb_entries'])

    # Generate resume command
    feature_id = analysis['feature_id']
    resume_command = f"/aod.build --resume"

    # Current date
    date = datetime.now().strftime("%Y-%m-%d")

    # Build substitution map
    substitutions = {
        "{CHECKPOINT_NUM}": checkpoint_num,
        "{PHASE_DESCRIPTION}": description,
        "{TASK_RANGE}": analysis['task_range'],
        "{DATE}": date,
        "{FEATURE_ID}": feature_id,
        "{TOTAL_TASKS}": str(analysis['total_tasks']),
        "{COMPLETED_TASKS}": str(analysis['completed_tasks']),
        "{PROGRESS_PERCENTAGE}": f"{analysis['progress_percentage']:.0f}",
        "{PHASES_TABLE}": phases_table,
        "{EXECUTIVE_SUMMARY}": user_input['executive_summary'],
        "{KEY_ACHIEVEMENTS}": "\n".join(user_input['achievements']),
        "{FILES_CREATED}": user_input['files_summary'],
        "{KB_ENTRIES}": kb_section,
        "{NEXT_TASK}": analysis.get('next_task', 'None'),
        "{RESUME_COMMAND}": resume_command,
        # Placeholders for sections user should fill
        "{WHAT_WAS_IMPLEMENTED}": "_TODO: Detail what was implemented by phase/user story_",
        "{SERVER_STATUS}": "_TODO: Describe server and database status_",
        "{QUALITY_METRICS}": "_TODO: List code quality, architecture, and performance metrics_",
        "{REMAINING_WORK}": f"**Remaining**: {analysis['pending_tasks']} tasks\n\n_TODO: Detail next waves and estimated duration_",
        "{PAUSE_RATIONALE}": "_TODO: Explain why pausing at this checkpoint_",
        "{TESTING_INSTRUCTIONS}": "_TODO: Provide testing commands and scenarios_",
        "{WHAT_HAPPENS_NEXT}": "_TODO: Describe what happens when resuming_",
        "{ESTIMATED_COMPLETION}": "_TODO: Provide time estimates for remaining work_",
        "{DEPENDENCIES}": "_TODO: List runtime dependencies and versions_",
        "{RISK_ASSESSMENT}": "_TODO: Document completed and remaining risks_",
        "{RECOMMENDATIONS}": "_TODO: Provide recommendations for next session_",
        "{SUCCESS_CRITERIA}": "_TODO: Status of success criteria from spec_",
        "{WHAT_ACCOMPLISHED}": f"{analysis['progress_percentage']:.0f}% of implementation complete",
        "{WHY_GOOD_STOPPING_POINT}": "_TODO: List reasons this is a good checkpoint_",
        "{WHATS_NEXT}": f"Resume with {resume_command}",
        "{IMPLEMENTATION_LEAD}": "Team Lead Agent",
        "{NEXT_REVIEW}": "_TODO: Specify next review milestone_"
    }

    # Perform substitutions
    content = template
    for key, value in substitutions.items():
        content = content.replace(key, value)

    # Generate filename
    filename = f"CHECKPOINT-{checkpoint_num}_{description}_{analysis['task_range']}.md"
    output_path = Path(output_dir) / filename

    # Write file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return filename


def main():
    parser = argparse.ArgumentParser(description="Generate checkpoint report")
    parser.add_argument("--tasks-file", required=True, help="Path to tasks.md")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--description", required=True, help="Checkpoint description (e.g., 'Phase1-2-Complete')")
    parser.add_argument("--checkpoint-num", help="Override checkpoint number (auto-detected if not provided)")

    args = parser.parse_args()

    # Validate inputs
    if not Path(args.tasks_file).exists():
        print(f"Error: Tasks file not found: {args.tasks_file}", file=sys.stderr)
        sys.exit(1)

    if not Path(args.output_dir).exists():
        print(f"Error: Output directory not found: {args.output_dir}", file=sys.stderr)
        sys.exit(1)

    # Load template
    script_dir = Path(__file__).parent.parent
    template_file = script_dir / "references" / "checkpoint_template.md"

    if not template_file.exists():
        print(f"Error: Template not found: {template_file}", file=sys.stderr)
        sys.exit(1)

    print("Analyzing tasks.md...\n")

    # Run analysis
    analysis = load_analysis(args.tasks_file)

    # Detect checkpoint number
    checkpoint_num = args.checkpoint_num or detect_checkpoint_number(args.output_dir)

    print(f"✓ Found {analysis['total_tasks']} total tasks")
    print(f"✓ Found {analysis['completed_tasks']} completed tasks ({analysis['progress_percentage']:.0f}%)")
    print(f"✓ Task range: {analysis['task_range']}")
    print(f"✓ Checkpoint #{checkpoint_num} (auto-detected)\n")

    # Prompt for user input
    user_input = prompt_user_input()

    print("\nGenerating checkpoint report...")

    # Generate checkpoint
    filename = generate_checkpoint(
        analysis=analysis,
        user_input=user_input,
        checkpoint_num=checkpoint_num,
        description=args.description,
        output_dir=args.output_dir,
        template_file=str(template_file)
    )

    print(f"\n✓ Generated: {filename}")
    print(f"✓ Location: {args.output_dir}/{filename}")

    # Update index (call update_index.py)
    print("\nUpdating CHECKPOINTS_README.md...")

    update_script = Path(__file__).parent / "update_index.py"
    checkpoints_readme = Path(args.output_dir) / "CHECKPOINTS_README.md"

    if checkpoints_readme.exists():
        subprocess.run([
            "python3",
            str(update_script),
            "--checkpoints-readme", str(checkpoints_readme),
            "--checkpoint-file", filename,
            "--checkpoint-num", checkpoint_num,
            "--progress", f"{analysis['progress_percentage']:.0f}"
        ])
        print("✓ Updated: CHECKPOINTS_README.md")
    else:
        print("⚠️  CHECKPOINTS_README.md not found - skipping index update")

    print(f"\nNext: Resume with /aod.build --resume")


if __name__ == "__main__":
    main()
