# -*- coding: utf-8 -*-

__author__ = 'markj'

import click
from subprocess import call
from os import makedirs
from os import path

import narGlobals as nar
from linuxLib import LinuxLib
from windowsLib import WindowsLib
from pom import Pom
import shutil

verbosity = 0


@click.command()
@click.option("-l", "--libpath", type=click.Path(exists=True), help="The path to the library you wish to create a NAR from.", prompt=True)
@click.option("-i", "--includepath", type=click.Path(exists=True),
              help="The path to the library includes, that is, the non-architecture specific headers.", prompt=True)
@click.option("-p", "--pompath", type=click.Path(exists=True),
              help="The pom file that describes this project. Auto-generation not currently supported.", prompt=True)
@click.option("-g", "--groupid", help="Unique identifier for your project following package name rules.", prompt=True)
@click.option("-a", "--artifactid", help="The name of the library.", prompt=True)
@click.option("-vr", "--version", help="The version of the library.", prompt=True)
@click.option("-ar", "--architecture", type=click.Choice(nar.ARCH_TYPES), help="The architecture the library was built on.", prompt=True)
@click.option("-o", "--os", type=click.Choice(nar.OS_TYPES), help="The operating system the library was built on.", prompt=True)
@click.option("-ln", "--linker", type=click.Choice(nar.LINKER_TYPES), help="The linker the library was built with.", prompt=True)
@click.option("-t", "--type", type=click.Choice(nar.LIB_TYPES), help="The type of library.", prompt=True)
@click.option("-in", "--install", default=False, is_flag=True, help="Whether to install the resultant NARs into the local maven repo.")
@click.option("-v", "--verbose", count=True, help="Verbosity of the utility. Accepts one or to repeats for two levels of output, e.g. -v or -vv")
@click.argument("outdir", type=click.Path(exists=True))
def enterCommandLine(libpath, includepath, pompath, groupid, artifactid, version, architecture, os, linker, type, install, verbose, outdir):
    """
    Wraps an existing native library in a NAR package for use with the nar plugin in the maven build system.

    OUTDIR is the location you wish to generate the files.

    """
    click.secho("-----------------------", bold=True, fg="green")
    click.secho("Binary to NAR generator", bold=True, fg="green")
    click.secho("-----------------------", bold=True, fg="green")

    global verbosity
    verbosity = verbose

    aol = createAol(architecture, os, linker)

    if os == "Linux":
        lib = LinuxLib(libpath, version, type)
    else:
        lib = WindowsLib(libpath, version, type)

    pom = Pom(pompath, groupid, artifactid, version)

    printPlan(aol, lib, pom, install, outdir)

    if click.confirm("\nShall we get on with it?", default=True):
        click.secho("Ok, sit back and relax!")
        createNar(lib, aol, groupid, artifactid, architecture, os, linker)
        createNoArchNar(lib, includepath)
        createLibNar(lib, aol)
        if install:
            installNar(pom, lib)

    click.secho("We're done!", bold=True, fg="green")


def printPlan(aol, lib, pom, install, outdir):
    click.secho("Library details:", bold=True)
    click.secho("  ├── Name is " + lib.libName)
    click.secho("  ├── Type is " + lib.type)
    click.secho("  ├── AOL is " + aol)
    click.secho("  └── Version is " + lib.version)
    click.secho("Execution plan:", bold=True)
    click.secho("  ├── 1. Create base NAR file called " + lib.createNarFileName())
    click.secho("  ├── 2. Create non-architecture specific NAR file called " + lib.createNarNoArchFileName())
    click.secho("  ├── 3. Create shared lib NAR file called " + lib.createNarSharedLibFileName(aol))
    if not install:
        click.secho("  └── 4. Use the pom file " + pom.path)
    else:
        click.secho("  ├── 4. Use the pom file " + pom.path)
        click.secho("  └── 5. Install the artefacts into the local repository")

    click.echo()
    click.secho("Files will be generated in ", nl=False)
    click.secho(outdir, fg="blue", bold=True)

    if install:
        click.echo("The NARS", nl=False)
        click.secho(" WILL ", nl=False, bold=True, fg="blue")
        click.echo("be installed into the local repo and available for use immediately.")
    else:
        click.echo("The NARS will", nl=False)
        click.secho(" NOT ", nl=False, bold=True, fg="red")
        click.echo("be installed into the local repo and therefore not available for use.")


def createAol(architecture, os, linker):
    if (linker == "g++"):
        return architecture + "-" + os + "-gpp"
    else:
        return architecture + "-" + os + "-" + linker


def createNar(lib, aol, groupId, artifactId, arch, operatingSystem, linker):
    propertiesPath = "META-INF/nar/" + groupId + "/" + artifactId
    makedirs(propertiesPath, exist_ok=True)

    narProps = open(path.join(propertiesPath, "nar.properties"), 'w')

    narProps.write("output=" + lib.libName + "-" + lib.version + "\n")
    narProps.write("nar.noarch=" + groupId + "\:" + artifactId + "\:nar\:noarch\n")
    narProps.write(aol + ".output=" + lib.libName + "\n")
    narProps.write(aol + ".libs.binding=" + lib.type + "\n")
    narProps.write("libs.binding=" + lib.type + "\n")
    narProps.write("nar.shared=" + groupId + "\:" + artifactId + "\:nar\:${aol}-" + lib.type + "\n")
    narProps.close()

    createJar(lib.createNarFileName(), "META-INF/")

    shutil.rmtree("META-INF")


def createJar(fileName, files):
    if verbosity > 1:
        jarCommand = ["jar", "-cvfM", fileName, files]
        click.secho(" ".join(jarCommand), fg='magenta')
    else:
        jarCommand = ["jar", "-cfM", fileName, files]
    call(jarCommand, shell=True)


def createNoArchNar(lib, includepath):
    allExceptHeaders = lambda srcDir, files: [f for f in files if path.isfile(path.join(srcDir, f)) and f[-2:] != ".h" or f[-2:] != ".hpp"]
    includeTargetPath = "include"
    shutil.copytree(includepath, includeTargetPath, ignore=allExceptHeaders)
    createJar(lib.createNarNoArchFileName(), "include/")
    shutil.rmtree("include")


def createLibNar(lib, aol):
    libPath = path.join("lib", aol, lib.type)
    makedirs(libPath)
    shutil.copy(lib.libPath, libPath)
    createJar(lib.createNarSharedLibFileName(aol), "lib/")
    shutil.rmtree("lib")


def installNar(pom, lib):
    narInstallCmd = [
                    "mvn", "Bq", "install:install-file",
                    "-Dfile=" + lib.createNarFileName(),
                    "-DgroupId=" + pom.groupId,
                    "-DartifactId=" + pom.artifactId,
                    "-Dpackaging=nar",
                    "-Dversion=" + pom.version,
                    "generatePom=False"
                    ]
    noarchInstallCmd = [
                    "mvn", "Bq", "install:install-file",
                    "-Dfile=" + lib.createNarNoArchFileName(),
                    "-DgroupId=" + pom.groupId,
                    "-DartifactId=" + pom.artifactId,
                    "-Dpackaging=nar",
                    "-Dversion=" + pom.version,
                    "generatePom=False",
                    "classifier=" + nar.NAR_NOARCH_QUALIFIER
                    ]
    libInstallCmd = [
                    "mvn", "Bq", "install:install-file",
                    "-Dfile=" + lib.createNarSharedLibFileName(),
                    "-DgroupId=" + pom.groupId,
                    "-DartifactId=" + pom.artifactId,
                    "-Dpackaging=nar",
                    "-Dversion=" + pom.version,
                    "generatePom=False"
                    "classifier=" + aol + "-" + lib.type
                    ]
    click.secho("Installing NAR file.")
    call(narInstallCmd)
    click.secho("Installing noarch NAR file.")
    call(noarchInstallCmd)
    click.secho("Installing lib NAR file.")
    call(libInstallCmd)
