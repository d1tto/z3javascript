import subprocess
import os
import re
import base64

env = os.environ.copy()
env["Z3_PATH"] = "./bin/libz3.so"

def read_regexes(path):
    f = open(path, "r", encoding="utf-8", newline=None)
    regexes = [line.replace("\n", "") for line in f.readlines()]
    return regexes

def generate_str(regex: str):
    b64regex = base64.b64encode(regex.encode())
    try:
        p = subprocess.run(args=["node", "bin/Tests/cmd.js", b64regex], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        if p.returncode != 0:
            return "ERROR"
        return p.stdout.decode()
    except subprocess.TimeoutExpired as e:
        return "Timeout"

datasets = ["npm.txt"]

def single_dataset(dataset, start):
    file_name = os.path.basename(dataset)
    fail_regex_file = open(file_name + "-fail.txt", "w", encoding="utf-8", newline=None)

    regexes = read_regexes(dataset)[start:]

    i = start
    for regex in regexes:
        print("{} {}/{} {}".format(dataset, i, len(regexes), regex))
        string = generate_str(regex)
        if string == "ERROR" or string == "UNSAT" or string == "Timeout":
            print("\t" + string)
            fail_regex_file.write(regex + "\n")
            fail_regex_file.flush()
        else:
            try:
                res = re.fullmatch(regex, string)
                if re.fullmatch(regex, string) == None:
                    print("\tNot Match")
                    fail_regex_file.write(regex + "\n")
                    fail_regex_file.flush()
                else:
                    print("\t" + string)
            except:
                print("\t re.error")
                fail_regex_file.write(regex + "\n")
                fail_regex_file.flush()
        i += 1
    fail_regex_file.flush()
    fail_regex_file.close()

str = generate_str("111")
print(str)


