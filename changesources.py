from buildbot.changes.gitpoller import GitPoller

import repos


def setup(c, config):
    c["change_source"] = []

    category = "production"

    main_repo = repos.get_main_repo()
    poller = GitPoller(main_repo.url,
                       project=main_repo.name,
                       category=category,
                       branches=[main_repo.branch],
                       pollinterval=60)
    c["change_source"].append(poller)

    for repo in repos.get_sub_repos():
        poller = GitPoller(repo.url,
                           project=main_repo.name,
                           category=category,
                           branches=[repo.branch],
                           pollinterval=60)
        c["change_source"].append(poller)
