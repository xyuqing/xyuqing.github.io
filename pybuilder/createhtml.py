import os
import argparse
from collections import OrderedDict

# print(path, filename)
PATHATTRIBUTES = ['href', 'src', 'data', 'srcset', 'cite', 'action', 'formaction', 'poster', 'usemap']

def extract_quoted_strings(s):
    """Extract quoted strings and non-quoted parts from a string."""
    in_quote = False
    quote_char = ''
    current_quote = ''
    quotes = []
    not_quotes = []
    current_not_quote = ''
    for char in s:
        if char in ('"', "'"):
            if in_quote:
                if char == quote_char:
                    in_quote = False
                    quotes.append(current_quote)
                    current_quote = ''
                else:
                    current_quote += char
            else:
                in_quote = True
                quote_char = char
                not_quotes.append(current_not_quote)
                current_not_quote = ''
        elif in_quote:
            current_quote += char
        else:
            current_not_quote += char
    if current_not_quote:
        not_quotes.append(current_not_quote)
    return quotes, not_quotes

def create_attribute_dict(s):
    """Create a dictionary of attributes from a tag string."""
    tag, attributes = s.split(' ', 1)
    quotes, not_quotes = extract_quoted_strings(attributes)
    attr_dict = OrderedDict()
    for i in range(len(not_quotes)):
        parts = not_quotes[i].split('=')
        for j in range(len(parts)-1):
            key = parts[j].strip().split()[-1]
            value = quotes[i] if j==len(parts)-2 else parts[j+1].strip().split()[0]
            attr_dict[key] = value
    return tag, attr_dict

def process_file(path, insert_file, relpath):
    insert_path = os.path.join(path, insert_file)
    if not os.path.isfile(insert_path):
        print(f"Warning: Insert file {insert_path} does not exist.")
        return ""
    with open(insert_path, 'r') as f:
        contents = f.read()
    in_tag = False

    new_contents = ''
    for c in contents:
        if c == '>':
            in_tag = False
            if len(tag_contents.strip().split()) == 1:
                new_contents += tag_contents
            else:
                tag, attributes_dict = create_attribute_dict(tag_contents)
                for attr in PATHATTRIBUTES:
                    if attr in attributes_dict:
                        original_path = attributes_dict[attr]
                        if original_path.startswith('.') or original_path.startswith('..'):
                            new_path = os.path.join(relpath, original_path)
                            new_path = os.path.normpath(new_path)
                            attributes_dict[attr] = new_path
                # Reconstruct the tag
                new_tag = tag + ' '
                for key, value in attributes_dict.items():  
                    new_tag += f'{key}="{value}" '
                new_tag = new_tag.strip()
                new_contents += new_tag
        if in_tag:
            tag_contents += c
        else:
            new_contents += c
        if c == '<':
            in_tag = True
            tag_contents = ''
    return new_contents

def build_html(name):
    path = os.path.dirname(name)
    filename = os.path.basename(name)
    with open(name, 'r') as f:
        contents = ''
        lines = f.readlines()
        write_dir = path
        write_name = filename.replace('.page', '.html')
        for line in lines:
            if line.lstrip().startswith('!inserthtml'):
                contents += '\n\n\n'
                insert_file = line.split('=')[1].strip().strip('\"\'')
                relpath = os.path.relpath(path, write_dir)
                contents += process_file(path, insert_file, relpath) + '\n\n'
            elif line.lstrip().startswith('!location'):
                write_dir = line.split('=')[1].strip().strip('\"\'')
                write_dir = os.path.normpath(os.path.join(path, write_dir))
            elif line.lstrip().startswith('!name'):
                write_name = line.split('=')[1].strip().strip('\"\'')
            else:
                contents += line
        if not os.path.isdir(write_dir):
            os.makedirs(write_dir)
        write_path = os.path.join(write_dir, write_name)
        write_path = os.path.normpath(write_path)
        with open(write_path, 'w') as f:
            f.write(contents)

parser = argparse.ArgumentParser(description='Generate HTML file for a paper.')
parser.add_argument('name', help='.page file to be converted to HTML')

args = parser.parse_args()
name = args.name

build_html(name)