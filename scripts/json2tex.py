"""
Generate LaTeX resume (article style) from JSON source.
Usage: python json2tex.py input.json [output.tex]
"""
import json
import os
import sys


def escape_latex(text):
    """Escape LaTeX special characters and normalize quotes and dashes."""
    if not isinstance(text, str):
        return text

    # Normalize Unicode quotes to straight ASCII versions.
    text = text.replace(''', "'").replace(''', "'")
    text = text.replace('"', '``').replace('"', "''")

    # Replace Unicode dashes with LaTeX equivalents.
    text = text.replace('–', '--').replace('—', '---')

    # Escape LaTeX special characters (order matters - backslash first).
    text = (text.replace('\\', '\\textbackslash{}')
                .replace('&', '\\&')
                .replace('%', '\\%')
                .replace('$', '\\$')
                .replace('#', '\\#')
                .replace('_', '\\_')
                .replace('{', '\\{')
                .replace('}', '\\}')
                .replace('~', '\\textasciitilde{}')
                .replace('^', '\\textasciicircum{}'))
    return text


# =====================================================================
# UTILITY FUNCTIONS
# =====================================================================

def get_output_path(json_path, output_arg):
    """Determine output file path: use provided arg or derive from input."""
    if output_arg:
        return output_arg
    return os.path.splitext(json_path)[0] + '.tex'


def load_resume_json(json_path):
    """Read and parse resume JSON file."""
    with open(json_path, encoding='utf-8') as file_handle:
        return json.load(file_handle)


# =====================================================================
# DOCUMENT BUILDING FUNCTIONS
# =====================================================================

def add_document_setup(lines):
    """Add LaTeX packages and configuration."""
    lines.append('\\documentclass[10pt]{article}')
    lines.append('\\usepackage[letterpaper,margin=0.7in]{geometry}')
    lines.append('\\usepackage{enumitem}')
    lines.append('\\usepackage{titlesec}')
    lines.append('\\usepackage[hidelinks]{hyperref}')
    lines.append('\\usepackage{xcolor}')
    lines.append('\\usepackage{ragged2e}')
    lines.append('\\usepackage{moresize}')
    lines.append('\\usepackage{fontawesome5}')
    lines.append('\\usepackage[default]{raleway}')
    lines.append('\\usepackage{multicol}')
    lines.append('')

    # Colour definitions
    lines.append('% Colour scheme')
    lines.append('\\definecolor{accent}{RGB}{10,60,90}')
    lines.append('\\definecolor{secondary}{RGB}{30,30,30}')
    lines.append('')

    # Font and layout settings
    lines.append('% Font and layout')
    lines.append('\\renewcommand{\\familydefault}{\\sfdefault}')
    lines.append('\\setlength{\\parindent}{0pt}')
    lines.append('\\newcommand{\\mytitle}[1]{\\color{accent}\\normalfont\\large\\bfseries{#1}}')
    lines.append('\\newcommand{\\tech}[1]{\\textcolor{secondary}{\\textbf{#1}}}')
    lines.append('')

    # Section formatting
    lines.append('% Section style')
    lines.append('\\titleformat{\\section}{\\mytitle}{}{0em}{}[{\\titlerule[0.8pt]}]')
    lines.append('\\titlespacing{\\section}{0pt}{9pt}{5pt}')
    lines.append('')

    # Bullet point styling
    lines.append('% Bullet list formatting')
    lines.append('\\setlist[itemize]{leftmargin=*,nosep,after=\\vspace{3pt}}')
    lines.append('\\setlist[itemize]{label=\\color{accent}\\scriptsize\\raisebox{0.4ex}{\\textbullet}}')
    lines.append('')

    # Experience entry command: title, dates, company, description
    lines.append('% Custom macros')
    lines.append('\\newcommand{\\experience}[4]{%')
    lines.append('  \\vspace{4pt}')
    lines.append('  \\begin{tabular*}{\\textwidth}{@{}l@{\\extracolsep{\\fill}}r@{}}')
    lines.append('    \\textbf{#1} & \\textit{#2} \\\\')
    lines.append('    \\textit{\\small#3} & \\textit{\\small#4}')
    lines.append('  \\end{tabular*}')
    lines.append('  \\vspace{-4pt}')
    lines.append('}')
    lines.append('')


def add_header_section(lines, resume_data):
    """Add name, title, and contact information."""
    lines.append('% ===== Header =====')
    lines.append('\\begin{center}')

    name_parts = resume_data["name"].split()
    if name_parts:
        first = escape_latex(name_parts[0]) if name_parts else ""
        last = escape_latex(name_parts[-1]) if len(name_parts) > 1 else ""
        lines.append(f'\\colorbox{{gray}}{{\\HUGE\\textcolor{{white}}{{\\textbf{{{first}}}}}}} \\\\[2pt]')
        lines.append(f'\\colorbox{{gray}}{{\\HUGE\\textcolor{{white}}{{\\textbf{{{last}}}}}}} \\\\[6pt]')

    if resume_data.get("title"):
        lines.append(f'    {{\\Large \\tech{{{escape_latex(resume_data["title"])}}}}} \\\\[6pt]')

    contact = resume_data.get("contact", {})
    contact_items = []

    if contact.get("email"):
        email = escape_latex(contact["email"])
        contact_items.append(f'\\faIcon{{at}}~\\href{{mailto:{email}}}{{{email}}}')

    if contact.get("phone"):
        phone = escape_latex(contact["phone"])
        contact_items.append(f'\\faIcon{{phone}}~{phone}')

    if contact.get("linkedin"):
        url = contact["linkedin"]
        parts = [p for p in url.split('/') if p]
        label = parts[-1] if parts else url
        contact_items.append(f'\\faIcon{{linkedin}}~\\href{{{escape_latex(url)}}}{{linkedin.com/in/{escape_latex(label)}}}')

    if contact.get("github"):
        url = contact["github"]
        parts = [p for p in url.split('/') if p]
        label = parts[-1] if parts else url
        contact_items.append(f'\\faIcon{{github}}~\\href{{{escape_latex(url)}}}{{{escape_latex(label)}}}')

    if contact_items:
        lines.append('    ' + '\\hfill '.join(contact_items))

    if contact.get("location"):
        lines.append(f'    \\\\[2pt]')
        lines.append(f'    \\textit{{{escape_latex(contact["location"])}}}~\\textbullet~\\textit{{Remote}}')

    lines.append('\\end{center}')
    lines.append('')


def add_summary_section(lines, resume_data):
    """Add professional summary."""
    if not resume_data.get("summary"):
        return

    lines.append('% ===== Summary =====')
    lines.append('\\section*{Summary}')
    lines.append('')
    lines.append(escape_latex(resume_data["summary"]))
    lines.append('')


def add_ai_expertise_section(lines, resume_data):
    """Add AI expertise section if present."""
    if not resume_data.get("ai_expertise"):
        return

    lines.append('% ===== AI Expertise =====')
    lines.append('\\section*{AI Expertise}')
    lines.append('')

    ai = resume_data["ai_expertise"]

    if ai.get("daily_practice"):
        lines.append('\\textbf{Daily practice:}')
        lines.append('\\begin{itemize}')
        for item in ai["daily_practice"]:
            lines.append(f'    \\item {escape_latex(item)}')
        lines.append('\\end{itemize}')
        lines.append('')

    if ai.get("teaching"):
        lines.append('\\textbf{What I teach about AI:}')
        lines.append('\\begin{itemize}')
        for item in ai["teaching"]:
            lines.append(f'    \\item {escape_latex(item)}')
        lines.append('\\end{itemize}')
        lines.append('')

    if ai.get("assessment"):
        lines.append('\\textbf{AI and assessment design (from training):}')
        lines.append('\\begin{itemize}')
        for item in ai["assessment"]:
            lines.append(f'    \\item {escape_latex(item)}')
        lines.append('\\end{itemize}')
        lines.append('')


def add_experience_section(lines, resume_data):
    """Add experience section (generic - can be teaching or industry)."""
    experience = resume_data.get("experience") or resume_data.get("teaching_experience") or resume_data.get("industry_experience")
    if not experience:
        return

    lines.append('% ===== Experience =====')
    lines.append('\\section*{Experience}')
    lines.append('')

    for job in experience:
        title = escape_latex(job["title"])
        dates = escape_latex(job.get("date", "") or job.get("dates", ""))
        company = escape_latex(job.get("company", ""))

        lines.append(f'\\experience{{{title}}}{{{dates}}}{{{company}}}{{}}')

        if job.get("technologies"):
            techs = job["technologies"]
            tech_str = ' / '.join([escape_latex(t) for t in techs])
            lines.append(f'\\hspace{{0.5cm}}\\texttt{{{tech_str}}}')

        if job.get("description"):
            lines.append(escape_latex(job["description"]))

        if job.get("bullets"):
            lines.append('\\begin{itemize}')
            for bullet in job["bullets"]:
                lines.append(f'    \\item {escape_latex(bullet)}')
            lines.append('\\end{itemize}')

        lines.append('')


def add_education_section(lines, resume_data):
    """Add education section."""
    if not resume_data.get("education"):
        return

    lines.append('% ===== Education =====')
    lines.append('\\section*{Education}')
    lines.append('\\begin{itemize}')

    for school in resume_data["education"]:
        degree = escape_latex(school.get("degree", ""))
        institution = escape_latex(school.get("institution", ""))
        year = escape_latex(school.get("year", "") or school.get("date", ""))

        item_text = f'\\tech{{{degree}}} -- {institution} \\hfill {year}'
        lines.append(f'    \\item {item_text}')

        field = school.get("field")
        thesis = school.get("thesis")
        if field:
            lines.append(f'    \\textit{{\\small {escape_latex(field)}}}')
        if thesis:
            lines.append(f'    \\textit{{\\small Thesis: {escape_latex(thesis)}}}')

        if school.get("details"):
            for detail in school["details"]:
                lines.append(f'    \\textit{{\\small {escape_latex(detail)}}}')

    lines.append('\\end{itemize}')
    lines.append('')


def add_awards_section(lines, resume_data):
    """Add honours and awards section."""
    if not resume_data.get("awards"):
        return

    lines.append('% ===== Honours & Awards =====')
    lines.append('\\section*{Honours \\& Awards}')
    lines.append('\\begin{itemize}[nosep,leftmargin=*]')

    for award in resume_data["awards"]:
        title = escape_latex(award.get("title", ""))
        org = escape_latex(award.get("organization", ""))
        year = escape_latex(award.get("year", ""))

        org_str = f' -- {org}' if org else ''
        year_str = f' \\hfill {year}' if year else ''
        lines.append(f'    \\item {title}{org_str}{year_str}')

    lines.append('\\end{itemize}')
    lines.append('')


def add_skills_section(lines, resume_data):
    """Add technical skills section."""
    if not resume_data.get("skills"):
        return

    lines.append('% ===== Technical Skills =====')
    lines.append('\\section*{Technical Skills}')

    skills = resume_data["skills"]
    for category, items in skills.items():
        if isinstance(items, list):
            items_str = ', '.join([escape_latex(item) for item in items])
        else:
            items_str = escape_latex(items)
        lines.append(f'\\textbf{{{escape_latex(category)}:}} {items_str} \\\\')

    lines.append('')


def add_languages_section(lines, resume_data):
    """Add languages section."""
    if not resume_data.get("languages"):
        return

    lines.append('% ===== Languages =====')
    lines.append('\\section*{Languages}')
    lines.append('\\begin{itemize}')

    for lang in resume_data["languages"]:
        language = escape_latex(lang.get("language", ""))
        proficiency = escape_latex(lang.get("proficiency", ""))
        lines.append(f'    \\item \\textbf{{{language}}} -- {proficiency}')

    lines.append('\\end{itemize}')
    lines.append('')


def add_portfolio_section(lines, resume_data):
    """Add portfolio section."""
    if not resume_data.get("portfolio"):
        return

    lines.append('% ===== Portfolio =====')
    lines.append('\\section*{Portfolio}')

    for item in resume_data["portfolio"]:
        title = escape_latex(item.get("title", ""))
        url = item.get("url", "")
        icon = "github" if "github.com" in url else "globe"
        lines.append(f'\\faIcon{{{icon}}}~\\href{{{escape_latex(url)}}}{{{title}}}\\\\' )

    lines.append('')


def add_published_games_section(lines, resume_data):
    """Add published games section."""
    if not resume_data.get("published_games"):
        return

    lines.append('% ===== Published Games =====')
    lines.append('\\section*{Published Games}')

    for game in resume_data["published_games"]:
        title = escape_latex(game.get("title", ""))
        platforms = game.get("platforms", [])
        year = game.get("year", "")

        platforms_str = ', '.join([escape_latex(p) for p in platforms]) if isinstance(platforms, list) else escape_latex(platforms)
        year_str = escape_latex(year) if isinstance(year, str) else ', '.join([escape_latex(y) for y in year])

        lines.append(f'{title} -- {platforms_str} ({year_str})\\\\')

    lines.append('')


def add_certifications_section(lines, resume_data):
    """Add certifications section."""
    if not resume_data.get("certifications"):
        return

    lines.append('% ===== Certifications =====')
    lines.append('\\section*{Certifications}')
    lines.append('\\begin{itemize}[nosep,leftmargin=*]')

    for cert in resume_data["certifications"]:
        title = escape_latex(cert.get("title", ""))
        issuer = escape_latex(cert.get("issuer", ""))
        date = escape_latex(cert.get("date", ""))
        credential_id = cert.get("credential_id", "")

        issuer_str = f' -- {issuer}' if issuer else ''
        date_str = f' \\hfill {date}' if date else ''
        lines.append(f'    \\item {title}{issuer_str}{date_str}')
        if credential_id:
            lines.append(f'         (ID: {escape_latex(credential_id)})')

    lines.append('\\end{itemize}')
    lines.append('')


def add_projects_section(lines, resume_data):
    """Add projects section."""
    if not resume_data.get("projects"):
        return

    lines.append('% ===== Projects =====')
    lines.append('\\section*{Projects}')

    for project in resume_data["projects"]:
        title = escape_latex(project.get("title", ""))
        description = escape_latex(project.get("description", ""))
        technologies = project.get("technologies", [])
        date = escape_latex(project.get("date", ""))

        date_str = f' \\hfill {date}' if date else ''
        lines.append(f'\\textbf{{{title}}}{date_str} \\\\')
        lines.append(f'{description} \\\\')

        if technologies:
            tech_str = ', '.join([escape_latex(t) for t in technologies])
            lines.append(f'\\textcolor{{secondary}}{{\\textbf{{Technologies:}}}} {tech_str} \\\\')

        lines.append('')


def add_volunteer_section(lines, resume_data):
    """Add volunteer experience section."""
    if not resume_data.get("volunteer"):
        return

    lines.append('% ===== Volunteer Experience =====')
    lines.append('\\section*{Volunteer Experience}')

    for vol in resume_data["volunteer"]:
        date = escape_latex(vol.get("date", ""))
        title = escape_latex(vol.get("title", ""))
        organization = escape_latex(vol.get("organization", ""))
        description = escape_latex(vol.get("description", ""))

        lines.append(f'\\textbf{{{title}}} \\hfill {date} \\\\')
        lines.append(f'\\textit{{{organization}}} \\\\')
        lines.append(f'{description} \\\\')
        lines.append('')


def add_publications_section(lines, resume_data):
    """Add publications section."""
    if not resume_data.get("publications"):
        return

    lines.append('% ===== Publications =====')
    lines.append('\\section*{Publications}')
    lines.append('\\begin{itemize}[nosep,leftmargin=*]')

    for pub in resume_data["publications"]:
        title = escape_latex(pub.get("title", ""))
        publication = escape_latex(pub.get("publication", ""))
        date = escape_latex(pub.get("date", ""))

        date_str = f' \\hfill {date}' if date else ''
        lines.append(f'    \\item {title} ({publication}){date_str}')

    lines.append('\\end{itemize}')
    lines.append('')


def add_memberships_section(lines, resume_data):
    """Add professional memberships section."""
    if not resume_data.get("memberships"):
        return

    lines.append('% ===== Professional Memberships =====')
    lines.append('\\section*{Professional Memberships}')
    lines.append('\\begin{itemize}[nosep,leftmargin=*]')

    for membership in resume_data["memberships"]:
        organization = escape_latex(membership.get("organization", ""))
        title = escape_latex(membership.get("title", ""))
        date = escape_latex(membership.get("date", ""))

        date_str = f' \\hfill {date}' if date else ''
        lines.append(f'    \\item {organization} ({title}){date_str}')

    lines.append('\\end{itemize}')
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

DEFAULT_SECTION_ORDER = [
    'summary',
    'ai_expertise',
    'experience',
    'education',
    'certifications',
    'awards',
    'skills',
    'projects',
    'volunteer',
    'publications',
    'languages',
    'memberships',
    'portfolio',
    'published_games',
]


def build_sections(lines, resume_data):
    """Build sections in order specified by JSON, respecting filters."""
    section_order = resume_data.get('section_order', DEFAULT_SECTION_ORDER)
    section_filter = set(resume_data.get('section_filter', []))

    for section_name in section_order:
        if section_name not in section_filter and section_name in SECTION_BUILDERS:
            SECTION_BUILDERS[section_name](lines, resume_data)


# =====================================================================
# MAIN ENTRY POINT
# =====================================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python json2tex.py input.json [output.tex]")
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = get_output_path(json_path, sys.argv[2] if len(sys.argv) > 2 else None)

    resume_data = load_resume_json(json_path)
    lines = []

    # Build complete LaTeX document.
    add_document_setup(lines)
    lines.append('\\begin{document}')
    lines.append('')
    add_header_section(lines, resume_data)
    build_sections(lines, resume_data)
    lines.append('\\end{document}')

    if os.path.exists(output_path):
        print(f"Overwriting existing file: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as file_handle:
        file_handle.write('\n'.join(lines))

    print(f"Wrote LaTeX CV (article style) to: {output_path}")


if __name__ == "__main__":
    main()
