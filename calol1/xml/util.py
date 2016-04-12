from xml.dom import Node as _Node


def getId(node):
    attr = node.attributes.get('id')
    if not attr:
        raise Exception("Invalid XML detected! Node %s has no id" % node.tagName)
    return attr.value


def findOrCreateElement(document, parent, tag, id):
    all = parent.getElementsByTagName(tag)
    selected = filter(lambda el: getId(el) == id, all)
    if len(selected) == 0:
        new = document.createElement(tag)
        new.setAttribute('id', id)
        parent.appendChild(new)
        return new
    elif len(selected) == 1:
        return selected[0]
    else:
        raise Exception("Invalid XML detected! More than one element type %s with id %s" % (tag, id))


# The conclusion is this is not kosher
# http://stackoverflow.com/questions/3310614/remove-whitespaces-in-xml-string
def stripNode(node, recurse=True):
    nodesToRemove = []
    nodeToBeStripped = False

    for childNode in node.childNodes:
        # list empty text nodes (to remove if any should be)
        if (childNode.nodeType == _Node.TEXT_NODE and childNode.nodeValue.strip(' \t\n') == ""):
            nodesToRemove.append(childNode)

        # only remove empty text nodes if not a leaf node (i.e. a child element exists)
        if childNode.nodeType == _Node.ELEMENT_NODE:
            nodeToBeStripped = True

    # remove flagged text nodes
    if nodeToBeStripped:
        for childNode in nodesToRemove:
            node.removeChild(childNode)

    # recurse if specified
    if recurse:
        for childNode in node.childNodes:
            stripNode(childNode, True)
