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
from fabric.api import sudo
from fabric.api import settings
from fabric.contrib.files import append

from common import slaves
from common import instances
from common import get_virtualenv_activate, get_virtualenv_bin
from common import get_instance_name


admin = "Daniel Narvaez <dwnarvaez@gmail.com>"

env.roledefs["slave"] = slaves.keys()


def get_settings():
    slave = slaves[env.host_string]
    return {"gateway": slave["gateway"]}


@task
@roles("slave")
def create(instance_name=get_instance_name()):
    with settings(**get_settings()):
        instance_info = instances[instance_name]

        run("rm -rf %s" % instance_info["sandbox_dir"])
        run("virtualenv --system-site-packages %s" %
            instance_info["sandbox_dir"])

        chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
        password = ''.join(random.choice(chars) for x in range(16))

        with prefix(get_virtualenv_activate(instance_name)):
            run("rm -rf buildbot")
            run("git clone git://github.com/buildbot/buildbot.git")
            run("cd buildbot; git checkout 9b76190207")
            run("pip install buildbot/slave")

            name = slaves[env.host_string]["name"]

            run("rm -rf %s" % instance_info["slave_dir"])

            run("buildslave create-slave --umask=022 %s "
                "buildbot.sugarlabs.org:%d "
                "%s %s" % (instance_info["slave_dir"],
                           instance_info["config"]["slaves_port"],
                           name, password))

            put(StringIO.StringIO(admin),
                os.path.join(instance_info["slave_dir"], "info", "admin"))
            put(StringIO.StringIO(name),
                os.path.join(instance_info["slave_dir"], "info", "host"))


@task
@roles("slave")
def start(instance_name=get_instance_name()):
    with settings(**get_settings()):
        buildslave_bin = get_virtualenv_bin(instance_name, "buildslave")
        slave_dir = instances[instance_name]["slave_dir"]
        run("%s start %s" % (buildslave_bin, slave_dir))


@task
@roles("slave")
def stop(instance_name=get_instance_name()):
    with settings(**get_settings()):
        with prefix(get_virtualenv_activate(instance_name)):
            run("buildslave stop %s" % instances[instance_name]["slave_dir"])


@task
@roles("slave")
def restart(instance_name=get_instance_name()):
    with settings(**get_settings()):
        with prefix(get_virtualenv_activate(instance_name)):
            run("buildslave restart %s" %
                instances[instance_name]["slave_dir"])


@task
@roles("slave")
def add_key(filename):
    with settings(**get_settings()):
        with open(filename) as f:
            append(".ssh/authorized_keys", f.read())


@task
@roles("slave")
def shutdown():
    with settings(**get_settings()):
        sudo("shutdown -h now")


@task
@roles("slave")
def clean_build(instance_name=get_instance_name()):
    with settings(**get_settings()):
        instance_info = instances[instance_name]
        slave_dir = instance_info["slave_dir"]
        for name in "full", "quick":
            run("rm -rf %s" % os.path.join(slave_dir, "*-%s" % name))


@task
@roles("slave")
def kill_dbus(instance_name=get_instance_name()):
    with settings(**get_settings()):
        run("killall dbus-daemon | true")
