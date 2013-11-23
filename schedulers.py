from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.timed import Nightly
from buildbot.changes.filter import ChangeFilter

import repos


def setup(c, config):
    c["schedulers"] = []

    for branch in config["branches"]:
        def filter_fn(change):
            repo = repos.find_by_name(change.codebase, change.branch)
            if repo is None:
                return False

            return branch in repo.parent_branches

        change_filter = ChangeFilter(filter_fn=filter_fn)

        codebases = {"sugar-build": {"repository": config["repo"],
                                     "branch": branch},
                     "osbuild": {"repository":
                                 "https://github.com/dnarvaez/osbuild.git"}}

        for repo in repos.get_sub_repos():
            if branch in repo.parent_branches:
                codebases[repo.name] = {"repository": repo.url,
                                        "branch": repo.branch}

        scheduler = SingleBranchScheduler(name="quick-%s" % branch,
                                          codebases=codebases,
                                          change_filter=change_filter,
                                          builderNames=["quick"])
        c["schedulers"].append(scheduler)

        scheduler = Nightly(name="nightly-%s" % branch,
                            codebases=codebases,
                            branch=branch,
                            builderNames=["full"],
                            hour=2,
                            minute=0)
        c['schedulers'].append(scheduler)

    builderNames = ["quick", "full"]
    for arch in config["architectures"]:
        builderNames.append("broot-%s" % str(arch))

    scheduler = ForceScheduler(name="force",
                               codebases=["sugar-build"],
                               builderNames=builderNames)
    c['schedulers'].append(scheduler)
