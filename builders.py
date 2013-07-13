import os
import json

from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.config import BuilderConfig
from buildbot.steps.transfer import DirectoryUpload
from buildbot.steps.master import MasterShellCommand


class PullCommand(ShellCommand):
    def setBuild(self, build):
        ShellCommand.setBuild(self, build)

        revisions = {}
        for source in build.getAllSourceStamps():
            if source.revision:
                revisions[source.codebase] = source.revision

        command = ["./osbuild", "pull"]

        if revisions:
            revisions_json = json.dumps(revisions)
            command.extend(["--revisions", revisions_json])

        self.setCommand(command)


def create_factory(config, mode="incremental"):
    factory = BuildFactory()

    factory.addStep(Git(repourl=config["repo"],
                        codebase="sugar-build",
                        branch=config.get("branch", "master"),
                        mode=mode))

    return factory


def add_broot_steps(factory, env={}):
    factory.addStep(ShellCommand(command=["./osbuild", "broot", "create"],
                                 description="creating",
                                 descriptionDone="create",
                                 haltOnFailure=True,
                                 env=env))

    factory.addStep(ShellCommand(command=["./osbuild", "broot", "distribute"],
                                 description="distributing",
                                 descriptionDone="distribute",
                                 haltOnFailure=True,
                                 env=env))


def add_steps(factory, env={}, clean=False, upload_docs=False,
              upload_dist=False):
    log_path = "build/logs/main.log"

    if clean:
        step = ShellCommand(command=["./osbuild", "clean", "--broot"],
                            description="cleaning",
                            descriptionDone="clean",
                            haltOnFailure=True,
                            logfiles={"log": log_path,
                                      "broot": "build/logs/broot.log"},
                            env=env)
        factory.addStep(step)

    factory.addStep(PullCommand(description="pulling",
                                descriptionDone="pull",
                                haltOnFailure=True,
                                logfiles={"log": log_path,
                                          "broot": "build/logs/broot.log"},
                                env=env))

    factory.addStep(ShellCommand(command=["./osbuild", "build"],
                                 description="building",
                                 descriptionDone="build",
                                 haltOnFailure=True,
                                 logfiles={"log": log_path},
                                 env=env))

    logfiles = {"log": log_path,
                "smoketest": "build/logs/check-smoketest.log",
                "modules": "build/logs/check-modules.log"}

    factory.addStep(ShellCommand(command=["./osbuild", "check"],
                                 description="checking",
                                 descriptionDone="check",
                                 haltOnFailure=True,
                                 logfiles=logfiles,
                                 env=env))

    factory.addStep(ShellCommand(command=["./osbuild", "docs"],
                                 description="docs",
                                 descriptionDone="docs",
                                 haltOnFailure=True,
                                 logfiles={"log": log_path},
                                 env=env))

    if upload_docs:
        docs_url = "http://developer.sugarlabs.org/"
        factory.addStep(DirectoryUpload(slavesrc="build/out/docs",
                                        masterdest="~/public_html/docs",
                                        url=docs_url))

    factory.addStep(ShellCommand(command=["./osbuild", "dist"],
                                 description="distribution",
                                 descriptionDone="distribution",
                                 haltOnFailure=True,
                                 logfiles={"log": log_path},
                                 env=env))

    if upload_dist:
        dist_dir = "~/dist"
        downloads_dir = "/srv/www-sugarlabs/download/sources/sucrose/glucose"

        factory.addStep(DirectoryUpload(slavesrc="build/out/dist",
                                        masterdest=dist_dir))

        commands_dir = os.path.join(os.path.dirname(__file__), "commands")
        command = "%s %s %s" % (os.path.join(commands_dir, "release-dist"),
                                dist_dir, downloads_dir)

        factory.addStep(MasterShellCommand(command=command,
                                           description="releasing",
                                           descriptionDone="release"))

    return factory


def setup(c, config):
    c["builders"] = []

    env = {"SUGAR_BUILDBOT": "yes"}

    factory = create_factory(config)
    add_steps(factory, env=env, upload_docs=True, upload_dist=True)

    slavenames = config["slaves"].keys()

    builder = BuilderConfig(name="quick",
                            slavenames=slavenames,
                            factory=factory,
                            category="quick")
    c["builders"].append(builder)

    factory = create_factory(config)
    add_steps(factory, env=env, clean=True)

    builder = BuilderConfig(name="full",
                            slavenames=slavenames,
                            factory=factory,
                            category="full")

    c["builders"].append(builder)

    factory = create_factory(config, "full")
    add_broot_steps(factory, env=env)

    builder = BuilderConfig(name="broot",
                            slavenames=slavenames,
                            factory=factory,
                            category="broot")

    c["builders"].append(builder)
