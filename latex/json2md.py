import json
import sys

def md_escape(text):
    """Escape special Markdown characters and normalize quotes/dashes."""
    if not isinstance(text, str):
        return text
    text = text.replace('’', "'").replace('‘', "'")
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('–', '-').replace('—', '--')
    text = text.replace('|', '\\|')
    return text

def main():
    # Usage: python json2md.py input.json [output.md]
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        print("Usage: python json2md.py input.json [output.md]")
        sys.exit(1)
    if len(sys.argv) > 2:
        md_file = sys.argv[2]
    else:
        md_file = json_file.replace('.json', '-resume.md')

    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)

    lines = []
    # Header
    lines.append(f"# {md_escape(data['name'])}")
    lines.append(f"**{md_escape(data['title'])}**")
    lines.append("")

    # Contact
    contact = data.get('contact', {})
    contact_lines = []
    if "location" in contact:
        contact_lines.append(f"- 📍 {md_escape(contact['location'])}")
    if "phone" in contact:
        contact_lines.append(f"- 📞 {md_escape(contact['phone'])}")
    if "email" in contact:
        contact_lines.append(f"- ✉️ [{md_escape(contact['email'])}](mailto:{contact['email']})")
    if "linkedin" in contact:
        contact_lines.append(f"- [LinkedIn]({contact['linkedin']})")
    if "github" in contact:
        contact_lines.append(f"- [GitHub]({contact['github']})")
    if "discord" in contact:
        contact_lines.append(f"- Discord: `{md_escape(contact['discord'])}`")
    if contact_lines:
        lines.append("**Contact:**")
        lines.extend(contact_lines)
        lines.append("")

    # Summary
    if data.get("summary"):
        lines.append("## Summary")
        lines.append(md_escape(data["summary"]))
        lines.append("")

    # Experience
    if data.get("experience"):
        lines.append("## Experience")
        for exp in data["experience"]:
            lines.append(f"**{md_escape(exp['title'])}**, {md_escape(exp['company'])}  \n{md_escape(exp['date'])}")
            lines.append(f"- {md_escape(exp['description'])}")
            techs = exp.get("technologies", [])
            if techs:
                lines.append(f"  - _Technologies:_ {', '.join(md_escape(t) for t in techs)}")
            lines.append("")
    
    # Education
    if data.get("education"):
        lines.append("## Education")
        for edu in data["education"]:
            degree = edu.get('degree')
            institution = edu.get('institution')
            date = edu.get('date')
            field = edu.get('field')
            lines.append(f"**{md_escape(degree)}**, {md_escape(institution)}  \n{md_escape(date)}")
            if field:
                lines.append(f"- Field: {md_escape(field)}")
            if edu.get("thesis"):
                lines.append(f"- Thesis: _{md_escape(edu['thesis'])}_")
            lines.append("")

    # Community Outreach
    if data.get("community_outreach"):
        lines.append("## Community Outreach")
        for c in data["community_outreach"]:
            org = f", {md_escape(c['organization'])}" if c.get("organization") else ""
            lines.append(f"- **{md_escape(c['role'])}**{org} ({md_escape(c['years'])})")
        lines.append("")

    # Awards
    if data.get("awards"):
        lines.append("## Awards")
        for a in data["awards"]:
            org = f", {md_escape(a['organization'])}" if a.get("organization") else ""
            year = f", {md_escape(a['year'])}" if a.get("year") else ""
            lines.append(f"- {md_escape(a['title'])}{org}{year}")
        lines.append("")

    # Languages
    if data.get("languages"):
        lines.append("## Languages")
        for l in data["languages"]:
            lines.append(f"- {md_escape(l['language'])}: {md_escape(l['proficiency'])}")
        lines.append("")

    # Work Samples
    if data.get("work_samples"):
        lines.append("## Work Samples")
        for ws in data["work_samples"]:
            lines.append(f"- [{md_escape(ws['title'])}]({ws['url']})")
        lines.append("")

    # Published Games
    if data.get("published_games"):
        lines.append("## Published Games")
        for g in data["published_games"]:
            platforms = ', '.join(md_escape(p) for p in g["platforms"])
            year = g["year"] if isinstance(g["year"], str) else ', '.join(md_escape(y) for y in g["year"])
            lines.append(f"- **{md_escape(g['title'])}** ({platforms}, {md_escape(year)})")
        lines.append("")

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

if __name__ == "__main__":
    main()