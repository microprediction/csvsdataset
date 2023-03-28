import os
from pathlib import Path
from pprint import pprint

TOP = os.path.dirname(os.path.abspath(__file__))
ROOT = Path(TOP).parent.absolute()
TESTDATA = os.path.join(TOP,'testdata')

if __name__=='__main__':
    print({'top':TOP,'root':ROOT})
