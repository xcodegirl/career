"""
Generate Markdown resume from JSON source.
Usage: python json2md.py input.json [output.md]
"""
import sys

from resume_builder_common import get_output_path, load_resume_json, build_sections


def escape_markdown(text):
    """Escape pipe chars and normalize curly quotes and dashes to straight ASCII."""
    if not isinstance(text, str):
        return text
    text = text.replace(''', "'").replace(''', "'")
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace('–', '-').replace('—', '--')
    text = text.replace('|', '\\|')
    return text


def write_resume(output_path, lines):
    """Write resume lines to markdown file."""
    with open(output_path, 'w', encoding='utf-8') as file_handle:
        file_handle.write('\n'.join(lines))


# =====================================================================
# SECTION BUILDERS
# =====================================================================

def add_summary_section(lines, resume_data):
    """Add professional summary."""
    if not resume_data.get("summary"):
        return
    lines.append("## Summary")
    lines.append(escape_markdown(resume_data["summary"]))
    lines.append("")


def add_ai_expertise_section(lines, resume_data):
    """Add AI expertise section if present."""
    if not resume_data.get("ai_expertise"):
        return

    lines.append("## AI Expertise")

    ai = resume_data["ai_expertise"]

    if ai.get("daily_practice"):
        lines.append("**Daily practice:**")
        for item in ai["daily_practice"]:
            lines.append(f"- {escape_markdown(item)}")
        lines.append("")

    if ai.get("teaching"):
        lines.append("**What I teach about AI:**")
        for item in ai["teaching"]:
            lines.append(f"- {escape_markdown(item)}")
        lines.append("")

    if ai.get("assessment"):
        lines.append("**AI and assessment design (from training):**")
        for item in ai["assessment"]:
            lines.append(f"- {escape_markdown(item)}")
        lines.append("")


def add_experience_section(lines, resume_data):
    """Add experience section."""
    if not resume_data.get("experience"):
        return
    lines.append("## Experience")
    for job in resume_data["experience"]:
        lines.append(f"**{escape_markdown(job['title'])}**, {escape_markdown(job['company'])}")
        lines.append(f"{escape_markdown(job['date'])}")
        if job.get("technologies"):
            tech_list = ' / '.join([f"`{escape_markdown(t)}`" for t in job["technologies"]])
            lines.append(f"  {tech_list}")
        if job.get("description"):
            lines.append(f"- {escape_markdown(job['description'])}")
        if job.get("bullets"):
            for bullet in job["bullets"]:
                lines.append(f"- {escape_markdown(bullet)}")
        lines.append("")


def add_education_section(lines, resume_data):
    """Add education section."""
    if not resume_data.get("education"):
        return
    lines.append("## Education")
    for school in resume_data["education"]:
        lines.append(f"**{escape_markdown(school['degree'])}** in {escape_markdown(school['field'])}")
        lines.append(f"_{escape_markdown(school['institution'])}_ — {escape_markdown(school['date'])}")
        lines.append("")


def add_certifications_section(lines, resume_data):
    """Add certifications section."""
    if not resume_data.get("certifications"):
        return
    lines.append("## Certifications")
    for cert in resume_data["certifications"]:
        title = escape_markdown(cert['title'])
        issuer = escape_markdown(cert.get('issuer', ''))
        date = escape_markdown(cert.get('date', ''))
        issuer_str = f" - {issuer}" if issuer else ""
        date_str = f" ({date})" if date else ""
        lines.append(f"- **{title}**{issuer_str}{date_str}")
    lines.append("")


def add_awards_section(lines, resume_data):
    """Add awards section."""
    if not resume_data.get("awards"):
        return
    lines.append("## Awards")
    for award in resume_data["awards"]:
        title = escape_markdown(award['title'])
        org = f", {escape_markdown(award['organization'])}" if award.get("organization") else ""
        year = f", {escape_markdown(award['year'])}" if award.get("year") else ""
        lines.append(f"- {title}{org}{year}")
    lines.append("")


def add_skills_section(lines, resume_data):
    """Add skills section."""
    if not resume_data.get("skills"):
        return
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


def add_projects_section(lines, resume_data):
    """Add projects section."""
    if not resume_data.get("projects"):
        return
    lines.append("## Projects")
    for project in resume_data["projects"]:
        title = escape_markdown(project['title'])
        description = escape_markdown(project.get('description', ''))
        technologies = project.get('technologies', [])
        date = escape_markdown(project.get('date', ''))
        date_str = f" ({date})" if date else ""
        lines.append(f"### {title}{date_str}")
        lines.append(f"{description}")
        if technologies:
            tech_str = ', '.join(escape_markdown(t) for t in technologies)
            lines.append(f"**Technologies:** {tech_str}")
        if project.get('url'):
            lines.append(f"[View Project]({project.get('url')})")
        lines.append("")


def add_volunteer_section(lines, resume_data):
    """Add volunteer experience section."""
    if not resume_data.get("volunteer"):
        return
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


def add_publications_section(lines, resume_data):
    """Add publications section."""
    if not resume_data.get("publications"):
        return
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


def add_languages_section(lines, resume_data):
    """Add languages section."""
    if not resume_data.get("languages"):
        return
    lines.append("## Languages")
    for lang in resume_data["languages"]:
        language = escape_markdown(lang['language'])
        proficiency = escape_markdown(lang['proficiency'])
        lines.append(f"- {language}: {proficiency}")
    lines.append("")


def add_memberships_section(lines, resume_data):
    """Add professional memberships section."""
    if not resume_data.get("memberships"):
        return
    lines.append("## Professional Memberships")
    for membership in resume_data["memberships"]:
        organization = escape_markdown(membership['organization'])
        title = escape_markdown(membership.get('title', ''))
        date = escape_markdown(membership.get('date', ''))
        title_str = f" ({title})" if title else ""
        date_str = f" - {date}" if date else ""
        lines.append(f"- **{organization}**{title_str}{date_str}")
    lines.append("")


def add_portfolio_section(lines, resume_data):
    """Add portfolio section."""
    if not resume_data.get("portfolio"):
        return
    lines.append("## Portfolio")
    for item in resume_data["portfolio"]:
        title = escape_markdown(item['title'])
        url = item['url']
        lines.append(f"- [{title}]({url})")
    lines.append("")


def add_published_games_section(lines, resume_data):
    """Add published games section."""
    if not resume_data.get("published_games"):
        return
    lines.append("## Published Games")
    for game in resume_data["published_games"]:
        title = escape_markdown(game['title'])
        platforms = ', '.join(escape_markdown(p) for p in game["platforms"])
        year = game["year"] if isinstance(game["year"], str) else ', '.join(escape_markdown(y) for y in game["year"])
        lines.append(f"- **{title}** ({platforms}, {escape_markdown(year)})")
    lines.append("")


# =====================================================================
# SECTION MAPPING AND ORDERING
# =====================================================================

SECTION_BUILDERS = {
    'summary': add_summary_section,
    'ai_expertise': add_ai_expertise_section,
    'experience': add_experience_section,
    'education': add_education_section,
    'certifications': add_certifications_section,
    'awards': add_awards_section,
    'skills': add_skills_section,
    'projects': add_projects_section,
    'volunteer': add_volunteer_section,
    'publications': add_publications_section,
    'languages': add_languages_section,
    'memberships': add_memberships_section,
    'portfolio': add_portfolio_section,
    'published_games': add_published_games_section,
}

def main():
    if len(sys.argv) < 2:
        print("Usage: python json2md.py input.json [output.md]")
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = get_output_path(json_path, sys.argv[2] if len(sys.argv) > 2 else None, '.md')

    resume_data = load_resume_json(json_path)
    lines = []

    # Header: Name and Title
    lines.append(f"# {escape_markdown(resume_data['name'])}")
    lines.append(f"## {escape_markdown(resume_data['title'])}")
    lines.append("")

    # Contact Info
    contact = resume_data.get('contact', {})
    contact_lines = []
    if 'email' in contact:
        contact_lines.append(f"- ✉️ [{escape_markdown(contact['email'])}](mailto:{contact['email']})")
    if 'phone' in contact:
        contact_lines.append(f"- 📞 {escape_markdown(contact['phone'])}")
    if "linkedin" in contact:
        contact_lines.append(f"- [LinkedIn]({contact['linkedin']})")
    if "github" in contact:
        contact_lines.append(f"- [GitHub]({contact['github']})")
    if "website" in contact:
        contact_lines.append(f"- [Website]({contact['website']})")

    if contact_lines:
        lines.append("**Contact:**")
        lines.extend(contact_lines)
        lines.append("")

    # Build sections in order specified by JSON
    build_sections(lines, resume_data, SECTION_BUILDERS)

    write_resume(output_path, lines)
    print(f"Wrote Markdown resume to: {output_path}")


if __name__ == "__main__":
    main()
