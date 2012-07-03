from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.config import BuilderConfig
from buildbot.locks import MasterLock

import repos

def create_factory(run_tests=True):
    env={"SUGAR_BUILDBOT": "yes"}

    factory = BuildFactory()

    factory.addStep(Git(repourl=repos.get_url("sugar-build"),
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

    if with_tests:
        factory.addStep(ShellCommand(command=["make", "test"],
                                     description="testing",
                                     descriptionDone="test",
                                     env=env))

    return factory

def setup(c, config):
    factory_build_only = create_factory(run_tests=False)
    factory_run_tests = create_factory(run_tests=True)

    c["builders"] = []

    bender_lock = MasterLock("bender")

    for name, info in config["slaves"].items():
        if info.get("run_tests", False):
            factory = factory_run_tests
        else:
            factory = factory_build_only

        builder = BuilderConfig(name=name,
                                slavenames=name,
                                factory=factory,
                                locks=[bender_lock.access("exclusive")])
        c["builders"].append(builder)

