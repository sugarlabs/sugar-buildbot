from buildbot.status import html
from buildbot.status.web import authz, auth

def setup(c, admin_name, admin_password):
    c["status"] = []

    basic_auth = auth.BasicAuth([(admin_name, admin_password)])
    authz_cfg = authz.Authz(auth=basic_auth, forceBuild="auth")

    c["status"].append(html.WebStatus(http_port=8010, authz=authz_cfg))

