"""
Generate HTML resume from JSON source.
Usage: python json2html.py input.json [output.html]
"""
import sys

from resume_builder_common import get_output_path, load_resume_json, build_sections


def escape_html(text):
    """Escape HTML entities and normalize curly quotes and dashes."""
    if not isinstance(text, str):
        return text
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('"', '&quot;').replace("'", '&#39;')
    text = text.replace(''', "'").replace(''', "'")
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace('–', '-').replace('—', '--')
    return text


# =====================================================================
# SECTION BUILDERS
# =====================================================================

def add_summary_section(lines, resume_data):
    """Add professional summary."""
    if not resume_data.get("summary"):
        return
    lines.append('<div class="section">')
    lines.append('<h2>Summary</h2>')
    lines.append(f'<p>{escape_html(resume_data["summary"])}</p>')
    lines.append('</div>')


def add_ai_expertise_section(lines, resume_data):
    """Add AI expertise section if present."""
    if not resume_data.get("ai_expertise"):
        return

    lines.append('<div class="section">')
    lines.append('<h2>AI Expertise</h2>')

    ai = resume_data["ai_expertise"]

    if ai.get("daily_practice"):
        lines.append('<div><strong>Daily practice:</strong>')
        lines.append('<ul>')
        for item in ai["daily_practice"]:
            lines.append(f'<li>{escape_html(item)}</li>')
        lines.append('</ul></div>')

    if ai.get("teaching"):
        lines.append('<div><strong>What I teach about AI:</strong>')
        lines.append('<ul>')
        for item in ai["teaching"]:
            lines.append(f'<li>{escape_html(item)}</li>')
        lines.append('</ul></div>')

    if ai.get("assessment"):
        lines.append('<div><strong>AI and assessment design (from training):</strong>')
        lines.append('<ul>')
        for item in ai["assessment"]:
            lines.append(f'<li>{escape_html(item)}</li>')
        lines.append('</ul></div>')

    lines.append('</div>')


def add_experience_section(lines, resume_data):
    """Add experience section."""
    experience = resume_data.get("experience") or resume_data.get("teaching_experience") or resume_data.get("industry_experience")
    if not experience:
        return
    lines.append('<div class="section">')
    lines.append('<h2>Experience</h2>')
    for job in resume_data["experience"]:
        title = escape_html(job["title"])
        company = escape_html(job["company"])
        lines.append(f'<h3>{title} <span style="font-weight:normal;">- {company}</span></h3>')
        lines.append(f'<div><em>{escape_html(job["date"])}</em></div>')
        if job.get("technologies"):
            techs = " / ".join([f"<code>{escape_html(t)}</code>" for t in job["technologies"]])
            lines.append(f'<p>{techs}</p>')
        if job.get("description"):
            lines.append(f'<p>{escape_html(job["description"])}</p>')
        lines.append('<ul>')
        if job.get("bullets"):
            for bullet in job["bullets"]:
                lines.append(f'<li>{escape_html(bullet)}</li>')
        lines.append('</ul>')
    lines.append('</div>')


def add_education_section(lines, resume_data):
    """Add education section."""
    if not resume_data.get("education"):
        return
    lines.append('<div class="section">')
    lines.append('<h2>Education</h2>')
    for school in resume_data["education"]:
        degree = escape_html(school["degree"])
        institution = escape_html(school["institution"])
        lines.append(f'<h3>{degree} - {institution}</h3>')
        lines.append(f'<div><em>{escape_html(school["date"])}</em></div>')
        lines.append(f'<div>Field: {escape_html(school["field"])}</div>')
        if school.get("thesis"):
            lines.append(f'<div>Thesis: <em>{escape_html(school["thesis"])}</em></div>')
    lines.append('</div>')


def add_certifications_section(lines, resume_data):
    """Add certifications section."""
    if not resume_data.get("certifications"):
        return
    lines.append('<div class="section">')
    lines.append('<h2>Certifications</h2>')
    lines.append('<ul>')
    for cert in resume_data["certifications"]:
        title = escape_html(cert["title"])
        issuer = escape_html(cert.get("issuer", ""))
        date = escape_html(cert.get("date", ""))
        credential_id = cert.get("credential_id", "")
        issuer_str = f' - {issuer}' if issuer else ''
        date_str = f' ({date})' if date else ''
        credential_str = f' - ID: {escape_html(credential_id)}' if credential_id else ''
        lines.append(f'<li><strong>{title}</strong>{issuer_str}{date_str}{credential_str}</li>')
    lines.append('</ul>')
    lines.append('</div>')


def add_awards_section(lines, resume_data):
    """Add awards section."""
    if not resume_data.get("awards"):
        return
    lines.append('<div class="section">')
    lines.append('<h2>Awards</h2>')
    lines.append('<ul>')
    for award in resume_data["awards"]:
        title = escape_html(award['title'])
        org = f", {escape_html(award['organization'])}" if award.get("organization") else ""
        year = f", {escape_html(award['year'])}" if award.get("year") else ""
        lines.append(f'<li>{title}{org}{year}</li>')
    lines.append('</ul>')
    lines.append('</div>')


def add_skills_section(lines, resume_data):
    """Add skills section."""
    if not resume_data.get("skills"):
        return
    lines.append('<div class="section">')
    lines.append('<h2>Skills</h2>')
    skills = resume_data["skills"]
    if isinstance(skills, dict):
        for category, items in skills.items():
            lines.append(f'<div><strong>{escape_html(category)}:</strong>')
            if isinstance(items, list):
                items_str = ', '.join(escape_html(item) for item in items)
            else:
                items_str = escape_html(items)
            lines.append(f'{items_str}</div>')
    lines.append('</div>')


def add_projects_section(lines, resume_data):
    """Add projects section."""
    if not resume_data.get("projects"):
        return
    lines.append('<div class="section">')
    lines.append('<h2>Projects</h2>')
    for project in resume_data["projects"]:
        title = escape_html(project["title"])
        description = escape_html(project.get("description", ""))
        technologies = project.get("technologies", [])
        date = escape_html(project.get("date", ""))
        url = project.get("url", "")
        date_str = f' ({date})' if date else ''
        lines.append(f'<h3>{title}{date_str}</h3>')
        lines.append(f'<p>{description}</p>')
        if technologies:
            tech_str = ', '.join(escape_html(t) for t in technologies)
            lines.append(f'<div><strong>Technologies:</strong> {tech_str}</div>')
        if url:
            lines.append(f'<div><a href="{escape_html(url)}">View Project</a></div>')
    lines.append('</div>')


def add_volunteer_section(lines, resume_data):
    """Add volunteer experience section."""
    if not resume_data.get("volunteer"):
        return
    lines.append('<div class="section">')
    lines.append('<h2>Volunteer Experience</h2>')
    for vol in resume_data["volunteer"]:
        title = escape_html(vol["title"])
        organization = escape_html(vol["organization"])
        date = escape_html(vol.get("date", ""))
        description = escape_html(vol.get("description", ""))
        lines.append(f'<h3>{title}</h3>')
        lines.append(f'<div><strong>{organization}</strong> - <em>{date}</em></div>')
        lines.append(f'<p>{description}</p>')
    lines.append('</div>')


def add_publications_section(lines, resume_data):
    """Add publications section."""
    if not resume_data.get("publications"):
        return
    lines.append('<div class="section">')
    lines.append('<h2>Publications</h2>')
    lines.append('<ul>')
    for pub in resume_data["publications"]:
        title = escape_html(pub["title"])
        publication = escape_html(pub.get("publication", ""))
        date = escape_html(pub.get("date", ""))
        url = pub.get("url", "")
        date_str = f', {date}' if date else ''
        pub_str = f' - {publication}' if publication else ''
        title_html = f'<a href="{escape_html(url)}">{title}</a>' if url else title
        lines.append(f'<li>{title_html}{pub_str}{date_str}</li>')
    lines.append('</ul>')
    lines.append('</div>')


def add_languages_section(lines, resume_data):
    """Add languages section."""
    if not resume_data.get("languages"):
        return
    lines.append('<div class="section">')
    lines.append('<h2>Languages</h2>')
    lines.append('<ul>')
    for lang in resume_data["languages"]:
        language = escape_html(lang["language"])
        proficiency = escape_html(lang["proficiency"])
        lines.append(f'<li>{language}: {proficiency}</li>')
    lines.append('</ul>')
    lines.append('</div>')


def add_memberships_section(lines, resume_data):
    """Add professional memberships section."""
    if not resume_data.get("memberships"):
        return
    lines.append('<div class="section">')
    lines.append('<h2>Professional Memberships</h2>')
    lines.append('<ul>')
    for membership in resume_data["memberships"]:
        organization = escape_html(membership["organization"])
        title = escape_html(membership.get("title", ""))
        date = escape_html(membership.get("date", ""))
        title_str = f' ({title})' if title else ''
        date_str = f' - {date}' if date else ''
        lines.append(f'<li><strong>{organization}</strong>{title_str}{date_str}</li>')
    lines.append('</ul>')
    lines.append('</div>')


def add_portfolio_section(lines, resume_data):
    """Add portfolio section."""
    if not resume_data.get("portfolio"):
        return
    lines.append('<div class="section">')
    lines.append('<h2>Portfolio</h2>')
    lines.append('<ul>')
    for item in resume_data["portfolio"]:
        title = escape_html(item["title"])
        url = escape_html(item["url"])
        lines.append(f'<li><a href="{url}">{title}</a></li>')
    lines.append('</ul>')
    lines.append('</div>')


def add_published_games_section(lines, resume_data):
    """Add published games section."""
    if not resume_data.get("published_games"):
        return
    lines.append('<div class="section">')
    lines.append('<h2>Published Games</h2>')
    lines.append('<ul>')
    for game in resume_data["published_games"]:
        title = escape_html(game["title"])
        platforms = ', '.join(escape_html(p) for p in game["platforms"])
        year = game["year"] if isinstance(game["year"], str) else ', '.join(escape_html(y) for y in game["year"])
        lines.append(f'<li><strong>{title}</strong> ({platforms}, {year})</li>')
    lines.append('</ul>')
    lines.append('</div>')


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

def build_html_document(resume_data):
    """Construct complete HTML resume from resume data."""
    lines = []

    # =====================================================================
    # HTML STRUCTURE AND STYLING
    # =====================================================================
    lines.append('<!DOCTYPE html>')
    lines.append('<html lang="en">')
    lines.append('<head>')
    lines.append('<meta charset="UTF-8">')
    lines.append(f'<title>{escape_html(resume_data["name"])} - Resume</title>')
    lines.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    lines.append('<style>')

    # Stylesheet: match PDF aesthetic (Raleway-inspired, accent color scheme)
    style_rules = [
        'body {',
        '  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Raleway, sans-serif;',
        '  background: #f8f9fa;',
        '  color: #1e1e1e;',
        '  margin: 0;',
        '  min-height: 100vh;',
        '}',
        '.container {',
        '  max-width: 850px;',
        '  margin: 40px auto;',
        '  background: #fff;',
        '  padding: 40px 48px;',
        '  box-shadow: 0 2px 8px rgba(0,0,0,0.08);',
        '}',
        'h1 {',
        '  font-size: 2.5em;',
        '  margin: 0 0 0.3em 0;',
        '  font-weight: 600;',
        '  color: #0a3c5a;',
        '  letter-spacing: -0.5px;',
        '}',
        '.title {',
        '  font-size: 1.15em;',
        '  color: #555;',
        '  margin-bottom: 1em;',
        '  font-weight: 500;',
        '}',
        'h2 {',
        '  border-bottom: 2.5px solid #0a3c5a;',
        '  padding-bottom: 0.4em;',
        '  margin: 1.8em 0 0.8em 0;',
        '  font-size: 1.2em;',
        '  font-weight: 600;',
        '  color: #0a3c5a;',
        '}',
        'h3 {',
        '  margin: 0.8em 0 0.3em 0;',
        '  font-size: 1em;',
        '  font-weight: 600;',
        '  color: #1e1e1e;',
        '}',
        '.contact-list {',
        '  list-style: none;',
        '  padding: 0;',
        '  margin: 0 0 1.5em 0;',
        '  display: flex;',
        '  flex-wrap: wrap;',
        '  gap: 1.5em;',
        '  font-size: 0.95em;',
        '}',
        '.contact-list li { color: #555; }',
        '.section {',
        '  margin-bottom: 1.8em;',
        '}',
        'ul {',
        '  margin: 0.5em 0;',
        '  padding-left: 1.5em;',
        '}',
        'li {',
        '  margin-bottom: 0.35em;',
        '  line-height: 1.5;',
        '}',
        'em {',
        '  color: #666;',
        '  font-style: italic;',
        '}',
        'strong { color: #0a3c5a; }',
        'a {',
        '  color: #0a3c5a;',
        '  text-decoration: none;',
        '  border-bottom: 1px solid rgba(10,60,90,0.3);',
        '  transition: all 0.2s;',
        '}',
        'a:hover {',
        '  border-bottom-color: #0a3c5a;',
        '  color: #1e1e1e;',
        '}',
        '@media (max-width: 600px) {',
        '  .container { padding: 24px; }',
        '  h1 { font-size: 1.8em; }',
        '  h2 { font-size: 1.1em; }',
        '  .contact-list { flex-direction: column; gap: 0.5em; }',
        '}',
    ]
    lines.extend(style_rules)
    lines.append('</style>')
    lines.append('</head>')
    lines.append('<body>')
    lines.append('<div class="container">')

    # =====================================================================
    # HEADER: NAME AND TITLE
    # =====================================================================
    lines.append(f'<h1>{escape_html(resume_data["name"])}</h1>')
    lines.append(f'<div style="font-size:1.2em; color:#444; margin-bottom:0.7em;">{escape_html(resume_data["title"])}</div>')

    # =====================================================================
    # CONTACT INFORMATION
    # =====================================================================
    contact = resume_data.get('contact', {})
    contact_items = []
    if "location" in contact:
        contact_items.append(f'<li>📍 {escape_html(contact["location"])}</li>')
    if "phone" in contact:
        contact_items.append(f'<li>📞 {escape_html(contact["phone"])}</li>')
    if "email" in contact:
        email = escape_html(contact["email"])
        contact_items.append(f'<li>✉️ <a href="mailto:{email}">{email}</a></li>')
    if "linkedin" in contact:
        url = escape_html(contact["linkedin"])
        contact_items.append(f'<li><a href="{url}">LinkedIn</a></li>')
    if "github" in contact:
        url = escape_html(contact["github"])
        contact_items.append(f'<li><a href="{url}">GitHub</a></li>')
    if contact_items:
        lines.append('<ul class="contact-list">')
        lines.extend(contact_items)
        lines.append('</ul>')

    # Build sections in order specified by JSON
    build_sections(lines, resume_data, SECTION_BUILDERS)

    lines.append('</div>')
    lines.append('</body>')
    lines.append('</html>')

    return lines


def main():
    if len(sys.argv) < 2:
        print("Usage: python json2html.py input.json [output.html]")
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = get_output_path(json_path, sys.argv[2] if len(sys.argv) > 2 else None, '.html')

    resume_data = load_resume_json(json_path)
    html_lines = build_html_document(resume_data)

    with open(output_path, 'w', encoding='utf-8') as file_handle:
        file_handle.write('\n'.join(html_lines))

    print(f"Wrote HTML resume to: {output_path}")


if __name__ == "__main__":
    main()
