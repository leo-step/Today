import re

def extract_links(markdown_text):
    link_regex = r'\[([^\]]+)\]\((http[s]?://[^\)]+)\)'
    matches = re.findall(link_regex, markdown_text)
    return [match[1] for match in matches]
