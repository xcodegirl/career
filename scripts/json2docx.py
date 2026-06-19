"""
Generate Word document resume from JSON source.
Usage: python json2docx.py input.json [output.docx]
"""
import json
import os
import sys

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
except ImportError:
    print("Error: python-docx is required. Install with: pip install python-docx")
    sys.exit(1)


def get_output_path(json_path, output_arg):
    """Determine output file path: use provided arg or derive from input."""
    if output_arg:
        return output_arg
    return os.path.splitext(json_path)[0] + '.docx'


def load_resume_json(json_path):
    """Read and parse resume JSON file."""
    with open(json_path, encoding='utf-8') as file_handle:
        return json.load(file_handle)


def build_resume_document(resume_data):
    """Construct Word document from resume data."""
    doc = Document()

    # =====================================================================
    # TITLE AND CONTACT INFO
    # =====================================================================
    title = doc.add_paragraph()
    title_run = title.add_run(resume_data["name"])
    title_run.font.size = Pt(28)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(42, 77, 122)
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    subtitle = doc.add_paragraph(resume_data.get("title", ""))
    subtitle.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    if subtitle.runs:
        subtitle_run = subtitle.runs[0]
        subtitle_run.font.size = Pt(14)
        subtitle_run.font.color.rgb = RGBColor(100, 100, 100)

    # Contact info formatting
    contact = resume_data.get("contact", {})
    if contact:
        contact_para = doc.add_paragraph()
        contact_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        contact_items = []
        if "linkedin" in contact:
            contact_items.append(contact["linkedin"].split("/")[-1])
        if "github" in contact:
            contact_items.append(contact["github"].split("/")[-1])
        contact_para.add_run(" | ".join(contact_items))
        contact_para.paragraph_format.space_before = Pt(6)
        contact_para.paragraph_format.space_after = Pt(12)

    # =====================================================================
    # SUMMARY SECTION
    # =====================================================================
    if resume_data.get("summary"):
        doc.add_heading("Who Am I?", level=2)
        doc.add_paragraph(resume_data["summary"])

    # Experience section
    if resume_data.get("experience"):
        doc.add_heading("Experience", level=2)
        for job in resume_data["experience"]:
            job_para = doc.add_paragraph(style='List Bullet')
            title_run = job_para.add_run(f"{job.get('title', '')} - {job.get('company', '')}")
            title_run.bold = True
            title_run.font.size = Pt(11)

            date_para = doc.add_paragraph(job.get("date", ""), style='List Bullet 2')
            date_para.paragraph_format.left_indent = Inches(0.5)
            if date_para.runs:
                date_run = date_para.runs[0]
                date_run.font.italic = True
                date_run.font.size = Pt(10)
                date_run.font.color.rgb = RGBColor(100, 100, 100)

            desc_para = doc.add_paragraph(job.get("description", ""), style='List Bullet 2')
            desc_para.paragraph_format.left_indent = Inches(0.5)

            if job.get("technologies"):
                tech_para = doc.add_paragraph(style='List Bullet 2')
                tech_para.paragraph_format.left_indent = Inches(0.5)
                tech_run = tech_para.add_run("Technologies: ")
                tech_run.bold = True
                tech_para.add_run(", ".join(job["technologies"]))

    # =====================================================================
    # EDUCATION SECTION
    # =====================================================================
    if resume_data.get("education"):
        doc.add_heading("Education", level=2)
        for school in resume_data["education"]:
            edu_para = doc.add_paragraph(style='List Bullet')
            degree_run = edu_para.add_run(f"{school.get('degree', '')}")
            degree_run.bold = True
            degree_run.font.size = Pt(11)
            edu_para.add_run(f" in {school.get('field', '')}")

            inst_para = doc.add_paragraph(style='List Bullet 2')
            inst_para.paragraph_format.left_indent = Inches(0.5)
            inst_run = inst_para.add_run(school.get('institution', ''))
            inst_run.italic = True

            date_para = doc.add_paragraph(school.get('date', ''), style='List Bullet 2')
            date_para.paragraph_format.left_indent = Inches(0.5)
            if date_para.runs:
                date_run = date_para.runs[0]
                date_run.font.color.rgb = RGBColor(100, 100, 100)

    # =====================================================================
    # AWARDS SECTION
    # =====================================================================
    if resume_data.get("awards"):
        doc.add_heading("Awards & Honours", level=2)
        for award in resume_data["awards"]:
            award_para = doc.add_paragraph(style='List Bullet')
            award_run = award_para.add_run(award.get('title', ''))
            award_run.bold = True
            award_para.add_run(f" - {award.get('organization', '')} ({award.get('year', '')})")

    # =====================================================================
    # LANGUAGES SECTION
    # =====================================================================
    if resume_data.get("languages"):
        doc.add_heading("Languages", level=2)
        for lang in resume_data["languages"]:
            lang_para = doc.add_paragraph(style='List Bullet')
            lang_para.add_run(f"{lang.get('language', '')}: {lang.get('proficiency', '')}")

    # =====================================================================
    # PORTFOLIO SECTION
    # =====================================================================
    if resume_data.get("portfolio"):
        doc.add_heading("Portfolio", level=2)
        for item in resume_data["portfolio"]:
            port_para = doc.add_paragraph(style='List Bullet')
            link_run = port_para.add_run(item.get('title', ''))
            link_run.font.color.rgb = RGBColor(61, 90, 241)
            link_run.underline = True
            port_para.add_run(f" - {item.get('url', '')}")

    # =====================================================================
    # PUBLISHED GAMES SECTION
    # =====================================================================
    if resume_data.get("published_games"):
        doc.add_heading("Published Games", level=2)
        for game in resume_data["published_games"]:
            platforms = ', '.join(game["platforms"]) if isinstance(game["platforms"], list) else game["platforms"]
            year = game["year"] if isinstance(game["year"], str) else ', '.join(game["year"])
            game_para = doc.add_paragraph(style='List Bullet')
            game_run = game_para.add_run(game.get('title', ''))
            game_run.bold = True
            game_para.add_run(f" ({platforms}, {year})")

    # =====================================================================
    # CERTIFICATIONS SECTION
    # =====================================================================
    if resume_data.get("certifications"):
        doc.add_heading("Certifications", level=2)
        for cert in resume_data["certifications"]:
            cert_para = doc.add_paragraph(style='List Bullet')
            cert_run = cert_para.add_run(cert.get('title', ''))
            cert_run.bold = True
            if cert.get('issuer'):
                cert_para.add_run(f" - {cert.get('issuer', '')}")
            if cert.get('date'):
                cert_para.add_run(f" ({cert.get('date', '')})")
            if cert.get('credential_id'):
                cred_para = doc.add_paragraph(f"ID: {cert.get('credential_id', '')}", style='List Bullet 2')
                cred_para.paragraph_format.left_indent = Inches(0.5)

    # =====================================================================
    # PROJECTS SECTION
    # =====================================================================
    if resume_data.get("projects"):
        doc.add_heading("Projects", level=2)
        for project in resume_data["projects"]:
            proj_para = doc.add_paragraph(style='List Bullet')
            proj_run = proj_para.add_run(project.get('title', ''))
            proj_run.bold = True
            if project.get('date'):
                proj_para.add_run(f" ({project.get('date', '')})")

            desc_para = doc.add_paragraph(project.get('description', ''), style='List Bullet 2')
            desc_para.paragraph_format.left_indent = Inches(0.5)

            if project.get('technologies'):
                tech_str = ', '.join(project['technologies'])
                tech_para = doc.add_paragraph(f"Technologies: {tech_str}", style='List Bullet 2')
                tech_para.paragraph_format.left_indent = Inches(0.5)

    # =====================================================================
    # VOLUNTEER EXPERIENCE SECTION
    # =====================================================================
    if resume_data.get("volunteer"):
        doc.add_heading("Volunteer Experience", level=2)
        for vol in resume_data["volunteer"]:
            vol_para = doc.add_paragraph(style='List Bullet')
            vol_run = vol_para.add_run(vol.get('title', ''))
            vol_run.bold = True
            vol_para.add_run(f" - {vol.get('organization', '')}")

            date_para = doc.add_paragraph(vol.get('date', ''), style='List Bullet 2')
            date_para.paragraph_format.left_indent = Inches(0.5)

            desc_para = doc.add_paragraph(vol.get('description', ''), style='List Bullet 2')
            desc_para.paragraph_format.left_indent = Inches(0.5)

    # =====================================================================
    # PUBLICATIONS SECTION
    # =====================================================================
    if resume_data.get("publications"):
        doc.add_heading("Publications", level=2)
        for pub in resume_data["publications"]:
            pub_para = doc.add_paragraph(style='List Bullet')
            pub_run = pub_para.add_run(pub.get('title', ''))
            pub_run.bold = True
            if pub.get('publication'):
                pub_para.add_run(f" - {pub.get('publication', '')}")
            if pub.get('date'):
                pub_para.add_run(f" ({pub.get('date', '')})")

    # =====================================================================
    # MEMBERSHIPS SECTION
    # =====================================================================
    if resume_data.get("memberships"):
        doc.add_heading("Professional Memberships", level=2)
        for membership in resume_data["memberships"]:
            mem_para = doc.add_paragraph(style='List Bullet')
            mem_run = mem_para.add_run(membership.get('organization', ''))
            mem_run.bold = True
            if membership.get('title'):
                mem_para.add_run(f" - {membership.get('title', '')}")
            if membership.get('date'):
                mem_para.add_run(f" ({membership.get('date', '')})")

    # =====================================================================
    # SKILLS SECTION
    # =====================================================================
    if resume_data.get("skills"):
        doc.add_heading("Skills", level=2)
        skills = resume_data["skills"]
        if isinstance(skills, dict):
            for category, items in skills.items():
                cat_para = doc.add_paragraph(style='List Bullet')
                cat_run = cat_para.add_run(f"{category}:")
                cat_run.bold = True
                if isinstance(items, list):
                    items_str = ', '.join(items)
                else:
                    items_str = str(items)
                cat_para.add_run(f" {items_str}")

    return doc


def main():
    if len(sys.argv) < 2:
        print("Usage: python json2docx.py input.json [output.docx]")
        sys.exit(1)

    json_path = sys.argv[1]
    output_path = get_output_path(json_path, sys.argv[2] if len(sys.argv) > 2 else None)

    resume_data = load_resume_json(json_path)
    doc = build_resume_document(resume_data)

    if os.path.exists(output_path):
        print(f"Overwriting existing file: {output_path}")

    doc.save(output_path)
    print(f"Wrote Word document to: {output_path}")


if __name__ == "__main__":
    main()
