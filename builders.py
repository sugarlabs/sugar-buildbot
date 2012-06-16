from buildbot.process.factory import BuildFactory
from buildbot.steps.source import Git
from buildbot.steps.shell import Compile
from buildbot.config import BuilderConfig

def setup(c, slaves_config):
    factory = BuildFactory()
    factory.addStep(Git(repourl="git://github.com/dnarvaez/sugar-build",
                        mode="copy"))
    factory.addStep(Compile(command=["make", "build"],
                            env={"SUGAR_BUILDBOT": "yes"}))

    c["builders"] = []
    c["builders"].append(BuilderConfig(name="build",
                                       slavenames=slaves_config.keys(),
                                       factory=factory))

