"""
Generate plain-text resume from JSON source.
Usage: python json2txt.py input.json [output.txt]
"""
import sys

from resume_builder_common import get_output_path, load_resume_json, DEFAULT_SECTION_ORDER, build_sections


SECTION_WIDTH = 78


def escape_text(text):
    """Normalize curly quotes and dashes to straight ASCII."""
    if not isinstance(text, str):
        return text
    text = text.replace(''', "'").replace(''', "'")
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace('–', '-').replace('—', '--')
    return text


def add_section_header(lines, title):
    """Add a section title with underline."""
    lines.append('')
    lines.append(title.upper())
    lines.append('─' * len(title))


def write_resume(output_path, lines):
    """Write resume lines to text file."""
    with open(output_path, 'w', encoding='utf-8') as file_handle:
        file_handle.write('\n'.join(lines).rstrip() + '\n')


# =====================================================================
# SECTION BUILDERS
# =====================================================================

def add_summary_section(lines, resume_data):
    """Add professional summary."""
    if not resume_data.get('summary'):
        return
    add_section_header(lines, 'Summary')
    lines.append(escape_text(resume_data['summary']))
    lines.append('')


def add_ai_expertise_section(lines, resume_data):
    """Add AI expertise section if present."""
    if not resume_data.get("ai_expertise"):
        return

    add_section_header(lines, 'AI Expertise')

    ai = resume_data["ai_expertise"]

    if ai.get("daily_practice"):
        lines.append('Daily practice:')
        for item in ai["daily_practice"]:
            lines.append(f'  - {escape_text(item)}')

    if ai.get("teaching"):
        lines.append('What I teach about AI:')
        for item in ai["teaching"]:
            lines.append(f'  - {escape_text(item)}')

    if ai.get("assessment"):
        lines.append('AI and assessment design (from training):')
        for item in ai["assessment"]:
            lines.append(f'  - {escape_text(item)}')

    lines.append('')


def add_experience_section(lines, resume_data):
    """Add experience section."""
    if not resume_data.get('experience'):
        return
    add_section_header(lines, 'Experience')
    for job in resume_data['experience']:
        title = escape_text(job['title'])
        company = escape_text(job['company'])
        lines.append(f"{title} | {company}")
        lines.append(escape_text(job['date']))
        if job.get('technologies'):
            techs = ' / '.join(escape_text(t) for t in job['technologies'])
            lines.append(f'  {techs}')
        if job.get('description'):
            lines.append(escape_text(job['description']))
        if job.get('bullets'):
            for bullet in job['bullets']:
                lines.append(f"  * {escape_text(bullet)}")
        lines.append('')


def add_education_section(lines, resume_data):
    """Add education section."""
    if not resume_data.get('education'):
        return
    add_section_header(lines, 'Education')
    for school in resume_data['education']:
        degree = escape_text(school.get('degree', ''))
        institution = escape_text(school.get('institution', ''))
        lines.append(f"{degree} | {institution}")
        if school.get('date'):
            lines.append(escape_text(school['date']))
        if school.get('field'):
            lines.append(f"Field: {escape_text(school['field'])}")
        if school.get('thesis'):
            lines.append(f"Thesis: {escape_text(school['thesis'])}")
        lines.append('')


def add_certifications_section(lines, resume_data):
    """Add certifications section."""
    if not resume_data.get('certifications'):
        return
    add_section_header(lines, 'Certifications')
    for cert in resume_data['certifications']:
        parts = [escape_text(cert['title'])]
        if cert.get('issuer'):
            parts.append(escape_text(cert['issuer']))
        if cert.get('date'):
            parts.append(escape_text(cert['date']))
        lines.append('- ' + ', '.join(parts))
        if cert.get('credential_id'):
            lines.append(f"  ID: {escape_text(cert['credential_id'])}")
    lines.append('')


def add_awards_section(lines, resume_data):
    """Add awards section."""
    if not resume_data.get('awards'):
        return
    add_section_header(lines, 'Awards')
    for award in resume_data['awards']:
        parts = [escape_text(award['title'])]
        if award.get('organization'):
            parts.append(escape_text(award['organization']))
        if award.get('year'):
            parts.append(escape_text(award['year']))
        lines.append('- ' + ', '.join(parts))
    lines.append('')


def add_skills_section(lines, resume_data):
    """Add skills section."""
    if not resume_data.get('skills'):
        return
    add_section_header(lines, 'Skills')
    skills = resume_data['skills']
    if isinstance(skills, dict):
        for category, items in skills.items():
            lines.append(f"{escape_text(category)}:")
            if isinstance(items, list):
                items_str = ', '.join(escape_text(item) for item in items)
            else:
                items_str = escape_text(items)
            lines.append(f"  {items_str}")
    lines.append('')


def add_projects_section(lines, resume_data):
    """Add projects section."""
    if not resume_data.get('projects'):
        return
    add_section_header(lines, 'Projects')
    for project in resume_data['projects']:
        title = escape_text(project['title'])
        description = escape_text(project.get('description', ''))
        technologies = project.get('technologies', [])
        date = escape_text(project.get('date', ''))
        date_str = f" ({date})" if date else ""
        lines.append(f"{title}{date_str}")
        lines.append(description)
        if technologies:
            tech_str = ', '.join(escape_text(t) for t in technologies)
            lines.append(f"Technologies: {tech_str}")
        lines.append('')


def add_volunteer_section(lines, resume_data):
    """Add volunteer experience section."""
    if not resume_data.get('volunteer'):
        return
    add_section_header(lines, 'Volunteer Experience')
    for vol in resume_data['volunteer']:
        title = escape_text(vol['title'])
        organization = escape_text(vol['organization'])
        date = escape_text(vol.get('date', ''))
        description = escape_text(vol.get('description', ''))
        lines.append(f"{title} | {organization}")
        lines.append(date)
        lines.append(description)
        lines.append('')


def add_publications_section(lines, resume_data):
    """Add publications section."""
    if not resume_data.get('publications'):
        return
    add_section_header(lines, 'Publications')
    for pub in resume_data['publications']:
        parts = [escape_text(pub['title'])]
        if pub.get('publication'):
            parts.append(escape_text(pub['publication']))
        if pub.get('date'):
            parts.append(escape_text(pub['date']))
        lines.append('- ' + ', '.join(parts))
        if pub.get('url'):
            lines.append(f"  URL: {escape_text(pub['url'])}")
    lines.append('')


def add_languages_section(lines, resume_data):
    """Add languages section."""
    if not resume_data.get('languages'):
        return
    add_section_header(lines, 'Languages')
    for lang in resume_data['languages']:
        language = escape_text(lang['language'])
        proficiency = escape_text(lang['proficiency'])
        lines.append(f"- {language}: {proficiency}")
    lines.append('')


def add_memberships_section(lines, resume_data):
    """Add professional memberships section."""
    if not resume_data.get('memberships'):
        return
    add_section_header(lines, 'Professional Memberships')
    for membership in resume_data['memberships']:
        parts = [escape_text(membership['organization'])]
        if membership.get('title'):
            parts.append(escape_text(membership['title']))
        if membership.get('date'):
            parts.append(escape_text(membership['date']))
        lines.append('- ' + ', '.join(parts))
    lines.append('')


def add_portfolio_section(lines, resume_data):
    """Add portfolio section."""
    if not resume_data.get('portfolio'):
        return
    add_section_header(lines, 'Portfolio')
    for item in resume_data['portfolio']:
        title = escape_text(item['title'])
        url = escape_text(item['url'])
        lines.append(f"- {title}: {url}")
    lines.append('')


def add_published_games_section(lines, resume_data):
    """Add published games section."""
    if not resume_data.get('published_games'):
        return
    add_section_header(lines, 'Published Games')
    for game in resume_data['published_games']:
        title = escape_text(game['title'])
        platforms = ', '.join(escape_text(p) for p in game['platforms'])
        year = game['year'] if isinstance(game['year'], str) else ', '.join(escape_text(y) for y in game['year'])
        lines.append(f"- {title} ({platforms}; {year})")
    lines.append('')


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
        print("Usage: python json2txt.py input.json [output.txt]")
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = get_output_path(json_path, sys.argv[2] if len(sys.argv) > 2 else None, '.txt')

    resume_data = load_resume_json(json_path)
    lines = []

    # Header
    lines.append(escape_text(resume_data['name']))
    lines.append(escape_text(resume_data['title']))
    lines.append('')

    # Contact Info
    contact = resume_data.get('contact', {})
    contact_lines = []
    if 'location' in contact:
        contact_lines.append(f"Location: {escape_text(contact['location'])}")
    if 'email' in contact:
        contact_lines.append(f"Email: {escape_text(contact['email'])}")
    if 'phone' in contact:
        contact_lines.append(f"Phone: {escape_text(contact['phone'])}")
    if 'linkedin' in contact:
        contact_lines.append(f"LinkedIn: {escape_text(contact['linkedin'])}")
    if 'github' in contact:
        contact_lines.append(f"GitHub: {escape_text(contact['github'])}")
    if 'website' in contact:
        contact_lines.append(f"Website: {escape_text(contact['website'])}")

    if contact_lines:
        add_section_header(lines, 'Contact')
        lines.extend(contact_lines)
        lines.append('')

    # Build sections in order specified by JSON
    build_sections(lines, resume_data, SECTION_BUILDERS)

    write_resume(output_path, lines)
    print(f"Wrote plain-text resume to: {output_path}")


if __name__ == '__main__':
    main()
