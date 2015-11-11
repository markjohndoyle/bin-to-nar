__author__ = 'markj'

import narGlobals as nar
import os.path

class WindowsLib:

    def __init__(self, libPath, version, type):
        super().__init__()
        self.libPath = libPath
        self.stripExtension(libPath)
        self.libName = os.path.basename(self.libName)
        self.version = version
        self.type = type


    def createNarFileName(self):
        return self.libName + "-" + self.version + nar.NAR_EXTENSION

    def createNarSharedLibFileName(self, aol):
        return  self.libName + "-" + self.version + "-" + aol + "-" + self.type + nar.NAR_EXTENSION

    def createNarNoArchFileName(self):
        return  self.libName + "-" + self.version + "-" + nar.NAR_NOARCH_QUALIFIER + nar.NAR_EXTENSION


    def stripExtension(self,libPath):
        self.libName = os.path.splitext(libPath)[0]