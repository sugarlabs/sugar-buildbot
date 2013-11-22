from buildbot.changes.gitpoller import GitPoller

import repos


def setup(c, config):
    c["change_source"] = []

    pollinterval = 300

    if config.get("sub_repos_changes", True):
        for repo in repos.get_sub_repos():
            skip = False
            for repo_prefix in ["git://github.com/dnarvaez",
                                "git://github.com/sugarlabs"]:
                if repo.url.startswith(repo_prefix):
                    skip = True

            if not skip and repo.branch:
                poller = GitPoller(repo.url,
                                   project="sugar-build",
                                   branches=[repo.branch],
                                   pollinterval=pollinterval)
                c["change_source"].append(poller)

    def codebaseGenerator(change_dict):
        repository = change_dict["repository"]
        branch = change_dict["branch"]

        repo_name = repository.split("/")[-1]
        if repo_name in ["sugar-build", "osbuild"]:
            return repo_name
        else:
            return repos.find(repository, branch).name

    c["codebaseGenerator"] = codebaseGenerator
