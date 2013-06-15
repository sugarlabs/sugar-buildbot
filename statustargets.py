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

    dialects = {"github": True}

    c["status"].append(html.WebStatus(http_port=config["web_port"],
                                      authz=authz_cfg,
                                      change_hook_dialects=dialects))

    c["status"].append(words.IRC(host="irc.freenode.net",
                                 nick="sugarbuildbot",
                                 channels=["#sugar-buildbot"],
                                 notify_events={"failureToSuccess": 1,
                                                "failure": 1}))

    c["status"].append(MailNotifier(fromaddr="buildbot@sugarlabs.org",
                                    mode=["problem"],
                                    lookup="sugarlabs.org",
                                    extraRecipients=["dwnarvaez@gmail.com"]))
