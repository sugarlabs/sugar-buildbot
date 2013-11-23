import json


class Repo:
    def __init__(self, name, url, branch="master"):
        self.parent_branches = []
        self.name = name
        self.url = url
        self.branch = branch


all_repos = None


def find_by_name(name, branch):
    for repo in all_repos:
        if repo.name == name and repo.branch == branch:
            return repo

    return None


def find_by_url(url, branch):
    for repo in all_repos:
        if url.startswith("https://github.com"):
            canonicalized_url = url.replace("https://", "git://")

            if not canonicalized_url.endswith(".git"):
                canonicalized_url = canonicalized_url + ".git"
        else:
            canonicalized_url = url

        if repo.url == canonicalized_url and repo.branch == branch:
            return repo

    return None


def get_all():
    return all_repos


def setup(config):
    all_repos = [Repo("sugar-build", config["repo"]),
                 Repo("osbuild", "https://github.com/dnarvaez/osbuild.git"),
                 Repo("broot", "https://github.com/dnarvaez/broot.git")]

    for branch in config["branches"]:
        for module in json.load(open("modules-%s.json" % branch)):
            if "tag" in module:
                continue

            module_branch = module.get("branch", "master")

            repo = find_by_url(module["repo"], module_branch)
            if repo is None:
                repo = Repo(module["name"], module["repo"], module_branch)
                all_repos.append(repo)

            repo.parent_branches.append(branch)
