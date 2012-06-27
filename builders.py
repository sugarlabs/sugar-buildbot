from buildbot.process.factory import BuildFactory
from buildbot.steps.source import Git
from buildbot.steps.shell import Compile
from buildbot.config import BuilderConfig

import repos

def setup(c, config):
    env={"SUGAR_BUILDBOT": "yes"}

    factory = BuildFactory()
    factory.addStep(Git(repourl=repos.get_url("sugar-build"),
                        method="incremental", alwaysUseLatest=True))
    factory.addStep(Compile(command=["make", "clean"], env=env))
    factory.addStep(Compile(command=["make", "build"], env=env))

    c["builders"] = []

    for slave in config["slaves"].keys():
        c["builders"].append(BuilderConfig(name=slave,
                                           slavenames=slave,
                                           factory=factory))

