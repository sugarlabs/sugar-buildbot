from buildbot.process.factory import BuildFactory
from buildbot.steps.source import Git
from buildbot.steps.shell import Compile
from buildbot.config import BuilderConfig

import repos

def setup(c, config):
    factory = BuildFactory()
    factory.addStep(Git(repourl=repos.get_url("sugar-build"),
                        mode="copy", alwaysUseLatest=True))
    factory.addStep(Compile(command=["make", "build"],
                            env={"SUGAR_BUILDBOT": "yes"}))

    c["builders"] = []
    c["builders"].append(BuilderConfig(name="build",
                                       slavenames=config["slaves"].keys(),
                                       factory=factory))

