import os
import sys

srcPath = f'{os.getcwd()}/src'
print(srcPath)
sys.path.insert(0, srcPath) # location of src