import subprocess
import os
import re
import sys
import base64
import json
from gen import generate_str

env = os.environ.copy()
env["Z3_PATH"] = "./bin/libz3.so"

def read_regexes(path):
    f = open(path, "r", encoding="utf-8", newline=None)
    regexes = [line.replace("\n", "") for line in f.readlines()]
    return regexes

def single_dataset(dataset_path, out_path, start=0):
    fail_regex_file = open(out_path, "w", encoding="utf-8", newline=None)

    regexes = read_regexes(dataset_path)[start:]

    i = start
    for regex in regexes:
        print("{} {}/{} {}".format(dataset_path, i, len(regexes), regex))
        string = generate_str(regex)
        if string == "ERROR" or string == "UNSAT" or string == "TIMEOUT":
            print("\t" + string)
            res = json.dumps({"regex": regex, "type": string})
            fail_regex_file.write(res + "\n")
            fail_regex_file.flush()
        else:
            try:
                res = re.fullmatch(regex, string)
                if re.fullmatch(regex, string) == None:
                    print(f"\t {string} Not Match")
                    res = json.dumps({"regex": regex, "type": "NOTMATCH", "string": string})
                    fail_regex_file.write(res + "\n")
                    fail_regex_file.flush()
                else:
                    print("\t" + string)
            except:
                print("\t re.error")
                res = json.dumps({"regex": regex, "type": "UNKNOWN", "string": string})
                fail_regex_file.write(res + "\n")
                fail_regex_file.flush()
        i += 1
    fail_regex_file.flush()
    fail_regex_file.close()

if __name__ == "__main__":
    dataset_path = sys.argv[1]

    file_name = os.path.basename(dataset_path)
    out_path = file_name + "-fail.txt"
    single_dataset(dataset_path, out_path)