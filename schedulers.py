from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.timed import Nightly
from buildbot.changes.filter import ChangeFilter

import repos


def setup(c, config):
    c["schedulers"] = []

    change_filter = ChangeFilter(project="sugar-build")
    slave_names = config["slaves"].keys()

    quick_builders = ["%s-quick" % name for name in slave_names]
    full_builders = ["%s-full" % name for name in slave_names]

    all_builders = []
    all_builders.extend(quick_builders)
    all_builders.extend(full_builders)

    codebases = {"sugar-build": {"repository": config["repo"]}}
    for repo in repos.get_sub_repos():
        codebases[repo.name] = {"repository": repo.url}

    scheduler = SingleBranchScheduler(name="quick",
                                      codebases=codebases,
                                      change_filter=change_filter,
                                      builderNames=quick_builders)
    c["schedulers"].append(scheduler)

    if config.get("nightly_builds", False):
        c['schedulers'].append(Nightly(name="nightly",
                                       codebases=codebases,
                                       branch=config.get("branch", "master"),
                                       builderNames=full_builders,
                                       hour=2,
                                       minute=0))

    c["schedulers"].append(ForceScheduler(name="force",
                                          codebases=codebases,
                                          builderNames=all_builders))
