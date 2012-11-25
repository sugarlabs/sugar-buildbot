from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.config import BuilderConfig
from buildbot.locks import MasterLock
from buildbot.process.properties import WithProperties

import repos

def create_factory(slave_name, slave_config):
    env={"SUGAR_BUILDBOT": "yes"}

    factory = BuildFactory()

    repourl = repos.get_url(slave_config.get("repo", "sugar-build"))

    factory.addStep(Git(repourl=repourl,
                        branch="master",
                        alwaysUseLatest=True))

    command = ["make", "check-system", "ARGS=--udpate --remove"]
    factory.addStep(ShellCommand(command=["make", "check-system"],
                                 description="checking system",
                                 descriptionDone="check system",
                                 warnOnFailure=True,
                                 env=check_system_env))

    factory.addStep(ShellCommand(command=["make", "clean"],
                                 description="cleaning",
                                 descriptionDone="clean",
                                 haltOnFailure=True,
                                 env=env))
    factory.addStep(ShellCommand(command=["make", "build"],
                                 description="building",
                                 descriptionDone="build",
                                 haltOnFailure=True,
                                 env=env))

    if slave_config.get("run_tests", True):
        factory.addStep(ShellCommand(command=["make", "test"],
                                     description="testing",
                                     descriptionDone="test",
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

        if info.get("run_tests", True):
            category = "testing"
        else:
            category = "stable"

        builder = BuilderConfig(name=name,
                                slavenames=name,
                                factory=factory,
                                category=category,
                                locks=[bender_lock.access("exclusive")])
        c["builders"].append(builder)

