from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.timed import Nightly, Periodic
from buildbot.changes import filter

import repos

def setup(c, config):
    c["schedulers"] = []

    for main_repo in repos.get_main_repos():
        change_filter = filter.ChangeFilter(project=main_repo.name)
        
        builder_names = []
        for key, info in config["slaves"].items():
            if info.get("repo", "sugar-build") == main_repo.name:
                builder_names.append(key)

        scheduler = SingleBranchScheduler(name="all-%s" % main_repo.name,
                                          change_filter=change_filter,
                                          builderNames=builder_names)
        c["schedulers"].append(scheduler)

    builder_names = config["slaves"].keys()
    c['schedulers'].append(Nightly(name="nightly",
                                   branch="master",
                                   builderNames=builder_names,
                                   hour=2,
                                   minute=0))

    periodicSchedulers = {}
    for name, slave in config["slaves"].items():
        if "periodic_build" in slave:
            timer = slave["periodic_build"]
            if timer in periodicSchedulers:
                periodicSchedulers[timer].append(name)
            else:
                periodicSchedulers[timer] = [name]

    for timer, builderNames in periodicSchedulers.items():
        c["schedulers"].append(Periodic(name="periodic-%d" % timer,
                                        builderNames=builderNames,
                                        periodicBuildTimer=timer))

    c["schedulers"].append(ForceScheduler(name="force",
                                          builderNames=builder_names,
                                          properties=[]))


