from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.config import BuilderConfig
from buildbot.locks import MasterLock
from buildbot.process.properties import WithProperties

import repos

def create_factory(env, slave_config, branch):
    factory = BuildFactory()

    repourl = repos.get_url(slave_config.get("repo", "sugar-build"))

    factory.addStep(Git(repourl=repourl,
                        branch=branch,
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

    return factory

def add_upload_steps(factory, env, slave_config):
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

def setup(c, config):
    c["builders"] = []

    bender_lock = MasterLock("bender")

    for name, info in config["slaves"].items(): 
        env={"SUGAR_BUILDBOT": name}

        factory = create_factory(env, info, "master")
        add_upload_steps(factory, env, info)

        builder = BuilderConfig(name=name,
                                slavenames=name,
                                factory=factory,
                                category="production",
                                locks=[bender_lock.access("exclusive")])
        c["builders"].append(builder)

        factory = create_factory(env, info, "testing")

        builder = BuilderConfig(name="%s-testing" % name,
                                slavenames=name,
                                factory=factory,
                                category="testing")

        c["builders"].append(builder)

