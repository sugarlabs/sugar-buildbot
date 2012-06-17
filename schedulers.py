from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.timed import Periodic
from buildbot.changes import filter

def setup(c, config):
    c["schedulers"] = []

    change_filter = filter.ChangeFilter(project="sugar")
    c["schedulers"].append(SingleBranchScheduler(name="all",
                                                 change_filter=change_filter,
                                                 builderNames=["build"]))

    c["schedulers"].append(Periodic(name="daily",
                                    builderNames=["build"],
                                    periodicBuildTimer=24*60*60))

    c["schedulers"].append(ForceScheduler(name="force",
                                          builderNames=["build"]))


