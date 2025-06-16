import json
import sys

def tex_escape(text):
    """Escape LaTeX special characters and normalize quotes/dashes."""
    if not isinstance(text, str):
        return text
    # Replace curly quotes/apostrophes with straight ones
    text = text.replace('’', "'").replace('‘', "'")
    text = text.replace('“', '``').replace('”', "''")
    # Replace en-dash and em-dash with LaTeX equivalents
    text = text.replace('–', '--').replace('—', '---')
    # Escape LaTeX special characters
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

def main():
    # Usage: python json2tex.py input.json [output.tex]
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        print("Usage: python json2tex.py input.json [output.tex]")
        sys.exit(1)
    if len(sys.argv) > 2:
        tex_file = sys.argv[2]
    else:
        tex_file = json_file.replace('.json', '-cv-fromjson.tex')

    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)

    lines = []
    lines.append('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    lines.append(f'% Developer CV for {tex_escape(data["name"])}')
    lines.append('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    lines.append('')
    lines.append('\\documentclass[9pt]{developercv}')
    lines.append('\\begin{document}')
    lines.append('')
    # Title and Contact
    lines.append('% TITLE AND CONTACT INFORMATION')
    lines.append('\\begin{minipage}[t]{0.45\\textwidth}')
    name_parts = data["name"].split()
    first = tex_escape(name_parts[0]) if name_parts else ""
    last = tex_escape(name_parts[-1]) if len(name_parts) > 1 else ""
    lines.append(f'\\colorbox{{gray}}{{\\HUGE\\textcolor{{white}}{{\\textbf{{{first}}}}}}} \\\\')
    lines.append(f'\\colorbox{{gray}}{{\\HUGE\\textcolor{{white}}{{\\textbf{{{last}}}}}}}')
    lines.append('')
    lines.append(f'{{\\huge {tex_escape(data["title"])}}}')
    lines.append('\\end{minipage}')
    lines.append('\\begin{minipage}[t]{0.275\\textwidth}')
    contact = data.get('contact', {})
    if "location" in contact:
        lines.append(f'\\icon{{MapMarker}}{{12}}{{\\href{{{tex_escape(contact.get("location_url",""))}}}{{{tex_escape(contact["location"])}}}}}\\\\')
    if "phone" in contact:
        lines.append(f'\\icon{{Phone}}{{12}}{{\\href{{tel:{tex_escape(contact["phone"].replace(" ", ""))}}}{{{tex_escape(contact["phone"])}}}}}\\\\')
    if "email" in contact:
        lines.append(f'\\icon{{At}}{{12}}{{\\href{{mailto:{tex_escape(contact["email"])}}}{{{tex_escape(contact["email"])}}}}}\\\\')
    lines.append('\\end{minipage}')
    lines.append('\\begin{minipage}[t]{0.275\\textwidth}')
    if "discord" in contact:
        lines.append(f'\\icon{{Discord}}{{12}}{{\\href{{https://discordapp.com/users/{tex_escape(contact["discord"])}}}{{discord: {tex_escape(contact["discord"])}}}}}\\\\')
    if "linkedin" in contact:
        lines.append(f'\\icon{{Globe}}{{12}}{{\\href{{{tex_escape(contact["linkedin"])}}}{{linkedin: {tex_escape(data["name"])}}}}}\\\\')
    if "github" in contact:
        lines.append(f'\\icon{{Github}}{{12}}{{\\href{{{tex_escape(contact["github"])}}}{{github: {tex_escape(contact["github"].split("/")[-1])}}}}}\\\\')
    lines.append('\\end{minipage}')
    lines.append('')
    # Introduction
    lines.append('% INTRODUCTION')
    lines.append('\\cvsect{Who Am I?}')
    lines.append(tex_escape(data["summary"]))
    lines.append('')
    # Experience
    if data.get("experience"):
        lines.append('% EXPERIENCE')
        lines.append('\\cvsect{Experience}')
        lines.append('\\begin{entrylist}')
        for exp in data["experience"]:
            lines.append('\t\\entry')
            lines.append(f'\t\t{{{tex_escape(exp["date"])}}}')
            lines.append(f'\t\t{{{tex_escape(exp["title"])}}}')
            lines.append(f'\t\t{{{tex_escape(exp["company"])}}}')
            desc = tex_escape(exp["description"])
            techs = exp.get("technologies", [])
            if techs:
                techs_str = '\\slashsep'.join([f'\\texttt{{{tex_escape(t)}}}' for t in techs])
                lines.append(f'\t\t{{{desc}\\\\ {techs_str}}}')
            else:
                lines.append(f'\t\t{{{desc}}}')
        lines.append('\\end{entrylist}')
        lines.append('')
    # Education
    if data.get("education"):
        lines.append('% EDUCATION')
        lines.append('\\cvsect{education}')
        lines.append('\\begin{entrylist}')
        for edu in data["education"]:
            lines.append('\t\\entry')
            lines.append(f'\t\t{{{tex_escape(edu.get("date", ""))}}}')
            lines.append(f'\t\t{{{tex_escape(edu.get("degree", ""))}}}')
            lines.append(f'\t\t{{{tex_escape(edu.get("institution", ""))}}}')
            field = edu.get("field", "")
            thesis = edu.get("thesis")
            if field and thesis:
                lines.append(f'\t\t{{{tex_escape(field)}\\\\\\footnotesize{{{{\\sl Thesis Title:}} {tex_escape(thesis)}}}}}')
            elif field:
                lines.append(f'\t\t{{{tex_escape(field)}}}')
            elif thesis:
                lines.append(f'\t\t{{\\footnotesize{{{{\\sl Thesis Title:}} {tex_escape(thesis)}}}}}')
            else:
                lines.append('\t\t{}')
        lines.append('\\end{entrylist}')
        lines.append('')
    # Community Outreach
    if data.get("community_outreach"):
        lines.append('% COMMUNITY OUTREACH')
        lines.append('\\cvsect{Community Outreach}')
        for c in data["community_outreach"]:
            org = f", {tex_escape(c['organization'])}" if c.get("organization") else ""
            lines.append(f'$\\bullet$ {tex_escape(c["role"])}{org}, {tex_escape(c["years"])}\\\\')
        lines.append('')
    # Awards
    if data.get("awards"):
        lines.append('\\cvsect{Awards}')
        for a in data["awards"]:
            org = tex_escape(a.get("organization", ""))
            year = tex_escape(a.get("year", ""))
            lines.append(f'$\\bullet$ {tex_escape(a["title"])}{", " + org if org else ""}{", " + year if year else ""}\\\\')
        lines.append('')
    # Languages and Work Samples
    has_languages = bool(data.get("languages"))
    has_work_samples = bool(data.get("work_samples"))
    if has_languages or has_work_samples:
        lines.append('\\begin{minipage}[t]{0.5\\textwidth}')
        if has_languages:
            lines.append('\\cvsect{Languages}')
            for l in data["languages"]:
                lines.append(f'\\textbf{{{tex_escape(l["language"])}}} - {tex_escape(l["proficiency"])}\\\\')
        if has_work_samples:
            lines.append('\\cvsect{Work Samples}')
            for ws in data["work_samples"]:
                repo = ws["url"].replace("https://github.com/", "")
                lines.append(f'\\icon{{Github}}{{12}}{{\\href{{{tex_escape(ws["url"])}}}{{github.com: {tex_escape(repo)}}}}}.')
        lines.append('\\end{minipage}')
        lines.append('\\hfill')
    # Published Games
    if data.get("published_games"):
        lines.append('\\begin{minipage}[t]{0.5\\textwidth}')
        lines.append('\\cvsect{Published Games}')
        for g in data["published_games"]:
            platforms = ', '.join([tex_escape(p) for p in g["platforms"]])
            year = g["year"] if isinstance(g["year"], str) else ', '.join([tex_escape(y) for y in g["year"]])
            lines.append(f'$\\bullet$ {tex_escape(g["title"])} - {platforms} ({year})\\\\')
        lines.append('\\end{minipage}')
        lines.append('')
    lines.append('\\end{document}')

    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

if __name__ == "__main__":
    main()