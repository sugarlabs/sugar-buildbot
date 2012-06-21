from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.timed import Periodic
from buildbot.changes import filter

def setup(c, config):
    c["schedulers"] = []

    change_filter = filter.ChangeFilter(project="sugar")
    builder_names = config["slaves"].keys()

    c["schedulers"].append(SingleBranchScheduler(name="all",
                                                 change_filter=change_filter,
                                                 builderNames=builder_names))

    c["schedulers"].append(Periodic(name="daily",
                                    builderNames=builder_names,
                                    periodicBuildTimer=24*60*60))

    c["schedulers"].append(ForceScheduler(name="force",
                                          builderNames=builder_names))


