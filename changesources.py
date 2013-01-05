from buildbot.changes.gitpoller import GitPoller

import repos


def setup(c, config):
    c["change_source"] = []

    pollinterval = 60

    poller = GitPoller(config.repo,
                       project="sugar-build",
                       branches=[config.branch],
                       pollinterval=pollinterval)
    c["change_source"].append(poller)

    if config.sub_repos_changes:
        for repo in repos.get_sub_repos():
            poller = GitPoller(repo.url,
                               project="sugar-build",
                               branches=[repo.branch],
                               pollinterval=pollinterval)
            c["change_source"].append(poller)

    def codebaseGenerator(change_dict):
        repository = change_dict["repository"]

        if repository == config.repo:
            return "sugar-build"
        else:
            return repos.get_by_url(repository)

    c["codebaseGenerator"] = codebaseGenerator
