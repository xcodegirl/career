"""
Generate HTML resume from JSON source.
Usage: python json2html.py input.json [output.html]
"""
import json
import os
import sys


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


def get_output_path(json_path, output_arg):
    """Determine output file path: use provided arg or derive from input."""
    if output_arg:
        return output_arg
    return os.path.splitext(json_path)[0] + '.html'


def load_resume_json(json_path):
    """Read and parse resume JSON file."""
    with open(json_path, encoding='utf-8') as file_handle:
        return json.load(file_handle)


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

    # Stylesheet: clean, readable design
    style_rules = [
        'body {',
        '  font-family: "Segoe UI", Arial, sans-serif;',
        '  background: linear-gradient(120deg, #e0e7ff 0%, #f8fafc 100%);',
        '  color: #232946;',
        '  margin: 0;',
        '  min-height: 100vh;',
        '}',
        '.container {',
        '  max-width: 800px;',
        '  margin: 48px auto 48px auto;',
        '  background: #fff;',
        '  border-radius: 18px;',
        '  box-shadow: 0 8px 32px rgba(44,62,80,0.10);',
        '  padding: 48px 32px 40px 32px;',
        '  border: 1px solid #e0e0e0;',
        '}',
        'h1 { font-size: 2.7em; margin-bottom: 0.1em; letter-spacing: 1px; color: #232946; }',
        'h2 { border-bottom: 2px solid #e0e7ff; padding-bottom: 0.2em; margin-top: 2em; color: #3d5af1; font-size: 1.3em; }',
        'h3 { margin-bottom: 0.2em; margin-top: 1.2em; font-size: 1.1em; color: #232946; }',
        '.contact-list { list-style: none; padding: 0; margin-bottom: 1.5em; }',
        '.contact-list li { display: inline-block; margin-right: 1.5em; color: #555; font-size: 1em; }',
        'ul { margin-top: 0.3em; margin-bottom: 1em; }',
        'li { margin-bottom: 0.2em; }',
        '.section { margin-bottom: 2em; }',
        'code { background: #f3f3f3; border-radius: 3px; padding: 2px 5px; font-size: 0.97em; }',
        'em { color: #666; }',
        'a { color: #3d5af1; text-decoration: none; border-bottom: 1px dotted #3d5af1; transition: color 0.2s, border-bottom 0.2s; }',
        'a:hover { color: #232946; border-bottom: 1px solid #232946; }',
        '@media (max-width: 600px) {',
        '  .container { padding: 18px 4vw 18px 4vw; }',
        '  h1 { font-size: 2em; }',
        '  h2 { font-size: 1.1em; }',
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
    if "discord" in contact:
        contact_items.append(f'<li>Discord: <code>{escape_html(contact["discord"])}</code></li>')

    if contact_items:
        lines.append('<ul class="contact-list">')
        lines.extend(contact_items)
        lines.append('</ul>')

    # =====================================================================
    # SUMMARY SECTION
    # =====================================================================
    if resume_data.get("summary"):
        lines.append('<div class="section">')
        lines.append('<h2>Summary</h2>')
        lines.append(f'<p>{escape_html(resume_data["summary"])}</p>')
        lines.append('</div>')

    # =====================================================================
    # EXPERIENCE SECTION
    # =====================================================================
    if resume_data.get("experience"):
        lines.append('<div class="section">')
        lines.append('<h2>Experience</h2>')
        for job in resume_data["experience"]:
            title = escape_html(job["title"])
            company = escape_html(job["company"])
            lines.append(f'<h3>{title} <span style="font-weight:normal;">- {company}</span></h3>')
            lines.append(f'<div><em>{escape_html(job["date"])}</em></div>')
            lines.append(f'<ul><li>{escape_html(job["description"])}</li>')
            if job.get("technologies"):
                techs = ", ".join(escape_html(t) for t in job["technologies"])
                lines.append(f'<li><strong>Technologies:</strong> {techs}</li>')
            lines.append('</ul>')
        lines.append('</div>')

    # =====================================================================
    # EDUCATION SECTION
    # =====================================================================
    if resume_data.get("education"):
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

    # =====================================================================
    # COMMUNITY OUTREACH SECTION
    # =====================================================================
    if resume_data.get("community_outreach"):
        lines.append('<div class="section">')
        lines.append('<h2>Community Outreach</h2>')
        lines.append('<ul>')
        for entry in resume_data["community_outreach"]:
            role = escape_html(entry['role'])
            org = f", {escape_html(entry['organization'])}" if entry.get("organization") else ""
            years = escape_html(entry['years'])
            lines.append(f'<li><strong>{role}</strong>{org} ({years})</li>')
        lines.append('</ul>')
        lines.append('</div>')

    # =====================================================================
    # AWARDS SECTION
    # =====================================================================
    if resume_data.get("awards"):
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

    # =====================================================================
    # LANGUAGES SECTION
    # =====================================================================
    if resume_data.get("languages"):
        lines.append('<div class="section">')
        lines.append('<h2>Languages</h2>')
        lines.append('<ul>')
        for lang in resume_data["languages"]:
            language = escape_html(lang["language"])
            proficiency = escape_html(lang["proficiency"])
            lines.append(f'<li>{language}: {proficiency}</li>')
        lines.append('</ul>')
        lines.append('</div>')

    # =====================================================================
    # PORTFOLIO SECTION
    # =====================================================================
    if resume_data.get("portfolio"):
        lines.append('<div class="section">')
        lines.append('<h2>Portfolio</h2>')
        lines.append('<ul>')
        for item in resume_data["portfolio"]:
            title = escape_html(item["title"])
            url = escape_html(item["url"])
            lines.append(f'<li><a href="{url}">{title}</a></li>')
        lines.append('</ul>')
        lines.append('</div>')

    # =====================================================================
    # PUBLISHED GAMES SECTION
    # =====================================================================
    if resume_data.get("published_games"):
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
    # CERTIFICATIONS SECTION
    # =====================================================================
    if resume_data.get("certifications"):
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

    # =====================================================================
    # PROJECTS SECTION
    # =====================================================================
    if resume_data.get("projects"):
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

    # =====================================================================
    # VOLUNTEER EXPERIENCE SECTION
    # =====================================================================
    if resume_data.get("volunteer"):
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

    # =====================================================================
    # PUBLICATIONS SECTION
    # =====================================================================
    if resume_data.get("publications"):
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

    # =====================================================================
    # MEMBERSHIPS SECTION
    # =====================================================================
    if resume_data.get("memberships"):
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

    # =====================================================================
    # SKILLS SECTION
    # =====================================================================
    if resume_data.get("skills"):
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

    lines.append('</div>')
    lines.append('</body>')
    lines.append('</html>')

    return lines


def main():
    if len(sys.argv) < 2:
        print("Usage: python json2html.py input.json [output.html]")
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = get_output_path(json_path, sys.argv[2] if len(sys.argv) > 2 else None)

    resume_data = load_resume_json(json_path)
    html_lines = build_html_document(resume_data)

    with open(output_path, 'w', encoding='utf-8') as file_handle:
        file_handle.write('\n'.join(html_lines))

    print(f"Wrote HTML resume to: {output_path}")


if __name__ == "__main__":
    main()
