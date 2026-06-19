"""
Generate developer-style LaTeX CV from JSON source.
Uses the public Developer CV template from latextemplates.com.
Usage: python json2tex-developer.py input.json [output.tex]
"""
import json
import os
import sys


HEADER_RULE = '%' + '-' * 88

# =====================================================================
# UTILITY FUNCTIONS
# =====================================================================


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


def add_document_header(lines, resume_data):
    """Add document preamble and packages."""
    lines.append('%' * 100)
    lines.append(f'% Developer CV for {escape_latex(resume_data["name"])}')
    lines.append('% Template: https://www.latextemplates.com/template/developer-cv')
    lines.append('%' * 100)
    lines.append('')
    lines.append(HEADER_RULE)
    lines.append('%      PACKAGES AND DOCUMENT CONFIGURATION')
    lines.append(HEADER_RULE)
    lines.append('')
    lines.append('\\documentclass[9pt]{developercv}')
    lines.append('')
    lines.append(HEADER_RULE)
    lines.append('\\begin{document}')
    lines.append('\\raggedbottom')
    lines.append('')


def add_title_and_contact(lines, resume_data):
    """Add name, title, and contact information."""
    lines.append(HEADER_RULE)
    lines.append('% TITLE AND CONTACT INFORMATION')
    lines.append(HEADER_RULE)
    lines.append('')

    lines.append('\\begin{minipage}[t]{0.70\\textwidth}')

    # Split name into first and last for visual display.
    name_parts = resume_data["name"].split()
    first = escape_latex(name_parts[0]) if name_parts else ""
    last = escape_latex(name_parts[-1]) if len(name_parts) > 1 else ""

    lines.append(f'\\colorbox{{gray}}{{\\HUGE\\textcolor{{white}}{{\\textbf{{{first}}}}}}} \\\\')
    lines.append(f'\\colorbox{{gray}}{{\\HUGE\\textcolor{{white}}{{\\textbf{{{last}}}}}}}')
    lines.append('')
    lines.append(f'{{\\huge {escape_latex(resume_data["title"])}}}')
    lines.append('\\end{minipage}')

    # Contact info in right column.
    lines.append('\\begin{minipage}[t]{0.05\\textwidth}')
    contact = resume_data.get('contact', {})

    if "location" in contact:
        location_url = escape_latex(contact.get("location_url", ""))
        location = escape_latex(contact["location"])
        lines.append(f'\\icon{{MapMarker}}{{12}}{{\\href{{{location_url}}}{{{location}}}}}\\\\')

    if "phone" in contact:
        phone_clean = contact["phone"].replace(" ", "")
        phone = escape_latex(contact["phone"])
        lines.append(f'\\icon{{Phone}}{{12}}{{\\href{{tel:{escape_latex(phone_clean)}}}{{{phone}}}}}\\\\')

    if "email" in contact:
        email = escape_latex(contact["email"])
        lines.append(f'\\icon{{At}}{{12}}{{\\href{{mailto:{email}}}{{{email}}}}}\\\\')

    lines.append('\\end{minipage}')

    # Additional contact info in far right.
    lines.append('\\begin{minipage}[t]{0.25\\textwidth}')

    if "discord" in contact:
        discord = escape_latex(contact["discord"])
        lines.append(f'\\icon{{Discord}}{{12}}{{\\href{{https://discordapp.com/users/{discord}}}{{discord: {discord}}}}}\\\\')

    if "linkedin" in contact:
        linkedin_url = escape_latex(contact["linkedin"])
        name_escaped = escape_latex(resume_data["name"])
        lines.append(f'\\icon{{Globe}}{{12}}{{\\href{{{linkedin_url}}}{{linkedin: {name_escaped}}}}}\\\\')

    if "github" in contact:
        github_url = escape_latex(contact["github"])
        github_handle = escape_latex(contact["github"].split("/")[-1])
        lines.append(f'\\icon{{Github}}{{12}}{{\\href{{{github_url}}}{{github: {github_handle}}}}}\\\\')

    lines.append('\\end{minipage}')
    lines.append('')
    lines.append('\\vspace{0.5cm}')
    lines.append('')


def add_summary_section(lines, resume_data):
    """Add professional summary."""
    if not resume_data.get("summary"):
        return

    lines.append(HEADER_RULE)
    lines.append('% INTRODUCTION')
    lines.append(HEADER_RULE)
    lines.append('')
    lines.append('\\cvsect{Who Am I?}')
    lines.append(escape_latex(resume_data["summary"]))
    lines.append('')
    lines.append(HEADER_RULE)


def add_experience_section(lines, resume_data):
    """Add experience section."""
    if not resume_data.get("experience"):
        return

    lines.append('% EXPERIENCE')
    lines.append(HEADER_RULE)
    lines.append('')
    lines.append('\\cvsect{Experience}')
    lines.append('\\begin{entrylist}')

    for job in resume_data["experience"]:
        lines.append('\t\\entry')
        lines.append(f'\t\t{{{escape_latex(job["date"])}}}')
        lines.append(f'\t\t{{{escape_latex(job["title"])}}}')
        lines.append(f'\t\t{{{escape_latex(job["company"])}}}')

        desc = escape_latex(job["description"])
        techs = job.get("technologies", [])

        if techs:
            techs_str = '\\slashsep'.join([f'\\texttt{{{escape_latex(t)}}}' for t in techs])
            lines.append(f'\t\t{{{desc}\\\\ {techs_str}}}')
        else:
            lines.append(f'\t\t{{{desc}}}')

    lines.append('\\end{entrylist}')
    lines.append('')
    lines.append(HEADER_RULE)


def add_education_section(lines, resume_data):
    """Add education section."""
    if not resume_data.get("education"):
        return

    lines.append('% EDUCATION')
    lines.append(HEADER_RULE)
    lines.append('')
    lines.append('\\cvsect{education}')
    lines.append('\\begin{entrylist}')

    for school in resume_data["education"]:
        lines.append('\t\\entry')
        lines.append(f'\t\t{{{escape_latex(school.get("date", ""))}}}')
        lines.append(f'\t\t{{{escape_latex(school.get("degree", ""))}}}')
        lines.append(f'\t\t{{{escape_latex(school.get("institution", ""))}}}')

        field = school.get("field", "")
        thesis = school.get("thesis")

        # Format field and thesis info.
        if field and thesis:
            field_escaped = escape_latex(field)
            thesis_escaped = escape_latex(thesis)
            lines.append(f'\t\t{{{field_escaped}\\\\\\footnotesize{{{{\\sl Thesis:}} {thesis_escaped}}}}}')
        elif field:
            lines.append(f'\t\t{{{escape_latex(field)}}}')
        elif thesis:
            thesis_escaped = escape_latex(thesis)
            lines.append(f'\t\t{{\\footnotesize{{{{\\sl Thesis:}} {thesis_escaped}}}}}')
        else:
            lines.append('\t\t{}')

    lines.append('\\end{entrylist}')
    lines.append('')
    lines.append(HEADER_RULE)


def add_community_outreach_section(lines, resume_data):
    """Add community outreach section."""
    if not resume_data.get("community_outreach"):
        return

    lines.append('% COMMUNITY OUTREACH')
    lines.append(HEADER_RULE)
    lines.append('')
    lines.append('\\cvsect{Community Outreach}')

    for entry in resume_data["community_outreach"]:
        role = escape_latex(entry['role'])
        org = f", {escape_latex(entry['organization'])}" if entry.get('organization') else ""
        years = escape_latex(entry['years'])
        lines.append(f'$\\bullet$ {role}{org}, {years}\\\\')

    lines.append('')
    lines.append(HEADER_RULE)


def add_awards_section(lines, resume_data):
    """Add awards and honours section."""
    if not resume_data.get("awards"):
        return

    lines.append('% AWARDS')
    lines.append(HEADER_RULE)
    lines.append('')
    lines.append('\\cvsect{Awards}')

    for award in resume_data["awards"]:
        title = escape_latex(award['title'])
        org = escape_latex(award.get('organization', ''))
        year = escape_latex(award.get('year', ''))

        org_part = f", {org}" if org else ""
        year_part = f", {year}" if year else ""
        lines.append(f'$\\bullet$ {title}{org_part}{year_part}\\\\')

    lines.append('')


def add_portfolio_section(lines, resume_data):
    """Add portfolio section."""
    if not resume_data.get("portfolio"):
        return

    lines.append('% PORTFOLIO')
    lines.append(HEADER_RULE)
    lines.append('')
    lines.append('\\cvsect{Portfolio}')
    for item in resume_data["portfolio"]:
        title = escape_latex(item.get("title", ""))
        url = escape_latex(item["url"])
        lines.append(f'\\icon{{Github}}{{12}}{{\\href{{{url}}}{{github.com: {title}}}}}.')
    lines.append('')


def add_published_games_section(lines, resume_data):
    """Add published games section."""
    if not resume_data.get("published_games"):
        return

    lines.append('% PUBLISHED GAMES')
    lines.append(HEADER_RULE)
    lines.append('')
    lines.append('\\cvsect{Published Games}')

    for game in resume_data["published_games"]:
        title = escape_latex(game["title"])
        platforms = ', '.join([escape_latex(p) for p in game["platforms"]])
        year = game["year"] if isinstance(game["year"], str) else ', '.join([escape_latex(y) for y in game["year"]])
        lines.append(f'$\\bullet$ {title} - {platforms} ({year})\\\\')

    lines.append('')


def add_certifications_section(lines, resume_data):
    """Add certifications section."""
    if not resume_data.get("certifications"):
        return

    lines.append('% CERTIFICATIONS')
    lines.append(HEADER_RULE)
    lines.append('')
    lines.append('\\cvsect{Certifications}')

    for cert in resume_data["certifications"]:
        title = escape_latex(cert.get("title", ""))
        issuer = escape_latex(cert.get("issuer", ""))
        date = escape_latex(cert.get("date", ""))
        issuer_str = f" -- {issuer}" if issuer else ""
        date_str = f" ({date})" if date else ""
        lines.append(f'$\\bullet$ {title}{issuer_str}{date_str}\\\\')
        if cert.get("credential_id"):
            lines.append(f'\\hspace{{1em}} ID: {escape_latex(cert["credential_id"])}\\\\')

    lines.append('')


def add_skills_section(lines, resume_data):
    """Add technical skills section."""
    if not resume_data.get("skills"):
        return

    lines.append('% TECHNICAL SKILLS')
    lines.append(HEADER_RULE)
    lines.append('')
    lines.append('\\cvsect{Technical Skills}')

    skills = resume_data["skills"]
    for category, items in skills.items():
        if isinstance(items, list):
            items_str = ', '.join([escape_latex(item) for item in items])
        else:
            items_str = escape_latex(items)
        lines.append(f'\\textbf{{{escape_latex(category)}:}} {items_str}\\\\')

    lines.append('')


def add_languages_section(lines, resume_data):
    """Add languages section."""
    if not resume_data.get("languages"):
        return

    lines.append('% LANGUAGES')
    lines.append(HEADER_RULE)
    lines.append('')
    lines.append('\\cvsect{Languages}')

    for lang in resume_data["languages"]:
        language = escape_latex(lang.get("language", ""))
        proficiency = escape_latex(lang.get("proficiency", ""))
        lines.append(f'$\\bullet$ {language}: {proficiency}\\\\')

    lines.append('')


def add_projects_section(lines, resume_data):
    """Add projects section."""
    if not resume_data.get("projects"):
        return

    lines.append('% PROJECTS')
    lines.append(HEADER_RULE)
    lines.append('')
    lines.append('\\cvsect{Projects}')

    for project in resume_data["projects"]:
        title = escape_latex(project.get("title", ""))
        description = escape_latex(project.get("description", ""))
        technologies = project.get("technologies", [])
        date = escape_latex(project.get("date", ""))

        date_str = f" ({date})" if date else ""
        lines.append(f'\\textbf{{{title}}}{date_str}\\\\')
        lines.append(f'{description}\\\\')

        if technologies:
            tech_str = ', '.join([escape_latex(t) for t in technologies])
            lines.append(f'\\textcolor{{secondary}}{{\\textbf{{Technologies:}}}} {tech_str}\\\\')

        lines.append('')


def add_volunteer_section(lines, resume_data):
    """Add volunteer experience section."""
    if not resume_data.get("volunteer"):
        return

    lines.append('% VOLUNTEER EXPERIENCE')
    lines.append(HEADER_RULE)
    lines.append('')
    lines.append('\\cvsect{Volunteer Experience}')

    for vol in resume_data["volunteer"]:
        date = escape_latex(vol.get("date", ""))
        title = escape_latex(vol.get("title", ""))
        organization = escape_latex(vol.get("organization", ""))
        description = escape_latex(vol.get("description", ""))

        lines.append(f'\\textbf{{{title}}} \\hfill {date}\\\\')
        lines.append(f'\\textit{{{organization}}}\\\\')
        lines.append(f'{description}\\\\')
        lines.append('')


def add_publications_section(lines, resume_data):
    """Add publications section."""
    if not resume_data.get("publications"):
        return

    lines.append('% PUBLICATIONS')
    lines.append(HEADER_RULE)
    lines.append('')
    lines.append('\\cvsect{Publications}')

    for pub in resume_data["publications"]:
        title = escape_latex(pub.get("title", ""))
        publication = escape_latex(pub.get("publication", ""))
        date = escape_latex(pub.get("date", ""))

        date_str = f" ({date})" if date else ""
        lines.append(f'$\\bullet$ {title} -- {publication}{date_str}\\\\')

    lines.append('')


def add_memberships_section(lines, resume_data):
    """Add professional memberships section."""
    if not resume_data.get("memberships"):
        return

    lines.append('% PROFESSIONAL MEMBERSHIPS')
    lines.append(HEADER_RULE)
    lines.append('')
    lines.append('\\cvsect{Professional Memberships}')

    for membership in resume_data["memberships"]:
        organization = escape_latex(membership.get("organization", ""))
        title = escape_latex(membership.get("title", ""))
        date = escape_latex(membership.get("date", ""))

        date_str = f" ({date})" if date else ""
        lines.append(f'$\\bullet$ {organization} -- {title}{date_str}\\\\')

    lines.append('')


# =====================================================================
# MAIN ENTRY POINT
# =====================================================================


def main():
    if len(sys.argv) < 2:
        print("Usage: python json2tex-developer.py input.json [output.tex]")
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = get_output_path(json_path, sys.argv[2] if len(sys.argv) > 2 else None)

    resume_data = load_resume_json(json_path)
    lines = []

    # Build complete LaTeX document.
    add_document_header(lines, resume_data)
    add_title_and_contact(lines, resume_data)
    add_summary_section(lines, resume_data)
    add_experience_section(lines, resume_data)
    add_education_section(lines, resume_data)
    add_community_outreach_section(lines, resume_data)
    add_awards_section(lines, resume_data)
    add_portfolio_section(lines, resume_data)
    add_published_games_section(lines, resume_data)

    lines.append('\\end{document}')

    if os.path.exists(output_path):
        print(f"Overwriting existing file: {output_path}")

    with open(output_path, 'w', encoding='utf-8') as file_handle:
        file_handle.write('\n'.join(lines))

    print(f"Wrote LaTeX CV (developer style) to: {output_path}")


if __name__ == "__main__":
    main()
