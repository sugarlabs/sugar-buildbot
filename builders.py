from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.config import BuilderConfig
from buildbot.locks import MasterLock
from buildbot.process.properties import WithProperties

import repos

def create_factory(slave_name, slave_config):
    env={"SUGAR_BUILDBOT": slave_name}

    factory = BuildFactory()

    repourl = repos.get_url(slave_config.get("repo", "sugar-build"))

    factory.addStep(Git(repourl=repourl,
                        branch="master",
                        alwaysUseLatest=True))

    command = ["make", "check-system", "ARGS=--update --remove"]
    factory.addStep(ShellCommand(command=command,
                                 description="checking system",
                                 descriptionDone="check system",
                                 warnOnFailure=True,
                                 env=env))

    factory.addStep(ShellCommand(command=["make", "clean"],
                                 description="cleaning",
                                 descriptionDone="clean",
                                 haltOnFailure=True,
                                 env=env))
    factory.addStep(ShellCommand(command=["make", "pull"],
                                 description="pulling",
                                 descriptionDone="pull",
                                 haltOnFailure=True,
                                 env=env)) 
    factory.addStep(ShellCommand(command=["make", "build"],
                                 description="building",
                                 descriptionDone="build",
                                 haltOnFailure=True,
                                 env=env))

    factory.addStep(ShellCommand(command=["make", "check"],
                                 description="testing",
                                 descriptionDone="test",
                                 haltOnFailure=True,
                                 logfiles={"testlogs": "logs/test.log"},
                                 env=env))

    if slave_config.get("upload_docs", False):
        factory.addStep(ShellCommand(command=["make", "docs-upload"],
                                     description="uploading docs",
                                     descriptionDone="upload docs",
                                     warnOnFailure=True,
                                     env=env))

    filename = WithProperties("SNAPSHOT_FILENAME=sugar-snapshot-%s-%s.tar",
                              "buildername", "buildnumber")

    factory.addStep(ShellCommand(command=["make", "snapshot-upload", filename],
                                 description="uploading snapshot",
                                 descriptionDone="upload snapshot",
                                 warnOnFailure=True,
                                 env=env))

    return factory

def setup(c, config):
    c["builders"] = []

    bender_lock = MasterLock("bender")

    for name, info in config["slaves"].items():
        factory = create_factory(name, info)

        builder = BuilderConfig(name=name,
                                slavenames=name,
                                factory=factory,
                                locks=[bender_lock.access("exclusive")])
        c["builders"].append(builder)

