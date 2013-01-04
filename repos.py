import json


class Repo:
    def __init__(self, name, url, branch=None):
        self.name = name
        self.url = url
        self.branch = branch

        if self.branch is None:
            self.branch = "master"


sub_repos = []


def get_by_name(name):
    for repo in sub_repos:
        if repo.name == name:
            return repo

    return None


def get_url(name):
    repo = get_by_name(name)
    if repo:
        return repo.url
    else:
        return None


def get_sub_repos():
    return sub_repos


def load_modules(path):
    for module in json.load(open(path)):
        sub_repos.append(Repo(name=module["name"],
                              url=module["repo"],
                              branch=module.get("branch", None)))

load_modules("modules/sugar.json")
load_modules("modules/activities.json")
