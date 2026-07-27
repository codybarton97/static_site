from textnode import *
import re
from enum import Enum
from htmlnode import HTMLNode, ParentNode
import os
import shutil

def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        origin_text = node.text
        if delimiter not in origin_text:
            new_nodes.append(node)
            continue

        parts = origin_text.split(delimiter)

        if len(parts) % 2 == 0:
            raise ValueError(f"Invalid Markdown syntax: missing closing delimiter '{delimiter}' in text: '{origin_text}'")

        for i in range(len(parts)):
            if parts[i] == "":
                continue

            if i % 2 == 0:
                new_nodes.append(TextNode(parts[i], TextType.TEXT))

            else:
                new_nodes.append(TextNode(parts[i], text_type))

    return new_nodes

def text_to_children(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    html_children = []
    for text_node in nodes:
        html_node = text_node_to_html_node(text_node)
        html_children.append(html_node)

    return html_children
###########################################################################################################################

def extract_markdown_images(text):
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)

def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)
###########################################################################################################################

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        current_text = node.text
        images = extract_markdown_images(current_text)
        if not images:
            new_nodes.append(node)
            continue

        alt_text, url = images[0]
        target = f"![{alt_text}]({url})"
        sections = current_text.split(target, 1)
        if sections[0] != "":
            new_nodes.append(TextNode(sections[0], TextType.TEXT))

        new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))

        remaining = TextNode(sections[1], TextType.TEXT)
        new_nodes.extend(split_nodes_image([remaining]))

    return new_nodes


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        current_text = node.text
        links = extract_markdown_links(current_text)
        if not links:
            new_nodes.append(node)
            continue
        
        anchor_text, url = links[0]
        target = f"[{anchor_text}]({url})"
        sections = current_text.split(target, 1)
        if sections[0] != "":
            new_nodes.append(TextNode(sections[0], TextType.TEXT))

        new_nodes.append(TextNode(anchor_text, TextType.LINK, url))

        remaining = TextNode(sections[1], TextType.TEXT)
        new_nodes.extend(split_nodes_link([remaining]))

    return new_nodes
##########################################################################################################################

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    return nodes
##########################################################################################################################

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    new_blocks = [block.strip() for block in blocks if block.strip()]
    return new_blocks

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(block):
    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return "heading"
    if block.startswith("```") and block.endswith("```"):
        return "code"

    lines = block.split("\n")
    if all(line.startswith(">") for line in lines):
        return "quote"

    if all(line.startswith("- ") for line in lines):
        return "unordered_list"
    
    is_ordered_list = True
    for index, line in enumerate(lines, start=1):
        prefix = f"{index}. "
        if not line.startswith(prefix):
            is_ordered_list = False
            break

    if is_ordered_list:
        return "ordered_list"

    return "paragraph"
#########################################################################################################################

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    child_nodes = []

    for block in blocks:
        block_type = block_to_block_type(block)

        if block_type == "heading":
            node = create_heading_node(block)
        elif block_type == "code":
            node = create_code_node(block)
        elif block_type == "quote":
            node = create_quote_node(block)
        elif block_type == "unordered_list":
            node = create_unordered_list_node(block)
        elif block_type == "ordered_list":
            node = create_ordered_list_node(block)
        else:
            node = create_paragraph_node(block)
            
        child_nodes.append(node)
    return ParentNode(tags="div", children=child_nodes)


###_HELPER_FUNCS_#########################################################################################################

def create_heading_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    text = block[level + 1:]
    return ParentNode(tags=f"h{level}", children=text_to_children(text))

def create_code_node(block):
    code_text = block[3:-3].strip("\n") + "\n"
    raw_text = TextNode(code_text, TextType.TEXT)
    html_text = text_node_to_html_node(raw_text)
    code_node = ParentNode(tags="code", children=[html_text])
    return ParentNode(tags="pre", children=[code_node])

def create_quote_node(block):
    lines = block.split("\n")
    clean_lines = []
    for line in lines:
        content = line[1:]
        if content.startswith(" "):
            content = content[1:]
        clean_lines.append(content)

    full_text = " ".join(clean_lines)
    return ParentNode(tags="blockquote", children=text_to_children(full_text))

def create_unordered_list_node(block):
    lines = block.split("\n")
    nodes = []
    for line in lines:
        item_text = line[2:]
        nodes.append(ParentNode(tags="li", children=text_to_children(item_text)))
    return ParentNode(tags="ul",  children=nodes)

def create_ordered_list_node(block):
    lines = block.split("\n")
    nodes = []
    for line in lines:
        end = line.find(". ") + 2
        item_text = line[end:]
        nodes.append(ParentNode(tags="li", children=text_to_children(item_text)))
    return ParentNode(tags="ol", children=nodes)

def create_paragraph_node(block):
    return ParentNode(tags="p", children=text_to_children(block))
##############################################################################################################################

def clean_and_copy_dir(static, public):
    if os.path.exists(public):
        print(f"Cleaning destination directory: {public}")
        shutil.rmtree(public)

    os.mkdir(public)

    def copy_recursive(src, dst):
        for item in os.listdir(src):
            src_path = os.path.join(src, item)
            dst_path = os.path.join(dst, item)

            if os.path.isfile(src_path):
                shutil.copy(src_path, dst_path)
                print(f"Copied file: {src_path} -> {dst_path}")
            else:
                os.mkdir(dst_path)
                print(f"Created directory: {dst_path}")
                copy_recursive(src_path, dst_path)

    print(f"Starting copy from {static} to {public}...")
    copy_recursive(static, public)
    print("Copy completed successfully.")
###################################################################################################################################

def extract_title(markdown):
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
        elif line == "#":
            return ""
    raise ValueErorr("No H1 header found in the markdown.")

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    title = extract_title(markdown_content)
    full_html = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)
    full_html = full_html.replace('href="/', f'href="{basepath}')
    full_html = full_html.replace('src="/', f'src="{basepath}')

    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(full_html)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    for entry in os.listdir(dir_path_content):
        src_path = os.path.join(dir_path_content, entry)
        if os.path.isdir(src_path):
            new_dest_dir = os.path.join(dest_dir_path, entry)
            generate_pages_recursive(src_path, template_path, new_dest_dir, basepath)

        elif os.path.isfile(src_path) and entry.endswith(".md"):
            filename = entry[:-3] + ".html"
            dest_file_path = os.path.join(dest_dir_path, filename)
            generate_page(src_path, template_path, dest_file_path, basepath)
