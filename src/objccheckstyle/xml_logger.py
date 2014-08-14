# Copyright 2014 The objcstylecheck Authors.
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

from lxml import etree
import error

class XmlLogger(object):

    def __init__(self, xmlLogFolder, checkstyleResultFilename):
        self.xmlLogFolder = xmlLogFolder
        self.checkstyleResultFilename = checkstyleResultFilename
        self.root = etree.Element("checkstyle")

    def startFile(self, fileName):
        self.currentFile = etree.Element("file", {"name":fileName})
        self.root.append(self.currentFile)

    def addError(self, err):
        if isinstance(err, error.Error):
            line = err.line()
            offset = err.offset()
            errorElement = etree.Element("error", {"line":str(line),
                                                   "column":str(offset),
                                                   "message":('%s - %s' % (err.kind, err.message)),
                                                   "source":"objccheckstyle",
                                                   "severity":"error"})
            self.currentFile.append(errorElement)
            return

    def persistToDisk(self):
        filePath = self.xmlLogFolder + "/" + self.checkstyleResultFilename
        file = open(filePath, "w")
        file.write(etree.tostring(self.root, pretty_print=True, xml_declaration=True, encoding='utf-8'));
        file.close()
