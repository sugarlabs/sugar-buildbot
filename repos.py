class Repo:
    def __init__(self, name, path, branch="master"):
        self.name = name
        self.url = "git://git.sugarlabs.org/%s" % path
        self.branch = branch

main_repos = [Repo(name="sugar-build",
                   path="sugar-build/sugar-build.git"),
              Repo(name="gnome-3-6",
                   path="~dnarvaez/sugar-build/gnome-3-6.git")]

sub_repos = [Repo(name="sugar-fructose",
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

def get_by_name(name):
    repos = []
    repos.extend(main_repos)
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

def get_main_repos():
    return main_repos

def get_sub_repos():
    return sub_repos
