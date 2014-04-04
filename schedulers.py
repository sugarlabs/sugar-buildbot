from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.timed import Nightly
from buildbot.schedulers.timed import Periodic
from buildbot.schedulers.forcesched import CodebaseParameter
from buildbot.schedulers.forcesched import StringParameter

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

        for repo in repos.get_all():
            if branch in repo.parent_branches:
                codebases[repo.name] = {"repository": repo.url,
                                        "branch": repo.branch}

        scheduler = Periodic(name="quick-%s" % branch,
                             codebases=codebases,
                             builderNames=["quick-%s" % branch],
                             periodicBuildTimer=3 * 60 * 60)
        c["schedulers"].append(scheduler)

        scheduler = Nightly(name="nightly-%s" % branch,
                            branch=branch,
                            codebases=codebases,
                            builderNames=["full-%s" % branch],
                            hour=12,
                            minute=0)
        c['schedulers'].append(scheduler)

        builders = []
        broot_builders = []

        builders.extend(["quick-%s" % str(branch), "full-%s" % str(branch)])
        for arch in config["architectures"]:
            broot_builders.append("broot-%s-%s" % (str(arch), str(branch)))

        all_builders = builders[:]
        all_builders.extend(broot_builders)

        codebases = {"sugar-build": {"repository": config["repo"],
                                     "branch": branch}}

        scheduler = Nightly(name="broot-nightly-%s" % branch,
                            branch=branch,
                            builderNames=broot_builders,
                            codebases=codebases,
                            hour=0,
                            minute=0,
                            dayOfWeek=0)
        c['schedulers'].append(scheduler)

        branch_parameter = StringParameter(name="branch",
                                           label="Branch:",
                                           default=branch)

        codebases = [CodebaseParameter(codebase="sugar-build",
                                       branch=branch_parameter)]

        scheduler = ForceScheduler(name="force-%s" % str(branch),
                                   codebases=codebases,
                                   builderNames=all_builders)
        c['schedulers'].append(scheduler)
