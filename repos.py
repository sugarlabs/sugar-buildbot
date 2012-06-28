class Repo:
    def __init__(self, name, path):
        self.name = name
        self.url = "git://git.sugarlabs.org/%s" % path

repos = [Repo(name="sugar-build",
              path="sugar-build/sugar-build.git"),
         Repo(name="sugar",
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
	          path="sugar-toolkit-gtk3/sugar-toolkit-gtk3.git")]

def get_by_name(name):
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

def get_all():
    return repos
