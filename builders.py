from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.config import BuilderConfig
from buildbot.locks import MasterLock
from buildbot.process.properties import WithProperties

import repos


def create_factory(config, env={}, full=False, distribute=False,
                   upload_docs=False, snapshot=False):
    factory = BuildFactory()

    factory.addStep(Git(repourl=config.repo,
                        branch=config.branch,
                        alwaysUseLatest=True))

    if config.check_system:
        command = ["make", "check-system", "ARGS=--update --remove"]
        factory.addStep(ShellCommand(command=command,
                                     description="checking system",
                                     descriptionDone="check system",
                                     warnOnFailure=True,
                                     env=env))

    factory.addStep(ShellCommand(command=["make", "pull"],
                                 description="pulling",
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
        factory.addStep(ShellCommand(command=["make", "docs-upload"],
                                     description="uploading docs",
                                     descriptionDone="upload docs",
                                     warnOnFailure=True,
                                     env=env))

    if snapshot:
        filename = WithProperties("SNAPSHOT_FILENAME=sugar-snapshot-%s-%s.tar",
                                  "buildername", "buildnumber")
        command = ["make", "snapshot-upload", filename]

        factory.addStep(ShellCommand(command=command,
                                     description="uploading snapshot",
                                     descriptionDone="upload snapshot",
                                     warnOnFailure=True,
                                     env=env))
    return factory


def setup(c, config):
    c["builders"] = []

    bender_lock = MasterLock("bender")

    for name, info in config.slaves.items():
        env = {"SUGAR_BUILDBOT": name}

        factory = create_factory(config, env=env, distribute=True,
                                 upload_docs=info.get("upload_docs", False))

        builder = BuilderConfig(name="%s-quick" % name,
                                slavenames=name,
                                factory=factory,
                                category="quick",
                                locks=[bender_lock.access("exclusive")])
        c["builders"].append(builder)

        factory = create_factory(config, env=env, full=True, snapshot=True)

        builder = BuilderConfig(name="%s-full" % name,
                                slavenames=name,
                                factory=factory,
                                category="full",
                                locks=[bender_lock.access("exclusive")])

        c["builders"].append(builder)
