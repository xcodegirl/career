"""
Generate LaTeX resume (plain article style) from JSON source.
Usage: python json2tex.py input.json [output.tex]
"""
import os
import sys

from resume_builder_common import get_output_path, load_resume_json, build_sections


def escape_latex(text):
    """Escape LaTeX special characters and normalize quotes and dashes."""
    if not isinstance(text, str):
        return text
    text = text.replace('‘', "'").replace('’', "'")
    text = text.replace('“', '``').replace('”', "''")
    text = text.replace('–', '--').replace('—', '---')
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


def description_lines(job):
    """Return LaTeX lines for a job's description paragraph and/or bullets."""
    out = []
    desc = job.get('description')
    if desc and isinstance(desc, str):
        out.append(escape_latex(desc))
        out.append('')
    bullets = job.get('bullets')
    if bullets:
        out.append('\\begin{itemize}')
        for item in bullets:
            out.append(f'    \\item {escape_latex(item)}')
        out.append('\\end{itemize}')
    return out


# =====================================================================
# DOCUMENT SETUP
# =====================================================================

def add_document_setup(lines):
    lines.append('\\documentclass[10pt]{article}')
    lines.append('\\usepackage[letterpaper, margin=0.75in]{geometry}')
    lines.append('\\usepackage{enumitem}')
    lines.append('\\usepackage[hidelinks]{hyperref}')
    lines.append('\\usepackage{titlesec}')
    lines.append('\\usepackage{fontawesome5}')
    lines.append('')
    lines.append('\\setlength{\\parindent}{0pt}')
    lines.append('\\setlength{\\parskip}{0pt}')
    lines.append('\\titleformat{\\section}{\\large\\bfseries}{}{0em}{}[\\titlerule]')
    lines.append('\\titlespacing{\\section}{0pt}{8pt}{4pt}')
    lines.append('\\setlist[itemize]{leftmargin=*, nosep, topsep=2pt}')
    lines.append('\\renewcommand{\\labelitemi}{\\textbullet}')
    lines.append('')


# =====================================================================
# HEADER
# =====================================================================

def add_header_section(lines, resume_data):
    lines.append('\\begin{center}')
    lines.append(f'{{\\LARGE\\bfseries {escape_latex(resume_data["name"])}}}\\\\[4pt]')
    if resume_data.get('title'):
        lines.append(f'{{\\large {escape_latex(resume_data["title"])}}}\\\\[4pt]')

    contact = resume_data.get('contact', {})
    items = []
    if contact.get('email'):
        items.append(f'\\faIcon{{at}}~\\href{{mailto:{escape_latex(contact["email"])}}}{{{escape_latex(contact["email"])}}}')
    if contact.get('phone'):
        items.append(f'\\faIcon{{phone}}~{escape_latex(contact["phone"])}')
    if contact.get('location'):
        items.append(f'\\faIcon{{map-marker-alt}}~{escape_latex(contact["location"])}')
    if contact.get('linkedin'):
        url = contact['linkedin']
        parts = [p for p in url.split('/') if p]
        label = parts[-1] if parts else url
        items.append(f'\\faIcon{{linkedin}}~\\href{{{escape_latex(url)}}}{{linkedin.com/in/{escape_latex(label)}}}')
    if contact.get('github'):
        url = contact['github']
        parts = [p for p in url.split('/') if p]
        label = parts[-1] if parts else url
        items.append(f'\\faIcon{{github}}~\\href{{{escape_latex(url)}}}{{{escape_latex(label)}}}')
    if items:
        lines.append(' \\enspace|\\enspace '.join(items) + '\\\\')

    lines.append('\\end{center}')
    lines.append('\\vspace{4pt}')
    lines.append('')


# =====================================================================
# SECTION BUILDERS
# =====================================================================

def add_summary_section(lines, resume_data):
    if not resume_data.get('summary'):
        return
    lines.append('\\section*{Summary}')
    lines.append(escape_latex(resume_data['summary']))
    lines.append('')


def add_ai_expertise_section(lines, resume_data):
    if not resume_data.get('ai_expertise'):
        return
    lines.append('\\section*{AI Expertise}')
    ai = resume_data['ai_expertise']
    if ai.get('daily_practice'):
        lines.append('\\textbf{Daily practice:}')
        lines.append('\\begin{itemize}')
        for item in ai['daily_practice']:
            lines.append(f'    \\item {escape_latex(item)}')
        lines.append('\\end{itemize}')
    if ai.get('teaching'):
        lines.append('\\textbf{What I teach about AI:}')
        lines.append('\\begin{itemize}')
        for item in ai['teaching']:
            lines.append(f'    \\item {escape_latex(item)}')
        lines.append('\\end{itemize}')
    if ai.get('assessment'):
        lines.append('\\textbf{AI and assessment design:}')
        lines.append('\\begin{itemize}')
        for item in ai['assessment']:
            lines.append(f'    \\item {escape_latex(item)}')
        lines.append('\\end{itemize}')
    lines.append('')


def add_experience_section(lines, resume_data):
    experience = resume_data.get('experience') or resume_data.get('teaching_experience') or resume_data.get('industry_experience')
    if not experience:
        return
    lines.append('\\section*{Experience}')
    for job in experience:
        title = escape_latex(job.get('title', ''))
        company = escape_latex(job.get('company', ''))
        date = escape_latex(job.get('date', '') or job.get('dates', ''))
        lines.append(f'\\textbf{{{title}}}, \\textit{{{company}}} \\hfill {date}')
        if job.get('technologies'):
            tech_str = ', '.join(escape_latex(t) for t in job['technologies'])
            lines.append(f'\\\\\\texttt{{\\small {tech_str}}}')
        lines.append('\\\\[-2pt]')
        lines.extend(description_lines(job))
        lines.append('')


def add_skills_section(lines, resume_data):
    if not resume_data.get('skills'):
        return
    lines.append('\\section*{Technical Skills}')
    skills = resume_data['skills']
    for category, items in skills.items():
        if isinstance(items, list):
            items_str = ', '.join(escape_latex(i) for i in items)
        else:
            items_str = escape_latex(items)
        lines.append(f'\\textbf{{{escape_latex(category)}:}} {items_str}\\\\[2pt]')
    lines.append('')


def add_education_section(lines, resume_data):
    if not resume_data.get('education'):
        return
    lines.append('\\section*{Education}')
    for school in resume_data['education']:
        degree = escape_latex(school.get('degree', ''))
        institution = escape_latex(school.get('institution', ''))
        date = escape_latex(school.get('date', '') or school.get('year', ''))
        field = escape_latex(school.get('field', ''))
        field_str = f', {field}' if field else ''
        lines.append(f'\\textbf{{{degree}{field_str}}}, {institution} \\hfill {date}')
        if school.get('thesis'):
            lines.append(f'\\\\\\textit{{\\small Thesis: {escape_latex(school["thesis"])}}}')
        lines.append('\\\\[2pt]')
    lines.append('')


def add_awards_section(lines, resume_data):
    if not resume_data.get('awards'):
        return
    lines.append('\\section*{Honours \\& Awards}')
    lines.append('\\begin{itemize}[nosep, leftmargin=0pt, label={}]')
    for award in resume_data['awards']:
        title = escape_latex(award.get('title', ''))
        org = escape_latex(award.get('organization', ''))
        year = escape_latex(str(award.get('year', '')))
        org_str = f', {org}' if org else ''
        year_str = f' \\hfill {year}' if year else ''
        lines.append(f'    \\item {title}{org_str}{year_str}')
    lines.append('\\end{itemize}')
    lines.append('')


def add_certifications_section(lines, resume_data):
    if not resume_data.get('certifications'):
        return
    lines.append('\\section*{Certifications}')
    lines.append('\\begin{itemize}[nosep, leftmargin=*]')
    for cert in resume_data['certifications']:
        title = escape_latex(cert.get('title', ''))
        issuer = escape_latex(cert.get('issuer', ''))
        date = escape_latex(cert.get('date', ''))
        issuer_str = f', {issuer}' if issuer else ''
        date_str = f' \\hfill {date}' if date else ''
        lines.append(f'    \\item {title}{issuer_str}{date_str}')
    lines.append('\\end{itemize}')
    lines.append('')


def add_projects_section(lines, resume_data):
    if not resume_data.get('projects'):
        return
    lines.append('\\section*{Projects}')
    for project in resume_data['projects']:
        title = escape_latex(project.get('title', ''))
        date = escape_latex(project.get('date', ''))
        description = escape_latex(project.get('description', ''))
        technologies = project.get('technologies', [])
        date_str = f' \\hfill {date}' if date else ''
        lines.append(f'\\textbf{{{title}}}{date_str}\\\\')
        if description:
            lines.append(f'{description}\\\\')
        if technologies:
            tech_str = ', '.join(escape_latex(t) for t in technologies)
            lines.append(f'\\texttt{{\\small {tech_str}}}\\\\')
        lines.append('')


def add_portfolio_section(lines, resume_data):
    if not resume_data.get('portfolio'):
        return
    lines.append('\\section*{Portfolio}')
    for item in resume_data['portfolio']:
        title = escape_latex(item.get('title', ''))
        url = item.get('url', '')
        icon = 'github' if 'github.com' in url else 'globe'
        lines.append(f'\\faIcon{{{icon}}}~\\href{{{escape_latex(url)}}}{{{title}}}\\\\')
    lines.append('')


def add_published_games_section(lines, resume_data):
    if not resume_data.get('published_games'):
        return
    lines.append('\\section*{Published Games}')
    lines.append('\\begin{itemize}[nosep, leftmargin=*]')
    for game in resume_data['published_games']:
        title = escape_latex(game.get('title', ''))
        platforms = game.get('platforms', [])
        year = game.get('year', '')
        platforms_str = ', '.join(escape_latex(p) for p in platforms) if isinstance(platforms, list) else escape_latex(platforms)
        year_str = escape_latex(year) if isinstance(year, str) else ', '.join(escape_latex(y) for y in year)
        lines.append(f'    \\item \\textbf{{{title}}} -- {platforms_str} ({year_str})')
    lines.append('\\end{itemize}')
    lines.append('')


def add_volunteer_section(lines, resume_data):
    if not resume_data.get('volunteer'):
        return
    lines.append('\\section*{Volunteer Experience}')
    for vol in resume_data['volunteer']:
        title = escape_latex(vol.get('title', ''))
        org = escape_latex(vol.get('organization', ''))
        date = escape_latex(vol.get('date', ''))
        lines.append(f'\\textbf{{{title}}}, {org} \\hfill {date}\\\\')
        lines.extend(description_lines(vol))
        lines.append('')


def add_publications_section(lines, resume_data):
    if not resume_data.get('publications'):
        return
    lines.append('\\section*{Publications}')
    lines.append('\\begin{itemize}[nosep, leftmargin=*]')
    for pub in resume_data['publications']:
        title = escape_latex(pub.get('title', ''))
        publication = escape_latex(pub.get('publication', ''))
        date = escape_latex(pub.get('date', ''))
        date_str = f' \\hfill {date}' if date else ''
        pub_str = f' ({publication})' if publication else ''
        lines.append(f'    \\item {title}{pub_str}{date_str}')
    lines.append('\\end{itemize}')
    lines.append('')


def add_languages_section(lines, resume_data):
    if not resume_data.get('languages'):
        return
    lines.append('\\section*{Languages}')
    lines.append('\\begin{itemize}[nosep, leftmargin=*]')
    for lang in resume_data['languages']:
        language = escape_latex(lang.get('language', ''))
        proficiency = escape_latex(lang.get('proficiency', ''))
        lines.append(f'    \\item \\textbf{{{language}}} -- {proficiency}')
    lines.append('\\end{itemize}')
    lines.append('')


def add_memberships_section(lines, resume_data):
    if not resume_data.get('memberships'):
        return
    lines.append('\\section*{Professional Memberships}')
    lines.append('\\begin{itemize}[nosep, leftmargin=*]')
    for m in resume_data['memberships']:
        org = escape_latex(m.get('organization', ''))
        title = escape_latex(m.get('title', ''))
        date = escape_latex(m.get('date', ''))
        title_str = f' ({title})' if title else ''
        date_str = f' \\hfill {date}' if date else ''
        lines.append(f'    \\item {org}{title_str}{date_str}')
    lines.append('\\end{itemize}')
    lines.append('')


# =====================================================================
# SECTION MAPPING
# =====================================================================

SECTION_BUILDERS = {
    'summary': add_summary_section,
    'ai_expertise': add_ai_expertise_section,
    'experience': add_experience_section,
    'skills': add_skills_section,
    'education': add_education_section,
    'certifications': add_certifications_section,
    'awards': add_awards_section,
    'projects': add_projects_section,
    'volunteer': add_volunteer_section,
    'publications': add_publications_section,
    'languages': add_languages_section,
    'memberships': add_memberships_section,
    'portfolio': add_portfolio_section,
    'published_games': add_published_games_section,
}


# =====================================================================
# MAIN
# =====================================================================

def main():
    if len(sys.argv) < 2:
        print('Usage: python json2tex.py input.json [output.tex]')
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = get_output_path(json_path, sys.argv[2] if len(sys.argv) > 2 else None, '.tex')

    resume_data = load_resume_json(json_path)
    lines = []

    add_document_setup(lines)
    lines.append('\\begin{document}')
    lines.append('\\pagestyle{empty}')
    lines.append('')
    add_header_section(lines, resume_data)
    build_sections(lines, resume_data, SECTION_BUILDERS)
    lines.append('\\end{document}')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f'Wrote LaTeX CV to: {output_path}')


if __name__ == '__main__':
    main()
