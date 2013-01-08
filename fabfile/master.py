import os
import StringIO
import json


from fabric.api import task
from fabric.api import sudo
from fabric.api import run
from fabric.api import env
from fabric.api import prefix
from fabric.api import put
from fabric.api import cd
from fabric.api import get
from fabric.api import execute
from fabric.api import roles
from fabric.api import with_settings
from fabric.api import settings

from common import slaves
from common import slave_gateway
from common import instances
from common import get_instance_name

repos = ["git://git.sugarlabs.org/sugar-buildbot/sugar-buildbot.git",
         "git://git.sugarlabs.org/sugar-build/sugar-build.git"]

activate_virtualenv = "source ~/sandbox/bin/activate"

env.roledefs["master"] = ["dnarvaez@shell.sugarlabs.org"]

master_settings = {"sudo_user": "buildbot",
                   "sudo_prefix": "sudo -H"}


@task
@roles("master")
@with_settings(**master_settings)
def create(instance_name=get_instance_name()):
    instance_info = instances[instance_name]

    sudo("rm -rf ~/sandbox")
    sudo("virtualenv ~/sandbox")

    with prefix(activate_virtualenv):
        sudo("pip install SQLAlchemy==0.7.9")
        sudo("pip install buildbot")

        sudo("rm -rf ~/%s" % instance_info["master_dir"])
        sudo("buildbot create-master ~/%s" % instance_info["master_dir"])

    execute(update)
    execute(configure)


@task
@roles("master")
@with_settings(**master_settings)
def update(instance_name=get_instance_name()):
    instance_info = instances[instance_name]

    with prefix(activate_virtualenv):
        sudo("rm -rf ~/git")
        sudo("mkdir ~/git")

        with cd("~/git"):
            for url in repos:
                sudo("git clone %s" % url)

        with cd("~/git/sugar-buildbot"):
            sudo("cp *.py master.cfg ~/%s" % instance_info["master_dir"])

        with cd("~/git/sugar-build"):
            sudo("cp -R config/modules ~/%s" % instance_info["master_dir"])


@task
@roles("master")
@with_settings(**master_settings)
def configure(instance_name=get_instance_name()):
    instance_info = instances[instance_name]

    repo = "git://git.sugarlabs.org/sugar-build/sugar-build.git"

    config = {"slaves": {}, "repo": repo}
    config.update(instance_info["config"])

    tac = StringIO.StringIO()

    for host, name in slaves.items():
        with settings(host_string=host, gateway=slave_gateway):
            get(os.path.join(instance_info["slave_dir"], "buildbot.tac"), tac)
            for line in tac.getvalue().split("\n"):
                start = "passwd = "
                if line.startswith(start):
                    password = line[len(start) + 1:-1]
                    config["slaves"][name] = {"password": password}

    config_json = StringIO.StringIO()
    json.dump(config, config_json, indent=4, sort_keys=True)
    put(config_json, "config.json")
    sudo("cp config.json ~/%s" % instance_info["master_dir"])
    run("rm config.json")


@task
@roles("master")
@with_settings(**master_settings)
def start(instance_name=get_instance_name()):
    with prefix(activate_virtualenv):
        sudo("buildbot start ~/%s" % instances[instance_name]["master_dir"])


@task
@roles("master")
@with_settings(**master_settings)
def stop(instance_name=get_instance_name()):
    with prefix(activate_virtualenv):
        sudo("buildbot stop ~/%s" % instances[instance_name]["master_dir"])


@task
@roles("master")
@with_settings(**master_settings)
def restart(instance_name=get_instance_name()):
    with prefix(activate_virtualenv):
        sudo("buildbot restart ~/%s" % instances[instance_name]["master_dir"])
