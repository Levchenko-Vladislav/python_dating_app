import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir) 
project_root = os.path.dirname(src_dir) 

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
    
if project_root not in sys.path:
    sys.path.insert(0, project_root)
