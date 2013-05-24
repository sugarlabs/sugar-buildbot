import json


class Repo:
    def __init__(self, name, url, branch, tag):
        self.name = name
        self.url = url
        self.branch = branch
        self.tag = tag

        if self.branch is None and self.tag is None:
            self.branch = "master"


sub_repos = []


def get_by_url(url):
    for repo in sub_repos:
        if repo.url == url:
            return repo

        if url.startswith("https://github.com"):
            git_protocol_url = url.replace("https://", "git://") + ".git"
            if repo.url == git_protocol_url:
                return repo

    return None


def get_sub_repos():
    return sub_repos


def load_modules(path):
    for module in json.load(open(path)):
        if get_by_url(module["repo"]) is None:
            sub_repos.append(Repo(name=module["name"],
                                  url=module["repo"],
                                  branch=module.get("branch", None),
                                  tag=module.get("tag", None)))

load_modules("modules.json")
