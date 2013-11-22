from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.timed import Nightly
from buildbot.changes.filter import ChangeFilter

import repos


def setup(c, config):
    c["schedulers"] = []

    change_filter = ChangeFilter(project="sugar-build")

    codebases = {"sugar-build": {"repository": config["repo"],
                                 "branch": config["branch"]},
                 "osbuild": {"repository":
                             "https://github.com/dnarvaez/osbuild.git",
                             "branch": config["branch"]}}

    for repo in repos.get_sub_repos():
        codebases[repo.name] = {"repository": repo.url,
                                "branch": repo.branch}

    scheduler = SingleBranchScheduler(name="quick",
                                      codebases=codebases,
                                      change_filter=change_filter,
                                      builderNames=["quick"])
    c["schedulers"].append(scheduler)

    for branch in config["branches"]:
        scheduler = Nightly(name="nightly-%s" % branch,
                            codebases=codebases,
                            branch=branch,
                            builderNames=["full"],
                            hour=2,
                            minute=0)
        c['schedulers'].append(scheduler)

    builderNames = ["quick", "full"]
    for arch in config["architectures"]:
        builderNames.append("broot-%s" % arch)

    scheduler = ForceScheduler(name="force",
                               codebases=["sugar-build"],
                               builderNames=builderNames)
    c['schedulers'].append(scheduler)
