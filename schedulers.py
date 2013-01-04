from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.timed import Nightly

import repos


def setup(c, config):
    c["schedulers"] = []

    slave_names = config.slaves.keys()

    quick_builders = ["%s-quick" % name for name in slave_names]
    full_builders = ["%s-full" % name for name in slave_names]

    all_builders = []
    all_builders.extend(quick_builders)
    all_builders.extend(full_builders)

    scheduler = SingleBranchScheduler(name="quick",
                                      builderNames=quick_builders)
    c["schedulers"].append(scheduler)

    if config.nightly_builds:
        c['schedulers'].append(Nightly(name="nightly",
                                       branch=config.branch,
                                       builderNames=full_builders,
                                       hour=2,
                                       minute=0))

    c["schedulers"].append(ForceScheduler(name="force",
                                          builderNames=all_builders))
