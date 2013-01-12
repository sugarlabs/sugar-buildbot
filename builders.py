import json
import pipes

from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.steps.master import MasterShellCommand
from buildbot.config import BuilderConfig
from buildbot.locks import MasterLock
from buildbot.process.properties import Interpolate
from buildbot.steps.transfer import DirectoryUpload
from buildbot.steps.transfer import FileUpload


class PullCommand(ShellCommand):
    def setBuild(self, build):
        ShellCommand.setBuild(self, build)

        revisions = {}
        for source in build.getAllSourceStamps():
            if source.revision:
                revisions[source.codebase] = source.revision

        command = ["make", "pull"]

        if revisions:
            revisions_json = pipes.quote(json.dumps(revisions))
            command.append("ARGS=--revisions=%s" % revisions_json)

        self.setCommand(command)


def create_factory(config, env={}, full=False, distribute=False,
                   upload_docs=False, snapshot=False):
    factory = BuildFactory()

    factory.addStep(Git(repourl=config["repo"],
                        codebase="sugar-build",
                        branch=config.get("branch", "master")))

    if config.get("check_system", True):
        command = ["make", "check-system", "ARGS=--update --remove"]
        factory.addStep(ShellCommand(command=command,
                                     description="checking system",
                                     descriptionDone="check system",
                                     warnOnFailure=True,
                                     env=env))

    factory.addStep(PullCommand(description="pulling",
                                descriptionDone="pull",
                                haltOnFailure=True,
                                logfiles={"log": "logs/pull.log"},
                                env=env))

    command = ["make", "build"]
    if full:
        command.append("ARGS=--full")

    factory.addStep(ShellCommand(command=command,
                                 description="building",
                                 descriptionDone="build",
                                 haltOnFailure=True,
                                 logfiles={"log": "logs/build.log"},
                                 env=env))

    factory.addStep(ShellCommand(command=["make", "check"],
                                 description="checking",
                                 descriptionDone="check",
                                 haltOnFailure=True,
                                 logfiles={"log": "logs/check.log"},
                                 env=env))

    if distribute:
        factory.addStep(ShellCommand(command=["make", "distribute"],
                                     description="distributing",
                                     descriptionDone="distribute",
                                     env=env))

    if upload_docs:
        docs_url = "http://shell.sugarlabs.org/~buildbot/docs/index.html"
        factory.addStep(DirectoryUpload(slavesrc="build/sugar-docs/html",
                                        masterdest="~/public_html/docs",
                                        url=docs_url))

    if snapshot:
        factory.addStep(ShellCommand(command=["make", "snapshot"],
                                     description="building snapshot",
                                     descriptionDone="build snapshot",
                                     warnOnFailure=True,
                                     env=env))

        masterdest = "~/public_html/snapshots/snapshot.tar.xz"
        factory.addStep(FileUpload(slavesrc="snapshot.tar.xz",
                                   masterdest=masterdest,
                                   mode=0755))

        command = Interpolate("~/public_html/snapshots/upload-completed "
                              "%(prop:slavename)s %(prop:buildnumber)s")
        factory.addStep(MasterShellCommand(command=command,
                                           description="releasing snapshot",
                                           descriptionDone="release snapshot"))

    return factory


def setup(c, config):
    c["builders"] = []

    bender_lock = MasterLock("bender")

    for name, info in config["slaves"].items():
        env = {"SUGAR_BUILDBOT": name,
               "PYTHONUNBUFFERED": "yes"}

        factory = create_factory(config, env=env,
                                 distribute=config.get("distribute", False),
                                 upload_docs=info.get("upload_docs", False))

        builder = BuilderConfig(name="%s-quick" % name,
                                slavenames=[name],
                                factory=factory,
                                category="quick",
                                locks=[bender_lock.access("exclusive")])
        c["builders"].append(builder)

        factory = create_factory(config, env=env, full=True,
                                 snapshot=config.get("snapshot", False))

        builder = BuilderConfig(name="%s-full" % name,
                                slavenames=[name],
                                factory=factory,
                                category="full",
                                locks=[bender_lock.access("exclusive")])

        c["builders"].append(builder)
