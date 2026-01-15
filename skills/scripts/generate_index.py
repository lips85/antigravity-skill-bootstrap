import os
import json
import re

def generate_index(skills_dir, output_file):
    print(f"🏗️ Generating index from: {skills_dir}")
    skills = []

    for root, dirs, files in os.walk(skills_dir):
        if "SKILL.md" in files:
            skill_path = os.path.join(root, "SKILL.md")
            dir_name = os.path.basename(root)
            
            skill_info = {
                "id": dir_name,
                "path": os.path.relpath(root, os.path.dirname(skills_dir)),
                "name": dir_name.replace("-", " ").title(),
                "description": ""
            }
            
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Try to extract from frontmatter first
                fm_match = re.search(r'^---\s*(.*?)\s*---', content, re.DOTALL)
                if fm_match:
                    fm_content = fm_match.group(1)
                    name_fm = re.search(r'^name:\s*(.+)$', fm_content, re.MULTILINE)
                    desc_fm = re.search(r'^description:\s*(.+)$', fm_content, re.MULTILINE)
                    
                    if name_fm:
                        skill_info["name"] = name_fm.group(1).strip()
                    if desc_fm:
                        skill_info["description"] = desc_fm.group(1).strip()
                
                # Fallback to Header and First Paragraph if needed
                if not skill_info["description"] or skill_info["description"] == "":
                    name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                    if name_match and not fm_match: # Only override if no frontmatter name
                         skill_info["name"] = name_match.group(1).strip()
                    
                    # Extract first paragraph
                    body = content
                    if fm_match:
                        body = content[fm_match.end():].strip()
                    
                    lines = body.split('\n')
                    desc_lines = []
                    for line in lines:
                        if line.startswith('#') or not line.strip():
                            if desc_lines: break
                            continue
                        desc_lines.append(line.strip())
                    
                    if desc_lines:
                        skill_info["description"] = " ".join(desc_lines)[:150] + "..."
            
            skills.append(skill_info)

    skills.sort(key=lambda x: x["name"])

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(skills, f, indent=2)
    
    print(f"✅ Generated index with {len(skills)} skills at: {output_file}")
    return skills

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_path = os.path.join(base_dir, "skills")
    output_path = os.path.join(base_dir, "skills_index.json")
    generate_index(skills_path, output_path)
