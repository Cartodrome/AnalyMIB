import argparse
import re
import warnings
from collections import namedtuple

MIB_START = re.compile("begin (?P<name>[A-Za-z0-9]*)")
MIB_FIELD = re.compile("(?P<name>[A-Za-z0-9]*)\s{0,1}(?P<value>[^\s]*)")
MIB_END   = re.compile("end (?P<name>[A-Za-z0-9]*)") 


class MIB(object):
    def __init__(self, name):
        self.name = name 
        self.fields = {}

    def add_field(self, name, value):
        #if name in self.fields:
            #warnings.warn("%s, field %s with value %s, overwritten with %s" % (
            #    self.name, name, self.fields[name], value), Warning) 
            #print self
            #exit()
        self.fields[name] = value

    def __repr__(self):
        return "BEGIN %s\n %s\nEND" % (self.name, "\n ".join(
            [key + " " + value for key in self.fields for value in 
             self.fields.values()]))


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
        if line == "":
            counter +=1
        if counter == lines_to_give_up:
            raise NoMatches 

        if new_mib:
            if MIB_END.match(line):
                return new_mib

            try:
                r = MIB_FIELD.match(line).groupdict()
            except AttributeError:
                print "Failed to match: %s" % line
                exit()

            try:
                new_mib.add_field(name=r["name"],
                                  value=r["value"])
            except AssertionError:
                new_mib.add_field(name=r["name"],
                                  value="")

            #if new_mib.name == "vpssCfgSipBindTable" or new_mib.name == "mcRtpPortTable":
            #    print r["value"].strip()

        r = MIB_START.match(line)
        if r:
            new_mib = MIB(r.groupdict()["name"])
            #print new_mib.name

def main(args, files1, files2):
    mibs = []
    for f1 in files1:
        while True:
            try:
                mibs.append(get_mib(f1))
            except NoMatches:
                break

        for mib in mibs[:]:
            if mib.name not in mibs_checked:
                print "Analysing: %s" % mib.name
                mibs_checked.append(mib.name)
                results[mib.name] = namedtuple("result", 
                                                        "count, ")
                results[mib.name].count = 0
                for new_mib in mibs[:]:
                    if mib.name == new_mib.name:
                        results[mib.name].count += 1
                    
                print "%s, %s" % (mib.name, results[mib.name].count)


                        
#            if mib.name not in mibs_checked:
#                print "Analysing: %s" % mib.name
#                mibs_checked.append(mib.name)
#                for f2 in files2:
#                    results[f2.name][mib.name] = namedtuple("result", 
#                                                            "count, ")
#                    results[f2.name][mib.name].count = 0
#                    while True:
#                        try:
#                            new_mib = get_mib(f2)
#                        except NoMatches:
#                            break
#                        if new_mib.name == mib.name:
#                            results[f2.name][mib.name].count += 1
#                    
#                    print "%s, %s, %s" % (f2.name, mib.name, results[f2.name][mib.name].count)


    print results
                        



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

