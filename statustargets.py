from buildbot.status import html
from buildbot.status.web import authz, auth
from buildbot.status import words
from buildbot.status.mail import MailNotifier

def setup(c, config):
    c["status"] = []

    admin_name = config["admin"]["name"];
    admin_password = config["admin"]["password"];

    basic_auth = auth.BasicAuth([(admin_name, admin_password)])
    authz_cfg = authz.Authz(auth=basic_auth, forceBuild="auth")

    c["status"].append(html.WebStatus(http_port=config["port"],
                                      authz=authz_cfg))

    c["status"].append(words.IRC(host="irc.freenode.net",
                                 nick="sugarbuildbot",
                                 channels=["#sugar-buildbot"],
                                 categories=["stable"],
                                 notify_events={"failureToSuccess": 1,
                                                "failure": 1}))

    c["status"].append(MailNotifier(fromaddr="buildbot@sugarlabs.org",
                                    mode=["problem"],
                                    lookup="sugarlabs.org"))

