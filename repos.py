class Repo:
    def __init__(self, name, path, branch="master"):
        self.name = name
        self.url = "git://git.sugarlabs.org/%s" % path
        self.branch = branch

main_repo = Repo(name="sugar-build",
                 path="sugar-build/sugar-build.git")

sub_repos = [Repo(name="sugar",
                  path="sugar/mainline.git"),
             Repo(name="sugar-base",
                  path="sugar-base/mainline.git"),
             Repo(name="sugar-toolkit",
                  path="sugar-toolkit/mainline.git"),
             Repo(name="sugar-datastore",
                  path="sugar-datastore/mainline.git"),
             Repo(name="sugar-artwork",
                  path="sugar-artwork/mainline.git"),
             Repo(name="sugar-toolkit-gtk3",
	          path="sugar-toolkit-gtk3/sugar-toolkit-gtk3.git"),
             Repo(name="chat",
                  path="chat/mainline.git",
                  branch="gtk3"),
             Repo(name="browse",
                  path="browse/mainline.git")]

def get_by_name(name):
    repos = [main_repo]
    repos.extend(sub_repos)

    for repo in repos:
        if repo.name == name:
            return repo

    return None

def get_url(name):
    repo = get_by_name(name)
    if repo:
        return repo.url
    else:
        return None

def get_main_repo():
    return main_repo

def get_sub_repos():
    return sub_repos
