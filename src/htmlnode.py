class HTMLNode():
    def __init__(self, tags=None, value=None, children=None, props=None):
        self.tags = tags
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError()

    def props_to_html(self):
        if not self.props:
            return ""

        attr = ""
        for key, value in self.props.items():
            attr += f' {key}="{value}"'

        return attr

    def __repr__(self):
        return f"HTMLNode({self.tags}, {self.value}, {self.children}, {self.props})"

class LeafNode(HTMLNode):
    def __init__(self, tags, value, props=None):
        if value is None:
            raise ValueError("All leaf nodes must have a value")
        super().__init__(tags=tags, value=value, children=None, props=props)
    
    def to_html(self):
        if self.value is None:
            raise ValueError("All leaf nodes must have a value")
        if self.tags is None:
            return self.value
        return f"<{self.tags}{self.props_to_html()}>{self.value}</{self.tags}>"

    def __repr__(self):
        return f"LeafNode({self.tags}, {self.value}, {self.props})"

class ParentNode(HTMLNode):
    def __init__(self, tags, children, props=None):
        super().__init__(tags=tags, value=None, children=children, props=props)

    def to_html(self):
        if self.tags is None:
            raise ValueError("All parent nodes must have a tag")
        if self.children is None:
            raise ValueError("All parent nodes must have children")
        
        html_children = ""
        for child in self.children:
            html_children += child.to_html()

        return f"<{self.tags}{self.props_to_html()}>{html_children}</{self.tags}>"