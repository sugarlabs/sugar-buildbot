from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.config import BuilderConfig

import repos

def setup(c, config):
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
    factory.addStep(ShellCommand(command=["make", "test"],
                                 description="testing",
                                 descriptionDone="test",
                                 env=env))

    c["builders"] = []

    for slave in config["slaves"].keys():
        c["builders"].append(BuilderConfig(name=slave,
                                           slavenames=slave,
                                           factory=factory))

