# Bin-to-nar tool packages and installs existing libraries as NAR artefacts.

## Prerequisites
Python3 compiled with enabled openSsl module
Python setuptools
Apache Maven: https://maven.apache.org/

## Build 
``` ./setup.py build ```

## Installation
``` ./setup.py install ```

## More setup options
```
usage: setup.py [global_opts] cmd1 [cmd1_opts] [cmd2 [cmd2_opts] ...]
or: setup.py --help [cmd1 cmd2 ...]
or: setup.py --help-commands
or: setup.py cmd --help
```

# Usage
```
binToNar --help
Usage: binToNar [OPTIONS] OUTDIR

  Wraps an existing native library in a NAR package for use with the nar
  plugin in the maven build system.

  OUTDIR is the location you wish to generate the files.

Options:
  -l, --libpath PATH              The path to the library you wish to create a
                                  NAR from.
  -i, --includepath PATH          The path to the library includes, that is,
                                  the non-architecture specific headers.
  -p, --pompath PATH              The pom file that describes this project.
                                  Auto-generation not currently supported.
  -g, --groupid TEXT              Unique identifier for your project following
                                  package name rules.
  -a, --artifactid TEXT           The name of the library.
  -vr, --version TEXT             The version of the library.
  -ar, --architecture [x86|i386|amd64|ppc|x86_64|sparc]
                                  The architecture the library was built on.
  -o, --os [Windows|Linux|MacOSX|SunOS|FreeBSD]
                                  The operating system the library was built
                                  on.
  -ln, --linker [msvc|g++|gcc|icc|icpc|ecc|ecpc|CC]
                                  The linker the library was built with.
  -t, --type [shared|static]      The type of library.
  -in, --install                  Whether to install the resultant NARs into
                                  the local maven repo.
  -d, --deploy TEXT...            Whether to deploy the resultant NARs into a
                                  given repo. Requires the repo URL and the
                                  server id
  --ext TEXT                      If your library has a non-standard filename
                                  extension you can provide it here.
  -v, --verbose                   Verbosity of the utility. Accepts one or to
                                  repeats for two levels of output, e.g. -v or
                                  -vv
  --help                          Show this message and exit.
```
## Example
Consider the following source project structure:
```
my_project|--lib
          |     |--my_shared_object.so
          |--include
          |         |--my_header.h
          |--target
          |
          |--maven
                  |--my_project_pom.xml
```

To build nar artifacts locally in output directory target:

cd my_project
binToNar -l lib/my_shared_object.so -i include -p maven/my_project_pom.xml -g
my_company.my_project -a my_artifact -vr my_version -o Linux -ln g++ -t shared
target


To build nar artifacts and install to local maven repository:

cd my_project

```
binToNar -l lib/my_shared_object.so -i include -p maven/my_project_pom.xml -g
my_company.my_project -a my_artifact -vr my_version -o Linux -ln g++ -t shared -in target
```

To build nar artifacts and deploy to external server(e.g. Nexus):

cd my_project

```
binToNar -l lib/my_shared_object.so -i include -p maven/my_project_pom.xml -g
my_company.my_project -a my_artifact -vr my_version -o Linux -ln g++ -t shared
-d https://my_server/my_repository my_server_id target
```

Note: Access to external server needs to be configured in Apache Maven
configuration (settings.xml)
