from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.timed import Nightly
from buildbot.changes import filter

def setup(c, config):
    c["schedulers"] = []

    change_filter = filter.ChangeFilter(project="sugar")
    builder_names = config["slaves"].keys()

    c["schedulers"].append(SingleBranchScheduler(name="all",
                                                 change_filter=change_filter,
                                                 builderNames=builder_names))

    c['schedulers'].append(Nightly(name="nightly",
                                   branch="master"
                                   builderNames=builder_names,
                                   hour=2,
                                   minute=0))

    c["schedulers"].append(ForceScheduler(name="force",
                                          builderNames=builder_names))


