#!/usr/bin/env python
# Copyright 2012 The ocstyle Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Basic Objective C style checker."""

import argparse
import os.path
import sys
import csv
import StringIO

import parcon
import rules

from xml_logger import  XmlLogger

def check(path, maxLineLength):
  """Style checks the given path."""
  with open(path) as f:
    return checkFile(path, f, maxLineLength)


def checkFile(path, f, maxLineLength):
  """Style checks the given file object."""
  content = f.read()
  lineErrors = rules.setupLines(content, maxLineLength)
  result = parcon.Exact(rules.entireFile).parse_string(content)
  if path.endswith(('.m', '.mm')):
    result = [err for err in result if not isinstance(err, rules.Error) or not err.kind.endswith('InHeader')]
  result.extend(lineErrors)
  result.sort(key=lambda err: err.position if isinstance(err, rules.Error) else 0)
  return result

def parseFilename(filename, maxLineLength) :
  if filename.endswith(('.m','.mm','.h')):
    xmlLogger.startFile(filename)
    for part in check(filename, maxLineLength):
        if isinstance(part,rules.Error):
          """sys.stderr.write(os.path.abspath(filename) + '%s\n' % part)"""
          xmlLogger.addError(part);
        else:
          print 'unparsed: %r\n' % part

def proceedFolder(root, excludedFolders, maxLineLength):
  foldersToExclude = None
  if not excludedFolders:
    foldersToExclude = [[None]]
  else :
    foldersToExclude = excludedFolders

  filesAndDirs = [f for f in os.listdir(root)]
  for f in filesAndDirs:
    filePath = os.path.join(root, f)
    if os.path.isfile(filePath):
      parseFilename(filePath, maxLineLength)
    else:
      if not f in foldersToExclude[0]:
        proceedFolder(filePath, foldersToExclude, maxLineLength)


def main():
  """Main body of the script."""

  parser = argparse.ArgumentParser()
  parser.add_argument("--maxLineLength", action="store", type=int, default=120, help="Maximum line length")
  parser.add_argument("--excludedDirs", action="store", type=str)
  parser.add_argument("--xmlLogFolderPath", action="store", type=str)
  parser.add_argument("--checkstyleResultFilename", action="store", type=str, default="checkstyle-result.xml")

  args, filenames = parser.parse_known_args()

  global xmlLogger
  xmlLogger = XmlLogger(StringIO.StringIO(args.xmlLogFolderPath).read(),
                        StringIO.StringIO(args.checkstyleResultFilename).read())
  for filename in filenames:
    if not os.path.isdir(filename):
      parseFilename(filename, args.maxLineLength)
    else :
      f = StringIO.StringIO(args.excludedDirs)
      excludedDirs = csv.reader(f)
      excludedDirs = list(excludedDirs)
      rootdir = filename
      proceedFolder(rootdir, excludedDirs, args.maxLineLength)



            # filePath = os.path.join(root, filename)
            #

      # for root, subFolders, files in os.walk(rootdir):
      #   for file in files:
      #     print os.path.realpath(file)
      #     if os.path.dirname(file) in excludedDirs:


    print
  xmlLogger.persistToDisk();

if __name__ == '__main__':
  main()