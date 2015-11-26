#!/usr/bin/env python

if __name__ == "__main__":
    import sys
    import os
    for dirpath, _, filenames in os.walk(sys.argv[1]):
        for fn in filenames:
            os.rename(os.path.join(dirpath, fn), os.path.join(dirpath, os.path.basename(dirpath)))

