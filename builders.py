from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.config import BuilderConfig
from buildbot.locks import MasterLock

import repos

def create_factory(slave_config):
    env={"SUGAR_BUILDBOT": "yes"}

    factory = BuildFactory()

    repourl = repos.get_url(slave_config.get("repo", "sugar-build"))

    factory.addStep(Git(repourl=repourl,
                        branch="master",
                        alwaysUseLatest=True))
    factory.addStep(ShellCommand(command=["make", "clean"],
                                 description="cleaning",
                                 descriptionDone="clean",
                                 env=env))
    factory.addStep(ShellCommand(command=["make", "build-glucose"],
                                 description="building glucose",
                                 descriptionDone="build glucose",
                                 env=env))
    factory.addStep(ShellCommand(command=["make", "build-fructose"],
                                 description="building fructose",
                                 descriptionDone="build fructose",
                                 env=env))

    if slave_config.get("run_tests", False):
        factory.addStep(ShellCommand(command=["make", "test"],
                                     description="testing",
                                     descriptionDone="test",
                                     logfiles={"testlogs": "logs/test.log"},
                                     env=env))

    return factory

def setup(c, config):
    c["builders"] = []

    bender_lock = MasterLock("bender")

    for name, info in config["slaves"].items():
        factory = create_factory(info)

        if info.get("run_tests", False):
            category = "testing"
        else:
            category = "stable"

        builder = BuilderConfig(name=name,
                                slavenames=name,
                                factory=factory,
                                category=category,
                                locks=[bender_lock.access("exclusive")])
        c["builders"].append(builder)

