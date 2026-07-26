import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):
    def test_props_multi(self):
        node = HTMLNode(
            props={
                "href": "https://google.com", 
                "target": "_blank",
            }
        )
        self.assertEqual(
            node.props_to_html(),
            ' href="https://google.com" target="_blank"'
        )

    def test_props_single(self):
        node = HTMLNode(props={"class": "primary-btn"})
        self.assertEqual(node.props_to_html(), ' class="primary-btn"')

    def test_props_empty(self):
        node = HTMLNode(props={})
        self.assertEqual(node.props_to_html(), "")

    def test_props_none(self):
        node = HTMLNode(props=None)
        self.assertEqual(node.props_to_html(), "")

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_no_tag(self):
        node = LeafNode(None, "This is raw structural text.")
        self.assertEqual(node.to_html(), "This is raw structural text.")

    def test_leaf_header(self):
        node = LeafNode("h1", "Main Title", {"class": "main-header"})
        self.assertEqual(node.to_html(), '<h1 class="main-header">Main Title</h1>')

    def test_leaf_link(self):
        node = LeafNode("a", "Click me!", {"href": "https://google.com", "target":"_blank"})
        self.assertEqual(
            node.to_html(),
            '<a href="https://google.com" target="_blank">Click me!</a>'
        )

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    
if __name__ == "__main__":
    unittest.main()