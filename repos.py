import json


class Repo:
    def __init__(self, name, url, branch):
        self.parent_branches = []
        self.name = name
        self.url = url
        self.branch = branch


sub_repos = []


def find_by_name(name, branch):
    for repo in sub_repos:
        if repo.name == name and repo.branch == branch:
            return repo

    return None


def find_by_url(url, branch):
    for repo in sub_repos:
        if url.startswith("https://github.com"):
            canonicalized_url = url.replace("https://", "git://")

            if not canonicalized_url.endswith(".git"):
                canonicalized_url = canonicalized_url + ".git"
        else:
            canonicalized_url = url

        if repo.url == canonicalized_url and repo.branch == branch:
            return repo

    return None


def get_sub_repos():
    return sub_repos


def load(config):
    for branch in config["branches"]:
        for module in json.load(open("modules-%s.json" % branch)):
            if "tag" in module:
                continue

            module_branch = module.get("branch", "master")

            repo = find_by_url(module["repo"], module_branch)
            if repo is None:
                repo = Repo(module["name"], module["repo"], module_branch)
                sub_repos.append(repo)

            repo.parent_branches.append(branch)
