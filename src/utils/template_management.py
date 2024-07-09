import re
from typing import List

from utils.log_management import log_error, log


def match_company_data_line_with_template(data_line: str, templates_json: dict) -> (bool, dict):
    """
    Determine if data_line has been inferred from one of the phrases in the template file.
    If true, list all the {keyword} and determine their value in data_line.

    Args:
        data_line (str): The data string to be matched.
        templates_json (dict): The json content of the template file.

    Returns:
        tuple: (bool, dict) where the bool indicates if a match was found,
               and the dict contains the {keyword} and their corresponding values in data_line.
    """
    log(f"Try matching  the company-data line with a template: {data_line}", "info")

    template_phrase_list    : list[str]         = get_template_phrase_list_from_json(templates_json)
    template_keywords_list  : list[str]         = get_template_keyword_list(template_phrase_list)
    template_keywords       : dict[str, str]    = {keyword: "" for keyword in template_keywords_list}

    for template in template_phrase_list:
        # Extract all {keywords} from the template
        found_keywords = set(re.findall(r'{(.*?)}', template))

        # Create a regex pattern from the template
        pattern = re.escape(template)
        for keyword in found_keywords:
            suffix = ""
            # Replace {keyword} with named capturing group
            while True:
                pattern0 = pattern.replace(r'\{' + keyword + r'\}', r'(?P<' + keyword+suffix + r'>.*?)', 1)
                if pattern0 == pattern:
                    pattern = pattern0
                    break
                pattern = pattern0
                suffix += "a"

        # Match the data_line with the regex pattern
        match = re.match(pattern, data_line)
        if match:
            # Extract the values of the {keywords}
            for keyword in found_keywords:
                template_keywords[keyword] = match.group(keyword)
            log(f"\t-> Successfully matched with {template}")
            return True, template_keywords

    log(f"\t-> No matching found")
    return False, template_keywords

def get_template_phrase_list_from_json(templates_json: dict) -> list[str]:
    """
    Get the list of template phrases (with keywords) in the input content of the template file.
    Args:
         templates_json (dict): content of the template file
    """
    try:
        return [t["template"] for t in templates_json.values()]
    except Exception as e:
        log_error(f"Failed to parse the template file: {e}", exception_to_raise=RuntimeError)

def get_template_keyword_list(template_phrase_list: List[str]) -> List[str]:
    """
    Extract unique keywords enclosed in curly braces from a list of template phrases.

    Args:
        template_phrase_list (List[str]): A list of template phrases containing keywords in the format {keyword}.

    Returns:
        List[str]: A list of unique keywords found in the template phrases.
    """
    keywords_set = set()

    for template in template_phrase_list:
        # Extract all {keywords} from the template
        keywords = re.findall(r'{(.*?)}', template)
        keywords_set.update(keywords)

    return list(keywords_set)