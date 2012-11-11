from buildbot.changes.gitpoller import GitPoller

import repos

def setup(c, config):
    c["change_source"] = []

    repo = repos.get_main_repo()
    poller = GitPoller(repo.url,
                       project=repo.name,
                       workdir="gitpoller_work/%s" % repo.name,
                       branch=repo.branch)
    c["change_source"].append(poller)

    for repo in repos.get_sub_repos():
        poller = GitPoller(repo.url,
                           project=repo.name,
                           workdir="gitpoller_work/%s" % repo.name,
                           branch=repo.branch)
        c["change_source"].append(poller)
