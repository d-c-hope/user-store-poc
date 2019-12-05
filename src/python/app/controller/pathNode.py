
class TreeNode:
    def __init__(self, pathString):
        self.children = []
        self.isTerminal = False
        self.schema = None
        self.pathString = pathString
        self.postEndpoint = False
        self.putCreation = False
        self.defaultType = None # where you post to say /personas, which doc does it write to out of core, skykids etc
        self.isDefault = False

    def addChild(self, child):
        self.children.append(child)

    def isIdRoot(self):
        """
        This is true for a node like persona in persona/<id>, i.e. anything where the caller can put multiple
        objects below
        Note would only ever be a single child in this scenario
        """
        idFilteredChildren = list(filter(lambda x: x.pathString.startswith('<'), self.children))
        if len(idFilteredChildren) == 1 and len(self.children) == 1:
            return True
        else:
            return False


    def print(self):
        print("Node {}".format(self.pathString))

    def pathNested(self, pathSoFar=[]):
        """Returns in form[['', 'optouts'], ['', ['persona', ['<id>', 'skykids'], ['<id>', 'sports']]]]"""

        if len(self.children) == 0: return [self.pathString]
        def makePath(rootPath, item):
            path = [self.pathString] + item
            return path
        vals = []
        for child in self.children:
            childPath = child.pathNested(pathSoFar)
            processed = makePath(pathSoFar, childPath)
            vals.append(processed)

        return vals

    def path(self, pathSoFar=[], vals = []):
        """Returns in form [[''], ['', 'persona', '<id>'], ['', 'persona', '<id>']]"""
        p = pathSoFar + [self.pathString]
        if len(self.children) == 0:
            vals.append(pathSoFar)
        for child in self.children:
            child.path(p, vals)

        return

    def __str__(self):
        return self.pathString

    def __repr__(self):
        return self.pathString


class PathNode:
    """Once the tree node has been evaluated a listof PathNodes is returned"""
    def __init__(self, pathVal, isTerminal=False,
                 schema=None, pathString=None,
                 defaultType=None, postEndpoint=False,
                 putCreation=True,
                 isIdRoot=False, isDefault=False):
        """

        :param pathVal: the val of this node in the path, e.g. 22 in persona/22/kids
        :param isTerminal:
        :param schema:
        :param pathString: the path that was matched against (i.e. with <id> rather than vals), provided isTerminal is
        true
        :param defaultType:
        """
        self.pathVal = pathVal
        self.isTerminal = isTerminal
        self.schema = schema
        self.pathString = pathString
        self.defaultType = defaultType # where you post to say /personas, which doc does it write to out of core, skykids etc
        self.postEndpoint = postEndpoint
        self.putCreation = putCreation
        self.isIdRoot = isIdRoot
        self.isDefault = isDefault

    def isIdNode(self):
        return self.pathString.startswith('<')

    def __str__(self):
        return self.pathVal

    def __repr__(self):
        return self.pathVal



def pathNodeFromTree(treeNode, val):
    """Convert a node in the tree of nodes (built from the routes config)
    into a node that goes in the match list (i.e. by taking a path down the tree)
    An actual path has values in place of <id>"""

    return PathNode(val,
                    treeNode.isTerminal,
                    treeNode.schema,
                    treeNode.pathString,
                    treeNode.defaultType,
                    treeNode.postEndpoint,
                    treeNode.putCreation,
                    treeNode.isIdRoot(),
                    treeNode.isDefault)
