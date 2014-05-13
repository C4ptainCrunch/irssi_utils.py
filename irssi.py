#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Written by Lasse Karstensen <lasse.karstensen@gmail.com>, 2008.
# Released under GPLv2 at http://hyse.org/irssi-log-merge/
#
# Modified by Nikita Marchant <nikita.marchant@gmail.com>, 2014
# Released under GPLv3 at http://github.com/C4ptainCrunCh/irssi_utils.py

import os, sys, glob, shutil, codecs

from helpers import handle_charset, dump, parse_timestamp

__all__ = ["IrssiLogMerger"]

class IrssiLogMerger():
    def __init__(self):
        self.linebuf = ''
        self.sessionbuf = ''
        self.files = {}
        self.merge_result = None

    def addfile(self, filename):
        if not self.merge_result is None:
            raise RuntimeError("Merge already occured, you may not add any more files")

        self.files[filename] = {
            'fp': codecs.open(filename, 'r+'),
            'time': None,
            'closed': False,
            'buffer': u''
        }

    def __repr__(self):
        return "<LogMerger {} files>".format(len(self.files))

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        if not self.merge_result is None:
            return self.merge_result

        self.merge_result = ""
        if len(self.files) == 0:
            return self.merge_result

        pref = None

        while True:
            if not pref:
                t1 = None
                for filename, fdict in self.files.items():
                    if fdict["closed"]:
                        continue

                    l = fdict["fp"].readline()

                    l = handle_charset(l)

                    fdict["buffer"] += l
                    if l.startswith('--- Log opened'):
                        datestring = " ".join(l.split()[3:])
                        try:
                            dt = parse_timestamp(datestring)
                        except ValueError as e:
                            print("ERROR: ValueError when parsing timestamp.")
                            raise e
                        fdict["time"] = dt


                active = []
                for filename, fdict in self.files.items():
                    if not fdict["closed"]:
                        active.append(filename)
                if len(active) == 0:
                    #print "No more data to read"
                    return self.merge_result
                # loop through all files and find the one with the earliest
                # timestamp.
                for filename, fdict in self.files.items():
                    if fdict["closed"]:
                        continue

                    #print "File: %s\ttimestamp: %s" % (filename, fdict["time"])
                    if t1 == None:
                        t1 = fdict["time"]

                    if fdict["time"] <= t1:
                        t1 = fdict["time"]
                        pref = filename
                #print "Finished electing. file %s. ts=%s, pref: %s" % (filename, t1,  pref)

            #print "dumping block from file %s (ts: %s)" % (pref, self.files[pref]["time"])
            while True:
                if len(self.files[pref]["buffer"]) > 0:
                    l = self.files[pref]["buffer"]
                    self.files[pref]["buffer"] = u''
                else:
                    l = self.files[pref]["fp"].readline()
                    l = handle_charset(l)
                    #print type(l), dump(l)
                    if len(l) == 0:
                        #print "end of file %s, forcing new election" % filename
                        self.files[pref]["closed"] = True
                        pref = None
                        break

                try:
                    self.merge_result += l
                except UnicodeEncodeError as e:
                    #print(type(l), dump(l)
                    print(e)
                    raise Exception

                if l.startswith('--- Log closed'):
                    #print "end of block, forcing new election"
                    pref = None
                    break


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Merge irssi logs')
    parser.add_argument('output', metavar='OUTPUT', type=str,
                   help='output file')
    parser.add_argument('inputs', metavar='INTPUT', type=str, nargs='+',
                   help='input files')

    args = parser.parse_args()

    merger = IrssiLogMerger()

    for f in args.inputs:
        merger.addfile(f)

    with open(args.output, "w") as out:
        out.write(str(merger))
