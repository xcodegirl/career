"""
Generate Markdown resume from JSON source.
Usage: python json2md.py input.json [output.md]
"""
import json
import os
import sys


def escape_markdown(text):
    """Escape pipe chars and normalize curly quotes and dashes to straight ASCII."""
    if not isinstance(text, str):
        return text
    text = text.replace(''', "'").replace(''', "'")
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace('–', '-').replace('—', '--')
    text = text.replace('|', '\\|')
    return text


def get_output_path(json_path, output_arg):
    """Determine output file path: use provided arg or derive from input."""
    if output_arg:
        return output_arg
    return os.path.splitext(json_path)[0] + '.md'


def load_resume_json(json_path):
    """Read and parse resume JSON file."""
    with open(json_path, encoding='utf-8') as file_handle:
        return json.load(file_handle)


def write_resume(output_path, lines):
    """Write resume lines to markdown file."""
    with open(output_path, 'w', encoding='utf-8') as file_handle:
        file_handle.write('\n'.join(lines))


def main():
    if len(sys.argv) < 2:
        print("Usage: python json2md.py input.json [output.md]")
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = get_output_path(json_path, sys.argv[2] if len(sys.argv) > 2 else None)

    resume_data = load_resume_json(json_path)
    lines = []

    # =====================================================================
    # HEADER: NAME AND TITLE
    # =====================================================================
    lines.append(f"# {escape_markdown(resume_data['name'])}")
    lines.append(f"**{escape_markdown(resume_data['title'])}**")
    lines.append("")

    # =====================================================================
    # CONTACT INFO
    # =====================================================================
    contact = resume_data.get('contact', {})
    contact_lines = []
    if "location" in contact:
        contact_lines.append(f"- 📍 {escape_markdown(contact['location'])}")
    if "phone" in contact:
        contact_lines.append(f"- 📞 {escape_markdown(contact['phone'])}")
    if "email" in contact:
        contact_lines.append(f"- ✉️ [{escape_markdown(contact['email'])}](mailto:{contact['email']})")
    if "linkedin" in contact:
        contact_lines.append(f"- [LinkedIn]({contact['linkedin']})")
    if "github" in contact:
        contact_lines.append(f"- [GitHub]({contact['github']})")
    if "discord" in contact:
        contact_lines.append(f"- Discord: `{escape_markdown(contact['discord'])}`")

    if contact_lines:
        lines.append("**Contact:**")
        lines.extend(contact_lines)
        lines.append("")

    # =====================================================================
    # SUMMARY SECTION
    # =====================================================================
    if resume_data.get("summary"):
        lines.append("## Summary")
        lines.append(escape_markdown(resume_data["summary"]))
        lines.append("")

    # =====================================================================
    # EXPERIENCE SECTION
    # =====================================================================
    if resume_data.get("experience"):
        lines.append("## Experience")
        for job in resume_data["experience"]:
            lines.append(f"**{escape_markdown(job['title'])}**, {escape_markdown(job['company'])}")
            lines.append(f"{escape_markdown(job['date'])}")
            lines.append(f"- {escape_markdown(job['description'])}")

            if job.get("technologies"):
                tech_list = ', '.join(escape_markdown(t) for t in job["technologies"])
                lines.append(f"  - _Technologies:_ {tech_list}")
            lines.append("")

    # =====================================================================
    # EDUCATION SECTION
    # =====================================================================
    if resume_data.get("education"):
        lines.append("## Education")
        for school in resume_data["education"]:
            degree = escape_markdown(school.get('degree', ''))
            institution = escape_markdown(school.get('institution', ''))
            date = escape_markdown(school.get('date', ''))
            field = school.get('field')
            thesis = school.get("thesis")

            lines.append(f"**{degree}**, {institution}")
            lines.append(f"{date}")
            if field:
                lines.append(f"- Field: {escape_markdown(field)}")
            if thesis:
                lines.append(f"- Thesis: _{escape_markdown(thesis)}_")
            lines.append("")

    # =====================================================================
    # COMMUNITY OUTREACH SECTION
    # =====================================================================
    if resume_data.get("community_outreach"):
        lines.append("## Community Outreach")
        for entry in resume_data["community_outreach"]:
            org = f", {escape_markdown(entry['organization'])}" if entry.get("organization") else ""
            role = escape_markdown(entry['role'])
            years = escape_markdown(entry['years'])
            lines.append(f"- **{role}**{org} ({years})")
        lines.append("")

    # =====================================================================
    # AWARDS SECTION
    # =====================================================================
    if resume_data.get("awards"):
        lines.append("## Awards")
        for award in resume_data["awards"]:
            title = escape_markdown(award['title'])
            org = f", {escape_markdown(award['organization'])}" if award.get("organization") else ""
            year = f", {escape_markdown(award['year'])}" if award.get("year") else ""
            lines.append(f"- {title}{org}{year}")
        lines.append("")

    # =====================================================================
    # LANGUAGES SECTION
    # =====================================================================
    if resume_data.get("languages"):
        lines.append("## Languages")
        for lang in resume_data["languages"]:
            language = escape_markdown(lang['language'])
            proficiency = escape_markdown(lang['proficiency'])
            lines.append(f"- {language}: {proficiency}")
        lines.append("")

    # =====================================================================
    # PORTFOLIO SECTION
    # =====================================================================
    if resume_data.get("portfolio"):
        lines.append("## Portfolio")
        for item in resume_data["portfolio"]:
            title = escape_markdown(item['title'])
            url = item['url']
            lines.append(f"- [{title}]({url})")
        lines.append("")

    # =====================================================================
    # PUBLISHED GAMES SECTION
    # =====================================================================
    if resume_data.get("published_games"):
        lines.append("## Published Games")
        for game in resume_data["published_games"]:
            title = escape_markdown(game['title'])
            platforms = ', '.join(escape_markdown(p) for p in game["platforms"])
            year = game["year"] if isinstance(game["year"], str) else ', '.join(escape_markdown(y) for y in game["year"])
            lines.append(f"- **{title}** ({platforms}, {escape_markdown(year)})")
        lines.append("")

    # =====================================================================
    # CERTIFICATIONS SECTION
    # =====================================================================
    if resume_data.get("certifications"):
        lines.append("## Certifications")
        for cert in resume_data["certifications"]:
            title = escape_markdown(cert['title'])
            issuer = escape_markdown(cert.get('issuer', ''))
            date = escape_markdown(cert.get('date', ''))
            credential_id = cert.get('credential_id', '')
            issuer_str = f" - {issuer}" if issuer else ""
            date_str = f" ({date})" if date else ""
            credential_str = f" [ID: {escape_markdown(credential_id)}]" if credential_id else ""
            lines.append(f"- **{title}**{issuer_str}{date_str}{credential_str}")
        lines.append("")

    # =====================================================================
    # PROJECTS SECTION
    # =====================================================================
    if resume_data.get("projects"):
        lines.append("## Projects")
        for project in resume_data["projects"]:
            title = escape_markdown(project['title'])
            description = escape_markdown(project.get('description', ''))
            technologies = project.get('technologies', [])
            date = escape_markdown(project.get('date', ''))
            url = project.get('url', '')
            date_str = f" ({date})" if date else ""
            lines.append(f"### {title}{date_str}")
            lines.append(f"{description}")
            if technologies:
                tech_str = ', '.join(escape_markdown(t) for t in technologies)
                lines.append(f"**Technologies:** {tech_str}")
            if url:
                lines.append(f"[View Project]({url})")
            lines.append("")

    # =====================================================================
    # VOLUNTEER EXPERIENCE SECTION
    # =====================================================================
    if resume_data.get("volunteer"):
        lines.append("## Volunteer Experience")
        for vol in resume_data["volunteer"]:
            title = escape_markdown(vol['title'])
            organization = escape_markdown(vol['organization'])
            date = escape_markdown(vol.get('date', ''))
            description = escape_markdown(vol.get('description', ''))
            lines.append(f"**{title}**, {organization}")
            lines.append(f"{date}")
            lines.append(f"- {description}")
            lines.append("")

    # =====================================================================
    # PUBLICATIONS SECTION
    # =====================================================================
    if resume_data.get("publications"):
        lines.append("## Publications")
        for pub in resume_data["publications"]:
            title = escape_markdown(pub['title'])
            publication = escape_markdown(pub.get('publication', ''))
            date = escape_markdown(pub.get('date', ''))
            url = pub.get('url', '')
            date_str = f" ({date})" if date else ""
            pub_str = f" - {publication}" if publication else ""
            title_link = f"[{title}]({url})" if url else title
            lines.append(f"- {title_link}{pub_str}{date_str}")
        lines.append("")

    # =====================================================================
    # MEMBERSHIPS SECTION
    # =====================================================================
    if resume_data.get("memberships"):
        lines.append("## Professional Memberships")
        for membership in resume_data["memberships"]:
            organization = escape_markdown(membership['organization'])
            title = escape_markdown(membership.get('title', ''))
            date = escape_markdown(membership.get('date', ''))
            title_str = f" ({title})" if title else ""
            date_str = f" - {date}" if date else ""
            lines.append(f"- **{organization}**{title_str}{date_str}")
        lines.append("")

    # =====================================================================
    # SKILLS SECTION
    # =====================================================================
    if resume_data.get("skills"):
        lines.append("## Skills")
        skills = resume_data["skills"]
        if isinstance(skills, dict):
            for category, items in skills.items():
                lines.append(f"**{escape_markdown(category)}:**")
                if isinstance(items, list):
                    items_str = ', '.join(escape_markdown(item) for item in items)
                else:
                    items_str = escape_markdown(items)
                lines.append(f"{items_str}")
            lines.append("")

    write_resume(output_path, lines)
    print(f"Wrote Markdown resume to: {output_path}")


if __name__ == "__main__":
    main()
