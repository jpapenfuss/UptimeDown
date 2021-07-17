import os

def caniread(path):
    if os.access(path, os.R_OK) is False:
        return False
    else:
        return True

def tobytes(value, multiplier):
    if multiplier in ["kB", "KB", "kilobyte", "kilobytes"]:
        return value * 1024
    if multiplier in ["mB", "MB", "megabyte", "megabytes"]:
        return value * 1024 * 1024
    if multiplier in ["gB", "GB", "gigabyte", "gigabytes"]:
        return value * 1024 * 1024 * 1024
    if multiplier in ["tB", "TB", "terabyte", "terabytes"]:
        return value * 1024 * 1024 * 1024 * 1024
    else:
        return 0
