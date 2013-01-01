from buildbot.changes.gitpoller import GitPoller

import repos


def setup(c):
    c["change_source"] = []

    main_repo = repos.get_main_repo()

    poller = GitPoller(main_repo.url,
                       project=main_repo.name,
                       branches=[main_repo.branch],
                       pollinterval=60)
    c["change_source"].append(poller)

    for repo in repos.get_sub_repos():
        poller = GitPoller(repo.url,
                           project=main_repo.name,
                           branches=[repo.branch],
                           pollinterval=60)
        c["change_source"].append(poller)
