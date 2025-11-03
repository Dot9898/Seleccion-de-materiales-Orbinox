
import sys
import os
from pathlib import Path
import streamlit.web.cli as stcli

ROOT_PATH = Path(__file__).resolve().parent
os.chdir(ROOT_PATH)

if __name__ == '__main__':
    sys.argv = ['streamlit', 'run', 'app/frontend.py']
    sys.exit(stcli.main())
