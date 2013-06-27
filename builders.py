import json

from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.config import BuilderConfig
from buildbot.locks import MasterLock
from buildbot.steps.transfer import DirectoryUpload


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


def create_factory(config, env={}, full=False, upload_docs=False):
    log_path = "build/logs/main.log"

    factory = BuildFactory()

    factory.addStep(Git(repourl=config["repo"],
                        codebase="sugar-build",
                        branch=config.get("branch", "master")))

    factory.addStep(ShellCommand(command=["./osbuild", "check-config"],
                                 description="checking config",
                                 descriptionDone="check config",
                                 haltOnFailure=True,
                                 env=env))

    if config.get("check_system", True):
        command = ["./osbuild", "check-system", "--update", "--remove"]
        factory.addStep(ShellCommand(command=command,
                                     description="checking system",
                                     descriptionDone="check system",
                                     warnOnFailure=True,
                                     flunkOnFailure=False,
                                     logfiles={"log": log_path},
                                     env=env))

    factory.addStep(PullCommand(description="pulling",
                                descriptionDone="pull",
                                haltOnFailure=True,
                                logfiles={"log": log_path},
                                env=env))

    command = ["./osbuild", "build"]
    if full:
        command.append("--clean-all")

    factory.addStep(ShellCommand(command=command,
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

    return factory


def setup(c, config):
    c["builders"] = []

    locks = {}

    for name, info in config["slaves"].items():
        lock_name = info.get("lock", None)
        if lock_name and lock_name not in locks:
            locks[lock_name] = MasterLock(lock_name)

        env = {"SUGAR_BUILDBOT": name,
               "PYTHONUNBUFFERED": "yes"}

        factory = create_factory(config, env=env,
                                 upload_docs=info.get("upload_docs", False))

        builder = BuilderConfig(name="%s-quick" % name,
                                slavenames=[name],
                                factory=factory,
                                category="quick",
                                locks=[locks[lock_name].access("exclusive")])
        c["builders"].append(builder)

        factory = create_factory(config, env=env, full=True)

        builder = BuilderConfig(name="%s-full" % name,
                                slavenames=[name],
                                factory=factory,
                                category="full",
                                locks=[locks[lock_name].access("exclusive")])

        c["builders"].append(builder)
