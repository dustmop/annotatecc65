# annotatecc

Annotatecc65.py and annotateld65.py are wrapper scripts that add source-level debugging to FCEUX when creating homebrew NES games using cc65.

When used in a build, annotatecc65.py associates C source files with meta-labels in the compiled assembly. During linking, annotateld65.py parses these meta-labels, and uses them along with debug information to generate nes.*.nl files. In the FCEUX debugger, comments containing the original source code will appear along side the assembly that it compiled down to.

# Usage

There are two choices:

1) Put annotatecc65.py and annotateld65.py into a folder that is in your PATH.

2) Or, put these scripts into the same directory as cc65.exe and ld65.exe

Then, in your build, change calls from cc65.exe to annotatecc65.py, and ld65.exe to annotateld65.py. Next, invoke your build normally.

Annotatecc65.py will create .annotate.\*.map and .annotate.\*.s files in the same directory as the compiled object files. These are safe to delete once the build is complete.

# Screenshot

![Source-level debugging in FCEUX](/screenshot/annotatecc.png?raw=true)

# Projects

The Wit.nes
Super Russian Roulette
