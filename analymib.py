import argparse
import re
import warnings
from collections import namedtuple
import time

MIB_START = re.compile("begin (?P<name>[A-Za-z0-9]*)")
MIB_FIELD = re.compile("\s*(?P<name>[A-Za-z0-9]+)\s{0,1}(?P<value>.*)")
MIB_END   = re.compile("end")


class MIB(object):
    def __init__(self, name):
        self.name = name
        self.fields = {}

    def add_field(self, name, value):
        self.fields[name] = value

    def __repr__(self):
        return "BEGIN %s\n %s\nEND" % (self.name, "\n ".join(
            [key + " " + value for key in self.fields for value in
             [self.fields[key]]]))


class MIBFile(object):
    def __init__(self, name):
        self.name = name
        self.file = open(name, "r")

    def readline(self):
        return self.file.readline()

    def readlines(self):
        location = self.file.tell()
        self.file.seek(0)
        result = self.readlines()
        self.file.seek(location)
        return result

    def reset_file(self):
        self.location = 0


class NoMatches(Exception):
    pass

def get_mib(f):
    keep_looking = True
    lines_to_give_up = 10
    counter = 0
    new_mib = None
    while keep_looking:
        line = f.readline()
        #print line
        if line == "":
            counter +=1
        if counter == lines_to_give_up:
            raise NoMatches

        if new_mib:
            if MIB_END.match(line):
                #print "X end"
                return new_mib

            try:
                r = MIB_FIELD.match(line).groupdict()
            except AttributeError:
                if line[0] == "#":
                    continue
                else:
                    #print "Failed to match: %s" % line
                    continue

            try:
                #print "X add field"
                new_mib.add_field(name=r["name"],
                                  value=r["value"])
               # print "X field added"
            except AssertionError:
                print "X blank field"
                new_mib.add_field(name=r["name"],
                                  value="")
                #print "X added blank"


        r = MIB_START.match(line)
        if r:
            #print "X start"
            new_mib = MIB(r.groupdict()["name"])
            #print new_mib.name

def main(args, files1, files2):
    container = {}
    for f1 in files1:
        container[f1.name] = []
        while True:
            try:
                mib = get_mib(f1)
                container[f1.name].append(mib)
            except NoMatches:
                break



    for f1 in container:
        for mib in container[f1]:
            if mib.name not in mibs_checked:
                print "Analysing: %s" % mib.name
                mibs_checked.append(mib.name)

                for f2 in container:
                    results[f2][mib.name] = namedtuple("result",
                                                       "count,same_fields,identical_fields")
                    results[f2][mib.name].count = 0
                    results[f2][mib.name].same_fields = 0
                    results[f2][mib.name].identical_fields = 0
                    for new_mib in container[f2]:
                        if mib.name == new_mib.name:
                            results[f2][mib.name].count += 1
                            if mib.fields.keys() == new_mib.fields.keys():
                                results[f2][mib.name].same_fields += 1
                            if mib.fields == new_mib.fields:
                                results[f2][mib.name].identical_fields += 1

                    #print "%s, %s, %s" % (f2, mib.name, results[f2][mib.name].count)


    results_file = open("results.csv", "w")
    print results
    print results.keys()
    results_file.write(",%s\n" % ",".join(results))
    for result in results:
        for mib_name in results[result]:
            results_file.write("%s,%s,%s,%s\n" % (
                mib_name,
                ",".join([str(results[f][mib_name].count) for f in results]),
                ",".join([str(results[f][mib_name].same_fields) for f in results]),
                ",".join([str(results[f][mib_name].identical_fields) for f in results])))

        break


def get_args():
    parser = argparse.ArgumentParser(description="AnalyMIB")
    parser.add_argument('files', nargs='+', type=str,
        help="Names of files to compare.")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    files1 = [MIBFile(f) for f in args.files]
    files2 = [MIBFile(f) for f in args.files]
    mibs_checked = []
    results = {}
    for f in args.files:
        results[f] = {}

    main(args, files1, files2)

