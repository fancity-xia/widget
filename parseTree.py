import io
import os
import re
from collections import deque

Indentation = "\xa0\xa0 "
Folder_list = "│"
Folder_end = "└──"
Folder_sub = "├──"
LinuxTree = "\xa0\xa0"


class UnParseFormatError(Exception):
    pass


class TreeNodeUnFound(Exception):
    pass


def listDumpTree(listobj: list | tuple | set, prefix: str):
    """
    [
        {
            "Alignment": [
                {"iPSC15P15QC": [
                    "231107_M002_V350204528_L01_",
                    "231107_M002_V350204528_L02_",
                    "23117_M002_V350204528_L03_",
                    {"ASD" : ["ASD1", "ASD2", "ASD3"]}
                    ]
                },
                {"iPSC16P15QC":
                    ["iPSC17P15QC.chrfak03", "iPSC17P15QC.chrfak05", "iPSC17P15QC.chrfak04"]
                }
            ],
        },
        "report.pdf",
    ]
    ├── Alignment
    │   ├── iPSC15P15QC
    │   │   ├── 231107_M002_V350204528_L01_
    │   │   ├── 231107_M002_V350204528_L02_
    │   │   ├── 23117_M002_V350204528_L03_
    │   │   └── ASD
    │   │       ├── ASD1
    │   │       ├── ASD2
    │   │       └── ASD3
    │   └── iPSC16P15QC
    │       ├── iPSC17P15QC.chrfak03
    │       ├── iPSC17P15QC.chrfak05
    │       └── iPSC17P15QC.chrfak04
    └── report.pdf
    :return:
    """
    if not prefix:
        prefix = ""
    for obj in range(len(listobj)):
        if obj == len(listobj) - 1:
            print(f"{prefix}{Folder_end}", end="")
            tmp = f"{prefix}{Indentation}"
        else:
            print(f"{prefix}{Folder_sub}", end="")
            tmp = f"{prefix}{Folder_list}{Indentation}"
        if isinstance(listobj[obj], dict):  # one key => list
            element = list(listobj[obj].keys())[0]
            print(element)
            listDumpTree(listobj[obj][element], tmp)
        elif isinstance(listobj[obj], (int, float, str)):
            print(f" {listobj[obj]}")
        else:
            raise UnParseFormatError("无法解析成树的数据结构")


class TreeNode:
    """
    linknode
    """
    def __init__(self, nodename, nextnode=None):
        self.name = nodename
        if nextnode:
            self.add_node(TreeNode(nextnode))

    def next(self) -> list:
        if hasattr(self, "nextlist"):
            return getattr(self, "nextlist")
        else:
            return []

    def len(self):
        return len(self.next())

    def add_node(self, nodeobj) -> list:
        if self.haskey(nodeobj.name):
            return getattr(self, "nextlist")
        else:
            tmp = getattr(self, "nextlist")
            tmp.append(nodeobj)
            return tmp

    @staticmethod
    def global_search_node(nodeobj, nodename):
        queue = deque([nodeobj])
        while queue:
            pnode = queue.popleft()
            for node in pnode.next():  # 广度搜索 or 深度搜索
                if node.name == nodename:
                    return node
                else:
                    queue.append(node)
        return None

    def add_search_node(self, nodename, objlist):
        nodeobj = self.global_search_node(self, nodename)
        if not nodeobj:
            raise TreeNodeUnFound("cannot find treenode")
        for obj in objlist:
            nodeobj.add_node(obj)

    def haskey(self, nodename) -> bool:
        if hasattr(self, "nextlist"):
            nodelist = getattr(self, "nextlist")
            for node in nodelist:
                if getattr(node, "name") == nodename:
                    return True
            return False
        else:
            setattr(self, "nextlist", [])
            return False

    def getkey(self, nodename):
        if hasattr(self, "nextlist"):
            nodelist = getattr(self, "nextlist")
            for node in nodelist:
                if getattr(node, "name") == nodename:
                    return node
            return None
        else:
            return None


def dumpStructTree(treeobj: TreeNode, prefix: str):
    """
    [
        {
            "Alignment": [
                {"iPSC15P15QC": [
                    "231107_M002_V350204528_L01_",
                    "231107_M002_V350204528_L02_",
                    "23117_M002_V350204528_L03_",
                    {"ASD" : ["ASD1", "ASD2", "ASD3"]}
                    ]
                },
                {"iPSC16P15QC":
                    ["iPSC17P15QC.chrfak03", "iPSC17P15QC.chrfak05", "iPSC17P15QC.chrfak04"]
                }
            ],
        },
        "report.pdf",
    ]
    ├── Alignment
    │   ├── iPSC15P15QC
    │   │   ├── 231107_M002_V350204528_L01_
    │   │   ├── 231107_M002_V350204528_L02_
    │   │   ├── 23117_M002_V350204528_L03_
    │   │   └── ASD
    │   │       ├── ASD1
    │   │       ├── ASD2
    │   │       └── ASD3
    │   └── iPSC16P15QC
    │       ├── iPSC17P15QC.chrfak03
    │       ├── iPSC17P15QC.chrfak05
    │       └── iPSC17P15QC.chrfak04
    └── report.pdf
    :return:
    """
    if not prefix:
        prefix = ""
    listobj = treeobj.next()
    ind = 0
    for obj in listobj:
        if ind == treeobj.len() - 1:
            print(f"{prefix}{Folder_end}", end="")
            tmp = f"{prefix}{Indentation}"
        else:
            print(f"{prefix}{Folder_sub}", end="")
            tmp = f"{prefix}{Folder_list}{Indentation}"
        ind += 1
        if obj.len() >= 1:  # one key => list
            print(obj.name)
            dumpStructTree(obj, tmp)
        elif obj.len() == 0:
            print(f" {obj.name}")
        else:
            raise UnParseFormatError("无法解析成树的数据结构")


def toTree(info: list) -> TreeNode:
    t = TreeNode("root")
    queue = deque([(t, info)])
    while queue:
        treeobj, nodelist = queue.popleft()
        for node in nodelist:
            if isinstance(node, dict):
                kname = list(node.keys())[0]
                tmp = TreeNode(kname)
                treeobj.add_node(tmp)
                queue.append((tmp, node[kname]))
            else:
                treeobj.add_node(TreeNode(node))
    return t


def LoadStructTree(reader: io.BufferedReader | io.StringIO) -> TreeNode:
    """
    从文本句柄或者字符串io接口读取
    :param reader:
    :return:
    """
    res = TreeNode("root")
    indexlist = []
    while True:
        line = reader.readline()
        line = line.strip()
        # there is annotation( "#" ) at head of line
        if re.search("^#", line):
            continue
        if re.search(r"^\s*$", line):
            break
        elements = re.split(r'' + Indentation + r'|\s\s\s', line)
        mvalue = re.compile(r'[' + Folder_end + Folder_sub + r']+\s*(.*)')
        value = mvalue.findall(elements[-1])[0]
        # indexlist[len(elements)-1] = value
        if len(elements) <= len(indexlist):
            indexlist[len(elements) - 1] = value
            indexlist = indexlist[:len(elements)]
        else:
            indexlist.append(value)
        # save to res
        res = stringToTree(res, indexlist)
    return res


def stringToTree(res: TreeNode, indexlist: list) -> TreeNode:
    """
    Transfer string to list struction
    "Alignment-iPSC15P15QC-ASD-ASD1"
    "report.pdf"
    =>
    [
        {
            "Alignment": [
                {
                    "iPSC15P15QC": [
                        {
                            "ASD":[ASD1,]
                        }
                    ]
                }
            ]
        },
        "report.pdf"
    ]
    :return:
    """
    tmp = res
    for ind in range(len(indexlist)):
        tmp.add_node(TreeNode(indexlist[ind]))
        tmp = tmp.getkey(indexlist[ind])
    return res


def test():
    h = [{
        "Alignment": [
            {"iPSC15P15QC": [
                "231107_M002_V350204528_L01_",
                "231107_M002_V350204528_L02_",
                "23117_M002_V350204528_L03_",
                {"ASD": ["ASD1", "ASD2", "ASD3"]}
            ]
            },
            {"iPSC16P15QC": ["iPSC17P15QC.chrfak03", "iPSC17P15QC.chrfak05", "iPSC17P15QC.chrfak04"]}
        ],
    },
        "report.pdf", ]
    listDumpTree(h, "")
    tree = toTree(h)
    dumpStructTree(tree, "")
    if os.path.lexists("./tree.txt"):
        with open("./tree.txt") as tt:
            ff = LoadStructTree(tt)
            dumpStructTree(ff, "")


if __name__ == "__main__":
    test()
