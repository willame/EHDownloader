#!/usr/bin/python3
import sys
from cx_Freeze import setup, Executable

copyDependentFiles = True
silent = True
base = None
packages = []
includes = []
excludes = []

if sys.platform == "win32":
    base = "Console"

setup(
    name = "EHDownloader",
    version = "2.0",
    options = {
        "build_exe": {
            "includes": includes,
            "excludes": excludes,
            "packages": packages
        }
    },
    executables = [
        Executable(
            "ehdownloader.py",
            base = base,
            icon = "../icon/eh_icon.ico"
        )
    ]
)
