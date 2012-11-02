from buildbot.changes.gitpoller import GitPoller

import repos

def setup(c, config):
    c["change_source"] = []

    for repo in repos.get_all(config):
        poller = GitPoller(repo.url,
                           project="sugar",
                           workdir="gitpoller_work/%s" % repo.name,
                           branch=repo.branch)
        c["change_source"].append(poller)
