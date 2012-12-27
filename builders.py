from buildbot.process.factory import BuildFactory
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.config import BuilderConfig
from buildbot.locks import MasterLock
from buildbot.process.properties import WithProperties
from buildbot.process.properties import Interpolate
from buildbot.status.results import SKIPPED

import repos


def should_snapshot(step):
    return step.build.getProperties().get("snapshot", False)


def step_skipped(step, results):
    return results != SKIPPED


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

    factory.addStep(ShellCommand(command=["make", "pull"],
                                 description="pulling",
                                 descriptionDone="pull",
                                 haltOnFailure=True,
                                 logfiles={"log": "logs/pull.log"},
                                 env=env))

    interpolate = Interpolate("ARGS=%(prop:build_args)s")
    factory.addStep(ShellCommand(command=["make", "build", interpolate],
                                 description="building",
                                 descriptionDone="build",
                                 haltOnFailure=True,
                                 logfiles={"log": "logs/build.log"},
                                 env=env))

    factory.addStep(ShellCommand(command=["make", "check"],
                                 description="testing",
                                 descriptionDone="test",
                                 haltOnFailure=True,
                                 logfiles={"log": "logs/test.log"},
                                 env=env))

    return factory


def add_upload_steps(factory, env, slave_config):
    if slave_config.get("distribute", False):
        factory.addStep(ShellCommand(command=["make", "distribute"],
                                     description="distributing",
                                     descriptionDone="distribute",
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
                                 doStepIf=should_snapshot,
                                 hideStepIf=step_skipped,
                                 env=env))


def setup(c, config):
    c["builders"] = []

    bender_lock = MasterLock("bender")

    for name, info in config["slaves"].items():
        env = {"SUGAR_BUILDBOT": name}

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
                                category="testing",
                                locks=[bender_lock.access("exclusive")])

        c["builders"].append(builder)
