from buildbot.status import html
from buildbot.status.web import authz
from buildbot.status import words
from buildbot.status.mail import MailNotifier
from buildbot.status.status_push import HttpStatusPush


def setup(c, config):
    c["status"] = []

    authz_cfg = authz.Authz(forceBuild=True,
                            forceAllBuilds=True,
                            stopBuild=True,
                            stopAllBuilds=True,
                            cancelPendingBuild=True,
                            stopChange=True)

    c["status"].append(html.WebStatus(http_port=config["web_port"],
                                      authz=authz_cfg,
                                      change_hook_dialects={"base": True}))

    c["status"].append(words.IRC(host="irc.freenode.net",
                                 nick="sbbot",
                                 channels=["#sugar"],
                                 categories=["upstream"],
                                 notify_events={"successToFailure": 1,
                                                "failureToSuccess": 1}))

    c["status"].append(MailNotifier(fromaddr="buildbot@sugarlabs.org",
                                    mode=["problem"],
                                    lookup="sugarlabs.org",
                                    categories=["upstream"],
                                    extraRecipients=["dwnarvaez@gmail.com"]))

    c["status"].append(HttpStatusPush(serverUrl=str(config["status_url"])))
