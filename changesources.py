from buildbot.changes.gitpoller import GitPoller

import repos


def setup(c, config):
    c["change_source"] = []

    pollinterval = 900

    for repo in repos.get_all():
        poller = GitPoller(repo.url,
                           project="sugar-build",
                           branches=[repo.branch],
                           pollinterval=pollinterval)
        c["change_source"].append(poller)

    def codebaseGenerator(change_dict):
        repository = change_dict["repository"]
        branch = change_dict["branch"]
        return repos.find_by_url(repository, branch).name

    c["codebaseGenerator"] = codebaseGenerator
