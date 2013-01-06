from buildbot.status import html
from buildbot.status.web import authz
from buildbot.status import words
from buildbot.status.mail import MailNotifier


def setup(c, config):
    c["status"] = []

    authz_cfg = authz.Authz(forceBuild=True,
                            forceAllBuilds=True,
                            stopBuild=True,
                            stopAllBuilds=True,
                            cancelPendingBuild=True,
                            stopChange=True)

    c["status"].append(html.WebStatus(http_port=config["web_port"],
                                      authz=authz_cfg))

    c["status"].append(words.IRC(host="irc.freenode.net",
                                 nick="sugarbuildbot",
                                 channels=["#sugar-buildbot"],
                                 categories=["production"],
                                 notify_events={"failureToSuccess": 1,
                                                "failure": 1}))

    c["status"].append(MailNotifier(fromaddr="buildbot@sugarlabs.org",
                                    mode=["problem"],
                                    categories=["production"],
                                    lookup="sugarlabs.org"))
