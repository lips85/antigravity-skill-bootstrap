import os
import re

def validate_skills(skills_dir):
    print(f"🔍 Validating skills in: {skills_dir}")
    errors = []
    skill_count = 0

    for root, dirs, files in os.walk(skills_dir):
        if "SKILL.md" in files:
            skill_count += 1
            skill_path = os.path.join(root, "SKILL.md")
            rel_path = os.path.relpath(skill_path, skills_dir)
            
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Frontmatter or Header
            has_frontmatter = content.strip().startswith("---")
            has_header = re.search(r'^#\s+', content, re.MULTILINE)
            
            if not (has_frontmatter or has_header):
                errors.append(f"❌ {rel_path}: Missing frontmatter or top-level heading")
            
            if has_frontmatter:
                # Basic check for name and description in frontmatter
                fm_match = re.search(r'^---\s*(.*?)\s*---', content, re.DOTALL)
                if fm_match:
                    fm_content = fm_match.group(1)
                    if "name:" not in fm_content:
                        errors.append(f"⚠️  {rel_path}: Frontmatter missing 'name:'")
                    if "description:" not in fm_content:
                        errors.append(f"⚠️  {rel_path}: Frontmatter missing 'description:'")
                else:
                    errors.append(f"❌ {rel_path}: Malformed frontmatter")

    print(f"✅ Found and checked {skill_count} skills.")
    if errors:
        print("\n⚠️  Validation Results:")
        for err in errors:
            print(err)
        return False
    else:
        print("✨ All skills passed basic validation!")
        return True

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_path = os.path.join(base_dir, "skills")
    validate_skills(skills_path)
