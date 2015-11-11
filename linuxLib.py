__author__ = 'markj'

import narGlobals as nar
import os.path

class LinuxLib:

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

    def stripPrefix(self):
        if self.libName.startswith(nar.LINUX_LIB_PREFIX):
            self.libName = self.libName[len(nar.LINUX_LIB_PREFIX):]
        else:
            # verbose output stuff
            pass

    def stripExtension(self,libPath):
        '''
        This could be a pain on Linux as there are no real extension standards. A library could be
        libx.so or libx.so.10.1.2
        '''
        self.libName = os.path.splitext(libPath)[0]
