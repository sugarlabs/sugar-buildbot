class Repo:
    def __init__(self, name, path, branch="master"):
        self.name = name
        self.url = "git://git.sugarlabs.org/%s" % path
        self.branch = branch

repos = [Repo(name="sugar-fructose",
              path="sugar-fructose/sugar-fructose.git"),
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
	          path="sugar-toolkit-gtk3/sugar-toolkit-gtk3.git"),
         Repo(name="terminal",
              path="terminal/mainline.git",
              branch="gtk3"),
         Repo(name="chat",
              path="chat/mainline.git",
              branch="gtk3"),
         Repo(name="read",
              path="read/mainline.git"),
         Repo(name="calculate",
              path="calculate/mainline.git"),
         Repo(name="log",
              path="log/mainline.git"),
         Repo(name="write",
              path="write/mainline.git"),
         Repo(name="pippy",
              path="pippy/mainline.git",
              branch="gtk3"),
         Repo(name="imageviewer",
              path="imageviewer/mainline.git"),
         Repo(name="jukebox",
              path="jukebox/mainline.git"),
         Repo(name="turtleart",
              path="turtleart/mainline.git"),
         Repo(name="browse",
              path="browse/mainline.git")]

def get_by_name(config, name):
    for repo in get_all(config):
        if repo.name == name:
            return repo

    return None

def get_url(config, name):
    repo = get_by_name(config, name)
    if repo:
        return repo.url
    else:
        return None

def get_all(config):
    path = config.get("repo_path", "sugar-build/sugar-build.git")

    all_repos = repos[:]
    all_repos.append(Repo(name="sugar-build", path=path))

    return all_repos
