from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.timed import Nightly
from buildbot.changes.filter import ChangeFilter

import repos


def create_filter_fn(branch):
    def filter_fn(change):
        repo = repos.find_by_name(change.codebase, change.branch)
        if repo is None:
            return False

        return branch in repo.parent_branches

    return filter_fn


def setup(c, config):
    c["schedulers"] = []

    for branch in config["branches"]:
        codebases = {}

        change_filter = ChangeFilter(filter_fn=create_filter_fn(branch))

        for repo in repos.get_all():
            if branch in repo.parent_branches:
                codebases[repo.name] = {"repository": repo.url,
                                        "branch": repo.branch}

        scheduler = SingleBranchScheduler(name="quick-%s" % branch,
                                          codebases=codebases,
                                          change_filter=change_filter,
                                          builderNames=["quick-%s" % branch])
        c["schedulers"].append(scheduler)

        scheduler = Nightly(name="nightly-%s" % branch,
                            codebases=codebases,
                            branch=branch,
                            builderNames=["full-%s" % branch],
                            hour=12,
                            minute=0)
        c['schedulers'].append(scheduler)

    builders = []
    broot_builders = []

    for branch in config["branches"]:
        builders.extend(["quick-%s" % str(branch), "full-%s" % str(branch)])
        for arch in config["architectures"]:
            broot_builders.append("broot-%s-%s" % (str(arch), str(branch)))

    all_builders = builders[:]
    all_builders.extend(broot_builders)

    scheduler = Nightly(name="broot-nightly",
                        branch=branch,
                        builderNames=broot_builders,
                        hour=0,
                        minute=0,
                        dayOfWeek=0)
    c['schedulers'].append(scheduler)

    scheduler = ForceScheduler(name="force",
                               codebases=["sugar-build"],
                               builderNames=all_builders)
    c['schedulers'].append(scheduler)
