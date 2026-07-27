from textnode import TextNode, TextType
from funcs import clean_and_copy_dir, generate_pages_recursive
import sys

def main():
    src_dir = "static"
    dst_dir = "docs"
    clean_and_copy_dir(src_dir, dst_dir)
    

    from_path = "content"
    template_path = "template.html"
    dest_path = "docs"

    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    generate_pages_recursive(from_path, template_path, dest_path, basepath)

    



if __name__ == "__main__":
    main()