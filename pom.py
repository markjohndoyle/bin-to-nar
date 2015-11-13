__author__ = 'markj'

import xml.etree.ElementTree as ET
import click
import shutil
import narGlobals as nar
from os import path

class Pom:
    ns = {"mvn": "http://maven.apache.org/POM/4.0.0"}

    def __init__(self, pompath, groupid, artifactid, version, outdir):
        #self.fileName = artifactid + "-" + version + nar.POM_EXTENSION
        self.fileName = "pom" + nar.POM_EXTENSION
        self.path = path.join(outdir, self.fileName)
        shutil.copy(pompath, self.path)
        self.project = ET.parse(pompath).getroot()
        self.parsePom(groupid, artifactid, version)


    def parsePom(self, groupid, artifactid, version):
        if self.project is None:
            raise click.BadParameter("Pom does NOT have a root project element.")


        groupIdElems  = self.project.findall("mvn:groupId", self.ns)
        if len(groupIdElems) != 1:
            raise click.BadParameter("The pom file does NOT have a unique groupId element! Found " + str(len(groupIdElems)) + " occurrences.")
        else:
            self.groupId = groupIdElems[0].text

        self.validateGroupId(groupid)


        artifactIdElems  = self.project.findall("mvn:artifactId", self.ns)
        if len(artifactIdElems) != 1:
            raise click.BadParameter("The pom file does NOT have a unique artifactId element! Found " + str(len(artifactIdElems)) + " occurrences.")
        else:
            self.artifactId = artifactIdElems[0].text

        self.validateArtifactId(artifactid)


        versionElems  = self.project.findall("mvn:version", self.ns)
        if len(versionElems) != 1:
            raise click.BadParameter("The pom file does NOT have a unique version element! Found " + str(len(versionElems)) + " occurrences.")
        else:
            self.version = versionElems[0].text

        self.validateVersion(version)

    def validateGroupId(self, groupid):
        if self.groupId != groupid:
            click.secho("The POM groupId ", nl=False)
            click.secho(self.groupId, fg="blue", nl=False)
            click.secho(" does ", nl=False)
            click.secho("NOT ", fg="red", bold=True, nl=False)
            click.secho("match the desired groupId ", nl=False)
            click.secho(groupid, fg="blue")
            if click.confirm("Would you like me to repair the pom file for you?"):
                self.updatePom()
            else:
                raise click.BadParameter("Pom does NOT have the correct groupId.")

    def validateArtifactId(self, artifactid):
        if self.artifactId != artifactid:
            click.secho("The POM artifactId ", nl=False)
            click.secho(self.artifactId, fg="blue", nl=False)
            click.secho(" does ", nl=False)
            click.secho("NOT ", fg="red", bold=True, nl=False)
            click.secho("match the desired artifactId ", nl=False)
            click.secho(artifactid, fg="blue")
            if click.confirm("Would you like me to repair the pom file for you?"):
                self.edited = True
                pass
            else:
                raise click.BadParameter("Pom does NOT have the correct artifactId.")

    def validateVersion(self, version):
        if self.version != version:
            click.secho("The POM version ", nl=False)
            click.secho(self.version, fg="blue", nl=False)
            click.secho(" does ", nl=False)
            click.secho("NOT ", fg="red", bold=True, nl=False)
            click.secho("match the desired version ", nl=False)
            click.secho(version, fg="blue")
            if click.confirm("Would you like me to repair the pom file for you?"):
                pass
            else:
                raise click.BadParameter("Pom does NOT have the correct version.")


    def updatePom(self):
        pass
