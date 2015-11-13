__author__ = 'markj'

import os.path

from binToNar import narGlobals as nar


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

    def stripExtension(self, libPath):
        soExtIndex = libPath.rfind(nar.LINUX_LIB_EXTENSION)
        if soExtIndex != -1:
            self.libName = self.libPath[:soExtIndex + len(nar.LINUX_LIB_EXTENSION)]
        else:
            self.libName = libPath
        self.libName = os.path.splitext(self.libName)[0]
