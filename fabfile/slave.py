import string
import StringIO
import os
import random

from fabric.api import task
from fabric.api import run
from fabric.api import env
from fabric.api import prefix
from fabric.api import put
from fabric.api import roles
from fabric.api import with_settings

from common import slaves
from common import slave_gateway
from common import instances
from common import activate_virtualenv


admin = "Daniel Narvaez <dwnarvaez@gmail.com>"

env.roledefs["slave"] = slaves.keys()

settings = {"gateway": slave_gateway}


@task
@roles("slave")
@with_settings(**settings)
def create():
    run("rm -rf sandbox")

    run("virtualenv --system-site-packages sandbox")

    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    password = ''.join(random.choice(chars) for x in range(16))

    with prefix(activate_virtualenv):
        run("pip install buildbot-slave")

        name = slaves[env.host_string]

        for info in instances.values():
            run("rm -rf %s" % info["slave_dir"])

            run("buildslave create-slave %s "
                "buildbot.sugarlabs.org:%d "
                "%s %s" % (info["slave_dir"], info["slave_port"],
                           name, password))

            put(StringIO.StringIO(admin),
                os.path.join(basedir, "info", "admin"))
            put(StringIO.StringIO(name),
                os.path.join(basedir, "info", "host"))


@task
@roles("slave")
@with_settings(**settings)
def start(basedir="slave"):
    with prefix(activate_virtualenv):
        run("buildslave start %s" % basedir)


@task
@roles("slave")
@with_settings(**settings)
def stop(basedir="slave"):
    with prefix(activate_virtualenv):
        run("buildslave stop %s" % basedir)


@task
@roles("slave")
@with_settings(**settings)
def restart(basedir="slave"):
    with prefix(activate_virtualenv):
        run("buildslave restart %s" % basedir)
