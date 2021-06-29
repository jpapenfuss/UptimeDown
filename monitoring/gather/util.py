import os

def caniread(path):
    if os.access(path, os.R_OK) is False:
        return False
    else:
        return True
