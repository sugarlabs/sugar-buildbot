from buildbot.changes.gitpoller import GitPoller

import repos


def setup(c, config):
    c["change_source"] = []

    pollinterval = 60

    poller = GitPoller(config.repo,
                       branches=[config.branch],
                       pollinterval=pollinterval)
    c["change_source"].append(poller)

    if config.sub_repos_changes:
        for repo in repos.get_sub_repos():
            poller = GitPoller(repo.url,
                               branches=[repo.branch],
                               pollinterval=pollinterval)
            c["change_source"].append(poller)
