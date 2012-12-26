from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.timed import Nightly, Periodic
from buildbot.changes import filter

import repos


def setup(c, config):
    c["schedulers"] = []

    main_repo = repos.get_main_repo()
    change_filter = filter.ChangeFilter(project=main_repo.name)

    builder_names = config["slaves"].keys()

    scheduler = SingleBranchScheduler(name="all-%s" % main_repo.name,
                                      change_filter=change_filter,
                                      builderNames=builder_names)
    c["schedulers"].append(scheduler)

    c['schedulers'].append(Nightly(name="nightly",
                                   branch="master",
                                   builderNames=builder_names,
                                   hour=2,
                                   minute=0,
                                   properties={"build_args": "--full"}))

    force_builder_names = ["%s-testing" % name for name in builder_names]
    force_builder_names.extend(builder_names)

    c["schedulers"].append(ForceScheduler(name="force",
                                          builderNames=force_builder_names,
                                          properties=[]))
