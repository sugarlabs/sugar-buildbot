from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.changes import filter

def setup(c):
    c["schedulers"] = []

    change_filter = filter.ChangeFilter(project="sugar")
    c["schedulers"].append(SingleBranchScheduler(name="all",
                                                 change_filter=change_filter,
                                                 builderNames=["build"]))
    c["schedulers"].append(ForceScheduler(name="force",
                                          builderNames=["build"]))


