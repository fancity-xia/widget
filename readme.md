##  Documentation
#### parseTree.py 

This module implements the function of parsing and generating the txt result of linux tree. 

``` python

from parseTree import *

# load from linux tree
tt = open("./tree.txt")
ff = LoadStructTree(tt)  # Store tree files as linked list structured data
tt.close()

# dump linknode as linux tree structure
dumpStructTree(ff, "")

# trans dict to linknode
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

# print list as linux tree
listDumpTree(h, "")

├──Alignment
│   ├──iPSC15P15QC
│   │   ├── 231107_M002_V350204528_L01_
│   │   ├── 231107_M002_V350204528_L02_
│   │   ├── 23117_M002_V350204528_L03_
│   │   └──ASD
│   │      ├── ASD1
│   │      ├── ASD2
│   │      └── ASD3
│   └──iPSC16P15QC
│      ├── iPSC17P15QC.chrfak03
│      ├── iPSC17P15QC.chrfak05
│      └── iPSC17P15QC.chrfak04
└── report.pdf


tree = toTree(h)  # transfer list to linknode
dumpStructTree(tree, "")  # same with listDumptree
```
