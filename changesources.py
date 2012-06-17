from buildbot.changes.gitpoller import GitPoller

repos = {"sugar": "sugar/mainline.git",
         "sugar-base": "sugar-base/mainline.git",
         "sugar-toolkit": "sugar-toolkit/mainline.git",
         "sugar-datastore": "sugar-datastore/mainline.git",
         "sugar-artwork": "sugar-artwork/mainline.git",
         "sugar-toolkit-gtk3": "sugar-toolkit-gtk3/sugar-toolkit-gtk3.git",
         "web": "web/mainline.git",
         "terminal": "terminal/mainline.git"}

def setup(c, config):
    c["change_source"] = []

    for name, path in repos.items():
        poller = GitPoller("git://git.sugarlabs.org/%s" % path,
                           project="sugar",
                           workdir="gitpoller_work/%s" % name)
        c["change_source"].append(poller)

    poller = GitPoller("git://github.com/dnarvaez/sugar-build",
                       project="sugar",
                       workdir="gitpoller_work/sugar-build")
    c["change_source"].append(poller)

