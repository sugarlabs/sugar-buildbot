from buildbot.changes.gitpoller import GitPoller

import repos

def setup(c, config):
    c["change_source"] = []

    for main_repo in repos.get_main_repos():
        all_repos = [main_repo]
        all_repos.extend(repos.get_sub_repos())

        for repo in all_repos:
            workdir = "gitpoller_work/%s/%s" % (main_repo.name, repo.name)
            poller = GitPoller(repo.url,
                               project=main_repo.main,
                               workdir=workdir
                               branch=repo.branch)
            c["change_source"].append(poller)
