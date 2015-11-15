__author__ = 'markj'

import os.path

from binToNar import narGlobals as nar


class LinuxLib:

    def __init__(self, libPath, version, type, ext):
        super().__init__()
        if ext == None:
            self.ext = "." + nar.LINUX_LIB_EXTENSION
        else:
            self.ext = "." + ext
        self.libPath = libPath
        self.libName = os.path.basename(self.libPath)
        self.stripExtension()
        self.stripPrefix()
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

    def stripExtension(self):
        soExtIndex = self.libName.rfind(self.ext)
        if soExtIndex != -1:
            self.libName = self.libName[:soExtIndex + len(self.ext)]
            self.libName = os.path.splitext(self.libName)[0]
