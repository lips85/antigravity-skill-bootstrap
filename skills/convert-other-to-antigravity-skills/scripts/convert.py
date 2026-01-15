#!/usr/bin/env python3
"""
Convert Skill to Antigravity Standard

This script modifies a given skill's SKILL.md to:
1. Use correct paths (.agent/skills/skills/...)
2. Use uv for execution (uv run ...)
3. Add Prerequisites section
"""

import sys
import re
from pathlib import Path

# Template for the Prerequisites section
PREREQUISITES_TEMPLATE = """## Prerequisites

This skill uses `uv` for dependency management.

1. Initialize `uv` project (if not already done):
```bash
uv init .
```

2. Add dependencies (No external packages required for this skill):
```bash
# uv add [package]
```

3. Run the skill using `uv run`:
```bash
uv run [script_path] ...
```

"""

def convert_skill(skill_path_str):
    skill_path = Path(skill_path_str).resolve()
    
    if not skill_path.exists():
        print(f"Error: Skill path not found: {skill_path}")
        return False
        
    skill_name = skill_path.name
    skill_md_path = skill_path / "SKILL.md"
    
    if not skill_md_path.exists():
        print(f"Error: SKILL.md not found in {skill_path}")
        return False
        
    content = skill_md_path.read_text(encoding='utf-8')
    original_content = content
    
    # 1. Add Prerequisites if missing
    if "## Prerequisites" not in content:
        # Insert after the first header (usually # Skill Name) and its description
        # We look for the first line starting with #, then find the next header or end of description
        # A simple heuristic: find the first "## " and insert before it, or after the first paragraph following #
        
        # Split frontmatter
        parts = content.split("---", 2)
        if len(parts) >= 3:
            # part[0] is empty, part[1] is frontmatter, part[2] is body
            body = parts[2]
            
            # Find insertion point: Before the first "## "
            match = re.search(r'\n## ', body)
            if match:
                insertion_index = match.start()
                new_body = body[:insertion_index] + "\n" + PREREQUISITES_TEMPLATE + body[insertion_index:]
                content = parts[0] + "---" + parts[1] + "---" + new_body
            else:
                # No subheaders? Just append after title? 
                # Let's just append to end if structure is weird, but usually there are headers.
                pass
        
    # 2. Fix Paths and Commands
    
    # Pattern 1: .claude/skills -> .agent/skills
    content = content.replace(".claude/skills", ".agent/skills")
    
    # Pattern 2: Explicit python/python3 commands
    # Case A: python3 .agent/skills/... -> uv run .agent/skills/...
    content = re.sub(r'python3? (\.agent/skills/)', r'uv run \1', content)
    
    # Case B: python3 scripts/script.py -> uv run .agent/skills/<name>/scripts/script.py
    # We match "python3 scripts/" or "python scripts/"
    def replace_relative_script(match):
        script_part = match.group(1) # just the script name part after scripts/
        return f"uv run .agent/skills/{skill_name}/scripts/{script_part}"
        
    content = re.sub(r'python3? scripts/([^\s]+)', replace_relative_script, content)
    
    # Case C: Just "scripts/script.py" usage in bash blocks (sometimes users just write the path)
    # This is risky if it's text, but in code blocks it usually means execute.
    # However, "python scripts/..." is covered above.
    # If the user wrote just "scripts/init_skill.py ...", we want "uv run .agent.../scripts/init_skill.py ..."
    # We look for lines starting with "scripts/" inside code blocks ideally, or just generally but safely.
    # Let's look for "scripts/..." that is NOT preceded by "/" (to avoid matching absolute paths or URL parts)
    
    def replace_bare_script(match):
        script_path = match.group(1)
        return f"uv run .agent/skills/{skill_name}/{script_path}"
        
    # Match "scripts/something.py" at start of line or after whitespace, ensuring it ends with .py
    content = re.sub(r'(?<=[\s\n])scripts/([^\s]+\.py)', replace_bare_script, content)

    # 3. Cleanup "uv run uv run" if any accident happened
    content = content.replace("uv run uv run", "uv run")

    if content != original_content:
        skill_md_path.write_text(content, encoding='utf-8')
        print(f"✅ Updated {skill_md_path}")
        return True
    else:
        print(f"ℹ️ No changes needed for {skill_name}")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: convert.py <skill_name_or_path>")
        sys.exit(1)
        
    target = sys.argv[1]
    
    # Check if it's a path or just name
    if Path(target).exists():
        path = Path(target)
    else:
        # Assume it's in .agent/skills/
        # We need to find the project root relative to this script
        # This script is in .agent/skills/convert-.../scripts/
        # Root is ../../../../
        script_dir = Path(__file__).parent
        root = script_dir.parent.parent.parent.parent
        # Try to construct path
        candidate = root / ".agent" / "skills" / target
        if candidate.exists():
            path = candidate
        else:
            # Maybe the user ran it from root and meant a relative path?
            candidate2 = Path.cwd() / target
            if candidate2.exists():
                path = candidate2
            else:
                print(f"Error: Could not find skill {target}")
                sys.exit(1)
                
    success = convert_skill(path)
    if not success:
        sys.exit(1)
