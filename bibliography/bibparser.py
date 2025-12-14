from pybtex.database import parse_file
from pybtex.richtext import Text


LATEX_SYMBOLS = {
    r'\textregistered': '®',
    r'\textcopyright': '©',
    r'\texttrademark': '™',
    # Add more symbols as needed
}

def formatted_title(title):
    return "<em class=\"papertitle\">" + title + "</em>"

def formatted_authors(persons, max_authors=5, emphasize_name=None):
    # for person in persons:
    #     print(person.last_names)
    persons = [("<strong>" + " ".join(person.first_names+person.last_names) + "</strong>") if str(person) == emphasize_name else " ".join(person.first_names+person.last_names) for person in persons]
    if len(persons) > max_authors:
        persons = persons[:max_authors] + ["et al."]
    return "<span class=\"paperauthors\">" + ", ".join(str(person) for person in persons) + "</span>"

def formatted_venue(venue_text):
    return "<em>" + venue_text + "</em>"

def format_bib_data(bib_data, max_authors=5, emphasize_name=None):
    output = ""
    for key in bib_data.entries:
        entry = bib_data.entries[key]
        title = formatted_title(entry.fields.get("title", ""))
        url = entry.fields.get("url", "#")
        authors = formatted_authors(entry.persons.get("author", []), max_authors, emphasize_name)
        venue = formatted_venue(entry.fields.get("journal", entry.fields.get("booktitle", "")))
        venue = latex_to_unicode(venue)
        year = entry.fields.get("year", "")
        output += f"<div><a href=\"{url}\">{title}</a><br>{authors}<br>{venue}, {year}</div><br>\n"
    return output

def latex_to_unicode(s: str) -> str:
    """
    Convert LaTeX special symbols in a string to Unicode.
    """
    # First, handle braces around commands: {\textregistered} -> \textregistered
    s = s.replace('{\\', '\\').replace('}', '')

    # Replace known LaTeX symbols
    for latex_cmd, unicode_char in LATEX_SYMBOLS.items():
        s = s.replace(latex_cmd, unicode_char)

    # Use Pybtex Text to handle accents and simple macros
    text_obj = Text(s)
    return text_obj.render_as('text')

bib_data = parse_file("publications.bib")

contents = format_bib_data(bib_data, emphasize_name="Xie, YuQing")
with open("bibliography.html", "w", encoding="utf-8") as f:
    f.write(contents)