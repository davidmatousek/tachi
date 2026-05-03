#!/usr/bin/env python3
"""
Update CHECKPOINTS_README.md with new checkpoint entry.

Usage:
    python update_index.py \
        --checkpoints-readme specs/001-my-feature/CHECKPOINTS_README.md \
        --checkpoint-file CHECKPOINT-02_US1-Complete_T001-T039.md \
        --checkpoint-num 02 \
        --progress 33
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List


def parse_checkpoint_filename(filename: str) -> dict:
    """Parse checkpoint filename to extract components."""

    # Expected format: CHECKPOINT-{NN}_{Description}_{TaskRange}.md
    match = re.match(
        r'CHECKPOINT-(\d+)_([^_]+)_(T\d+-T\d+)\.md',
        filename
    )

    if not match:
        raise ValueError(f"Invalid checkpoint filename format: {filename}")

    return {
        "number": match.group(1),
        "description": match.group(2),
        "task_range": match.group(3)
    }


def extract_checkpoint_info(checkpoint_path: Path) -> dict:
    """Extract key information from checkpoint file."""

    with open(checkpoint_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract key achievements (look for bullet points in Key Technical Achievements section)
    achievements = []
    in_achievements = False
    for line in content.split('\n'):
        if '## Key Technical Achievements' in line:
            in_achievements = True
            continue
        if in_achievements and line.startswith('##'):
            break
        if in_achievements and line.strip().startswith('-'):
            achievements.append(line.strip())
        if len(achievements) >= 4:
            break

    return {
        "achievements": achievements[:4]  # Limit to 4 key achievements
    }


def update_active_checkpoints_section(
    content: str,
    checkpoint_num: str,
    checkpoint_file: str,
    task_range: str,
    description: str,
    progress: str,
    achievements: List[str]
) -> str:
    """Add new checkpoint to Active Checkpoints section."""

    date = datetime.now().strftime("%Y-%m-%d")

    # Build checkpoint entry
    entry_lines = [
        f"\n### ✅ Checkpoint {checkpoint_num} - {description}",
        f"**File**: [{checkpoint_file}](./{checkpoint_file})",
        f"**Date**: {date}",
        f"**Status**: ⏸️ PAUSED",
        f"**Progress**: {progress}%",
        f"**Range**: {task_range}",
        "",
        "**Key Achievements**:"
    ]

    if achievements:
        entry_lines.extend(achievements)
    else:
        entry_lines.append("- See checkpoint file for details")

    entry_lines.append("")
    entry_lines.append(f"**Next**: Resume implementation from next task")
    entry_lines.append("")

    entry = "\n".join(entry_lines)

    # Find insertion point (before "Future Checkpoints" section)
    future_checkpoints_match = re.search(r'\n## Future Checkpoints', content)

    if not future_checkpoints_match:
        raise ValueError("Could not find '## Future Checkpoints' section")

    insert_pos = future_checkpoints_match.start()

    # Insert new entry
    updated = content[:insert_pos] + entry + "\n---\n" + content[insert_pos:]

    return updated


def update_progress_table(content: str, checkpoint_num: str, progress: str) -> str:
    """Update progress tracking table with new checkpoint status."""

    # Find the progress table
    table_match = re.search(
        r'(\| Checkpoint \| Tasks \| Progress \| Duration \| Status \|.*?\n'
        r'\|------------|-------|----------|----------|--------\|.*?\n'
        r'(?:\| .+? \| .+? \| .+? \| .+? \| .+? \|\n)+)',
        content,
        re.DOTALL
    )

    if not table_match:
        return content  # Table not found, skip update

    table_section = table_match.group(0)

    # Update the row for this checkpoint number
    checkpoint_pattern = rf'(\| \*\*{checkpoint_num}\*\* \| .+? \| )(\d+%)(.*?\| )(⏳ Pending)( \|)'

    def replace_status(match):
        return f"{match.group(1)}{progress}%{match.group(3)}✅ COMPLETE{match.group(5)}"

    updated_table = re.sub(checkpoint_pattern, replace_status, table_section)

    # Replace in content
    updated = content.replace(table_section, updated_table)

    return updated


def update_next_checkpoint_footer(content: str, checkpoint_num: str) -> str:
    """Update the 'Next Checkpoint Planned' footer."""

    next_num = int(checkpoint_num) + 1

    # Find last line with "Next Checkpoint Planned"
    footer_pattern = r'\*\*Next Checkpoint Planned\*\*: Checkpoint \d+ \(.+?\)'

    replacement = f"**Next Checkpoint Planned**: Checkpoint {next_num:02d}"

    updated = re.sub(footer_pattern, replacement, content)

    return updated


def update_last_updated(content: str) -> str:
    """Update the 'Last Updated' timestamp."""

    date = datetime.now().strftime("%Y-%m-%d")

    updated = re.sub(
        r'\*\*Last Updated\*\*: \d{4}-\d{2}-\d{2}',
        f"**Last Updated**: {date}",
        content
    )

    return updated


def main():
    parser = argparse.ArgumentParser(description="Update CHECKPOINTS_README.md")
    parser.add_argument("--checkpoints-readme", required=True, help="Path to CHECKPOINTS_README.md")
    parser.add_argument("--checkpoint-file", required=True, help="Checkpoint filename (e.g., CHECKPOINT-02_...)")
    parser.add_argument("--checkpoint-num", required=True, help="Checkpoint number (e.g., 02)")
    parser.add_argument("--progress", required=True, help="Overall progress percentage (e.g., 33)")

    args = parser.parse_args()

    readme_path = Path(args.checkpoints_readme)

    if not readme_path.exists():
        print(f"Error: CHECKPOINTS_README.md not found: {args.checkpoints_readme}", file=sys.stderr)
        sys.exit(1)

    # Parse checkpoint filename
    try:
        info = parse_checkpoint_filename(args.checkpoint_file)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract checkpoint details if file exists
    checkpoint_path = readme_path.parent / args.checkpoint_file
    achievements = []

    if checkpoint_path.exists():
        try:
            checkpoint_info = extract_checkpoint_info(checkpoint_path)
            achievements = checkpoint_info["achievements"]
        except Exception as e:
            print(f"Warning: Could not extract achievements: {e}", file=sys.stderr)

    # Read README
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update sections
    try:
        content = update_active_checkpoints_section(
            content=content,
            checkpoint_num=args.checkpoint_num,
            checkpoint_file=args.checkpoint_file,
            task_range=info["task_range"],
            description=info["description"],
            progress=args.progress,
            achievements=achievements
        )

        content = update_progress_table(
            content=content,
            checkpoint_num=args.checkpoint_num,
            progress=args.progress
        )

        content = update_next_checkpoint_footer(
            content=content,
            checkpoint_num=args.checkpoint_num
        )

        content = update_last_updated(content)

    except Exception as e:
        print(f"Error updating README: {e}", file=sys.stderr)
        sys.exit(1)

    # Write updated README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✓ Updated {readme_path.name}")


if __name__ == "__main__":
    main()
