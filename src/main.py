from textnode import TextNode, TextType
from funcs import clean_and_copy_dir, generate_pages_recursive
def main():
    src_dir = "static"
    dst_dir = "public"
    clean_and_copy_dir(src_dir, dst_dir)
    

    from_path = "content"
    template_path = "template.html"
    dest_path = "public"

    generate_pages_recursive(from_path, template_path, dest_path)





if __name__ == "__main__":
    main()