from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.timed import Nightly
from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.changes.filter import ChangeFilter


def setup(c, config):
    c["schedulers"] = []

    for branch in config["branches"]:
        change_filter = ChangeFilter(project="sugar-build")
        scheduler = SingleBranchScheduler(name="quick-%s" % branch,
                                          change_filter=change_filter,
                                          builderNames=["quick-%s" % branch])
        c["schedulers"].append(scheduler)

        scheduler = Nightly(name="quick-%s" % branch,
                            branch=branch,
                            builderNames=["quick-%s" % branch],
                            hour=range(0, 24, 3))
        c["schedulers"].append(scheduler)

        scheduler = Nightly(name="nightly-%s" % branch,
                            branch=branch,
                            builderNames=["full-%s" % branch],
                            hour=12,
                            minute=0)
        c['schedulers'].append(scheduler)

        builders = []
        broot_builders = []

        builders.extend(["quick-%s" % str(branch), "full-%s" % str(branch)])
        for arch in config["architectures"]:
            broot_builders.append("broot-%s-%s" % (str(arch), str(branch)))

        all_builders = builders[:]
        all_builders.extend(broot_builders)

        scheduler = Nightly(name="broot-nightly-%s" % branch,
                            branch=branch,
                            builderNames=broot_builders,
                            hour=0,
                            minute=0,
                            dayOfWeek=0)
        c['schedulers'].append(scheduler)

        scheduler = ForceScheduler(name="force-%s" % str(branch),
                                   builderNames=all_builders)
        c['schedulers'].append(scheduler)
