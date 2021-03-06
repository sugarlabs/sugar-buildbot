import os
import json

from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.config import BuilderConfig
from buildbot.steps.transfer import DirectoryUpload
from buildbot.steps.transfer import FileUpload
from buildbot.steps.master import MasterShellCommand
from buildbot.process.properties import Interpolate


class PullCommand(ShellCommand):
    def setBuild(self, build):
        ShellCommand.setBuild(self, build)

        sources = {}
        for source_stamp in build.getAllSourceStamps():
            name =  source_stamp.repository.split("/")[-1];
            sources[name] = {"repository": source_stamp.repository,
                             "revision": source_stamp.revision}

        command = ["./osbuild", "pull"]

        if sources:
            sources_json = json.dumps(sources)
            command.extend(["--sources", sources_json])

        self.setCommand(command)


def get_command_path(command):
    return os.path.join(os.path.dirname(__file__), "commands", command)


def create_factory(config, mode="incremental"):
    factory = BuildFactory()

    factory.addStep(Git(repourl=config["repo"],
                        alwaysUseLatest=True,
                        mode=mode))

    return factory


def add_broot_steps(factory, arch, branch, env={}):
    factory.addStep(ShellCommand(command=["./osbuild", "broot", "clean"],
                                 description="cleaning",
                                 descriptionDone="clean",
                                 haltOnFailure=True,
                                 env=env))

    command = ["./osbuild", "broot", "create", "--arch=%s" % arch]
    factory.addStep(ShellCommand(command=command,
                                 description="creating",
                                 descriptionDone="create",
                                 haltOnFailure=True,
                                 env=env))

    factory.addStep(ShellCommand(command=["./osbuild", "broot", "distribute"],
                                 description="distributing",
                                 descriptionDone="distribute",
                                 haltOnFailure=True,
                                 env=env))

    broot_dir = "~/public_html/broot/"
    broot_filename = "%(prop:buildername)s-%(prop:buildnumber)s.tar.xz"

    masterdest = Interpolate(os.path.join(broot_dir, broot_filename))
    factory.addStep(FileUpload(slavesrc="build/sugar-build-broot.tar.xz",
                               masterdest=masterdest))

    command = Interpolate("%s %s %s %s %s" %
                          (get_command_path("release-broot"), broot_dir,
                           broot_filename, arch, branch))

    factory.addStep(MasterShellCommand(command=command,
                                       description="releasing",
                                       descriptionDone="release"))


def add_steps(factory, env={}, clean=False, upload_docs=False,
              upload_dist=False):
    log_path = "build/logs/osbuild.log"

    if clean:
        step = ShellCommand(command=["./osbuild", "clean", "--broot"],
                            description="cleaning",
                            descriptionDone="clean",
                            haltOnFailure=True,
                            logfiles={"log": log_path},
                            env=env)
        factory.addStep(step)

    factory.addStep(PullCommand(description="pulling",
                                descriptionDone="pull",
                                haltOnFailure=True,
                                logfiles={"log": log_path},
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

        command = "%s %s %s" % (get_command_path("release-dist"),
                                dist_dir, downloads_dir)

        factory.addStep(MasterShellCommand(command=command,
                                           description="releasing",
                                           descriptionDone="release"))

    return factory


def setup(c, config):
    c["builders"] = []

    env = {"SUGAR_BUILDBOT": "yes"}

    slavenames = config["slaves"].keys()

    for branch in config["branches"]:
        factory = create_factory(config)
        add_steps(factory, env=env, upload_docs=True, upload_dist=True)

        builder = BuilderConfig(name="quick-%s" % branch,
                                category="upstream",
                                slavenames=slavenames,
                                factory=factory)
        c["builders"].append(builder)

        factory = create_factory(config)
        add_steps(factory, env=env)

        builder = BuilderConfig(name="try-%s" % branch,
                                category="pullrequest",
                                slavenames=slavenames,
                                factory=factory)
        c["builders"].append(builder)

        factory = create_factory(config)
        add_steps(factory, env=env, clean=True)

        builder = BuilderConfig(name="full-%s" % branch,
                                category="upstream",
                                slavenames=slavenames,
                                factory=factory)

        c["builders"].append(builder)

        for arch in config["architectures"]:
            factory = create_factory(config, "full")
            add_broot_steps(factory, arch, branch, env=env)

            arch_slavenames = [name for name in slavenames
                               if config["slaves"][name]["arch"] == arch]

            builder = BuilderConfig(name="broot-%s-%s" % (arch, branch),
                                    category="upstream",
                                    slavenames=arch_slavenames,
                                    factory=factory)

            c["builders"].append(builder)
