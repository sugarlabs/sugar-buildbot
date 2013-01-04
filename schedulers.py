from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.timed import Nightly
from buildbot.changes.filter import ChangeFilter

import repos


def setup(c, config):
    c["schedulers"] = []

    main_repo = repos.get_main_repo()

    project_filter = ChangeFilter(project=main_repo.name)

    slave_names = config.slaves.keys()

    quick_builders = ["%s-quick" % name for name in slave_names]
    full_builders = ["%s-full" % name for name in slave_names]

    all_builders = []
    all_builders.extend(quick_builders)
    all_builders.extend(full_builders)

    scheduler = SingleBranchScheduler(name="%s-quick" % main_repo.name,
                                      change_filter=project_filter,
                                      builderNames=quick_builders)
    c["schedulers"].append(scheduler)

    c['schedulers'].append(Nightly(name="nightly",
                                   branch="master",
                                   builderNames=full_builders,
                                   hour=2,
                                   minute=0))

    c["schedulers"].append(ForceScheduler(name="force",
                                          builderNames=all_builders))
