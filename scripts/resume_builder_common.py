"""
Shared utilities for all json2* resume generators.
"""
import json
import os


def get_output_path(json_path, output_arg, extension):
    """Determine output file path: use provided arg or derive from input."""
    if output_arg:
        return output_arg
    return os.path.splitext(json_path)[0] + extension


def load_resume_json(json_path):
    """Read and parse resume JSON file."""
    with open(json_path, encoding='utf-8-sig') as file_handle:
        return json.load(file_handle)


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


def build_sections(output, resume_data, section_builders):
    """Build sections in order specified by JSON, respecting filters."""
    section_order = resume_data.get('section_order', DEFAULT_SECTION_ORDER)
    section_filter = set(resume_data.get('section_filter', []))

    for section_name in section_order:
        if section_name not in section_filter and section_name in section_builders:
            section_builders[section_name](output, resume_data)
