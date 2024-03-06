#!/bin/python3

import subprocess
import os
import re
import base64

env = os.environ.copy()
env["Z3_PATH"] = "./bin/libz3.so"

def b64regex_generate_str(b64regex: str, timeout=10):
    try:
        p = subprocess.run(args=["node", "bin/Tests/cmd.js", b64regex], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        if p.returncode != 0:
            return "ERROR"
        return p.stdout.decode()
    except subprocess.TimeoutExpired as e:
        return "TIMEOUT"

def generate_str(regex: str, timeout=10):
    b64regex = base64.b64encode(regex.encode())
    return b64regex_generate_str(b64regex, timeout=timeout)

if __name__ == "__main__":
    import time
    x = generate_str("(?=a(?=bcd)b).+")
    print(x)