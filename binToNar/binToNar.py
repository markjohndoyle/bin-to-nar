# -*- coding: utf-8 -*-

__author__ = 'markj'

from subprocess import call
from os import makedirs
from os import path
import shutil

import click

from binToNar import narGlobals as nar
from binToNar.linuxLib import LinuxLib
from binToNar.windowsLib import WindowsLib
from binToNar.pom import Pom

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
    click.secho("Binary to NAR generator - dev2", bold=True, fg="green")
    click.secho("-----------------------", bold=True, fg="green")

    global verbosity
    verbosity = verbose

    aol = createAol(architecture, os, linker)

    if os == "Linux":
        lib = LinuxLib(libpath, version, type)
    else:
        lib = WindowsLib(libpath, version, type)

    pom = Pom(pompath, groupid, artifactid, version, outdir)

    printPlan(aol, lib, pom, install, outdir)

    if click.confirm("\nShall we get on with it?", default=True):
        click.secho("Ok, sit back and relax!")
        createNar(lib, aol, groupid, artifactid, architecture, os, linker, outdir)
        createNoArchNar(lib, includepath, outdir)
        createLibNar(lib, aol, outdir)
        if install:
            installNar(pom, lib, aol, outdir)

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


def createNar(lib, aol, groupId, artifactId, arch, operatingSystem, linker, outdir):
    propertiesPath = path.join(outdir, "META-INF", "nar", groupId, artifactId)
    makedirs(propertiesPath)

    narProps = open(path.join(outdir, propertiesPath, "nar.properties"), 'w')

    narProps.write("output=" + lib.libName + "-" + lib.version + "\n")
    narProps.write("nar.noarch=" + groupId + "\:" + artifactId + "\:nar\:noarch\n")
    narProps.write(aol + ".output=" + lib.libName + "\n")
    narProps.write(aol + ".libs.binding=" + lib.type + "\n")
    narProps.write("libs.binding=" + lib.type + "\n")
    narProps.write("nar.shared=" + groupId + "\:" + artifactId + "\:nar\:${aol}-" + lib.type + "\n")
    narProps.close()

    createJar(lib.createNarFileName(), "META-INF/", outdir)

    shutil.rmtree(path.join(outdir, "META-INF/"))


def createNoArchNar(lib, includepath, outdir):
    allExceptHeaders = lambda srcDir, files: [f for f in files if path.isfile(path.join(srcDir, f)) and f[-2:] != ".h" and f[-4:] != ".hpp"]
    includeTargetPath = path.join(outdir, "include")
    shutil.copytree(includepath, includeTargetPath, ignore=allExceptHeaders)
    createJar(lib.createNarNoArchFileName(), "include/", outdir)
    shutil.rmtree(includeTargetPath)


def createLibNar(lib, aol, outdir):
    libPath = path.join(outdir, "lib", aol, lib.type)
    makedirs(libPath)
    shutil.copy(lib.libPath, libPath)
    createJar(lib.createNarSharedLibFileName(aol), "lib/", outdir)
    shutil.rmtree(path.join(outdir, "lib"))

def createJar(fileName, files, outdir):
    if verbosity > 1:
        jarCommand = ["jar", "-cvfM", path.join(outdir, fileName), "-C", outdir, files]
        click.secho(" ".join(jarCommand), fg='magenta')
    else:
        jarCommand = ["jar", "-cfM", path.join(outdir, fileName), "-C", outdir, files]
    call(jarCommand)


def installNar(pom, lib, aol, outdir):
    narInstallCmd = [
                    "mvn", "org.apache.maven.plugins:maven-install-plugin:2.5.2::install-file",
                    "\"-Dfile=" + path.join(outdir, lib.createNarFileName()) + "\"",
                    "\"-Dtype=nar" + "\"",
                    "\"-DgroupId=" + pom.groupId  + "\"",
                    "\"-DartifactId=" + pom.artifactId  + "\"",
                    "\"-Dversion=" + pom.version + "\"",
                    "\"-Dpackaging=nar\"",
                    "\"-DgeneratePom=false\""
                    ]
    noarchInstallCmd = [
                    "mvn", "org.apache.maven.plugins:maven-install-plugin:2.5.2::install-file",
                    "\"-Dfile=" + path.join(outdir, lib.createNarNoArchFileName()) + "\"",
                    #"\"-DgroupId=" + pom.groupId  + "\"",
                    #"\"-DartifactId=" + pom.artifactId  + "\"",
                    #"\"-Dversion=" + pom.version + "\"",
                    "\"-Dpackaging=nar\"",
                    "\"-DgeneratePom=false\"",
                    "\"-Dclassifier=" + nar.NAR_NOARCH_QUALIFIER  + "\"",
                    "\"-DpomFile=" + pom.path + "\""
                    ]
    libInstallCmd = [
                    "mvn", "org.apache.maven.plugins:maven-install-plugin:2.5.2::install-file",
                    "\"-Dfile=" + path.join(outdir, lib.createNarSharedLibFileName(aol)) + "\"",
                    "\"-Dpackaging=nar\"",
                    "\"-DgeneratePom=false\"",
                    "\"-Dclassifier=" + aol + "-" + lib.type + "\"",
                    "\"-DpomFile=" + pom.path + "\""
                    ]

    click.secho("Installing NAR file.", fg="green")
    click.secho(" ".join(narInstallCmd), fg="cyan")
    retcode = call(narInstallCmd, shell=True, cwd=outdir)
    if retcode != 0:
        raise click.ClickException("Error installing NAR file")
    else:
        click.secho("Installing noarch NAR file.", fg="green")
        click.secho(" ".join(noarchInstallCmd), fg="cyan")
        retcode = call(noarchInstallCmd, shell=True, cwd=outdir)
        if retcode != 0:
            raise click.ClickException("Error installing NAR file")
        else:
            click.secho(" ".join(libInstallCmd), fg="cyan")
            click.secho("Installing lib NAR file.", fg="green")
            call(libInstallCmd, shell=True, cwd=outdir)
