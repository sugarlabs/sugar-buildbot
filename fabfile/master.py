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
from common import instances
from common import get_instance_name
from common import get_virtualenv_activate
from common import docs_slave
from common import dist_slave

env.roledefs["master"] = ["dnarvaez@shell.sugarlabs.org"]

master_settings = {"sudo_user": "buildbot",
                   "sudo_prefix": "sudo -H"}


@task
@roles("master")
@with_settings(**master_settings)
def create(instance_name=get_instance_name()):
    instance_info = instances[instance_name]

    sudo("rm -rf ~/%s" % instance_info["sandbox_dir"])
    sudo("virtualenv ~/%s" % instance_info["sandbox_dir"])

    with prefix(get_virtualenv_activate(instance_name)):
        sudo("pip install SQLAlchemy==0.7.9")
        sudo("pip install buildbot")

        sudo("rm -rf ~/%s" % instance_info["master_dir"])
        sudo("buildbot create-master --log-size %d --log-count %d ~/%s" %
             (1024 * 1024 * 10, 10, instance_info["master_dir"]))

    execute(update)
    execute(configure)


@task
@roles("master")
@with_settings(**master_settings)
def update(instance_name=get_instance_name()):
    instance_info = instances[instance_name]

    with prefix(get_virtualenv_activate(instance_name)):
        sudo("rm -rf ~/git")
        sudo("mkdir ~/git")

        with cd("~/git"):
            url = "git://github.com/sugarlabs/sugar-buildbot.git"
            sudo("git clone %s" % url)

            with cd("sugar-buildbot"):
                sudo("git checkout %s" % instance_info["branch"])

            config = instance_info["config"]
            sudo("git clone %s" % config["repo"])

            with cd("sugar-build"):
                sudo("git checkout %s" % config["branch"])

        with cd("~/git/sugar-buildbot"):
            sudo("cp *.py master.cfg ~/%s" % instance_info["master_dir"])

        with cd("~/git/sugar-build"):
            sudo("cp -R build/config/modules.json ~/%s" %
                 instance_info["master_dir"])


@task
@roles("master")
@with_settings(**master_settings)
def configure(instance_name=get_instance_name()):
    instance_info = instances[instance_name]

    config = {"slaves": {}}
    config.update(instance_info["config"])

    tac = StringIO.StringIO()

    for host, info in slaves.items():
        slave_config = {"lock": info["lock"]}
        config["slaves"][info["name"]] = slave_config

        with settings(host_string=host, gateway=info["gateway"]):
            get(os.path.join(instance_info["slave_dir"], "buildbot.tac"), tac)
            for line in tac.getvalue().split("\n"):
                start = "passwd = "
                if line.startswith(start):
                    password = line[len(start) + 1:-1]
                    slave_config["password"] = password

    if instance_info["upload_docs"]:
        config["slaves"][docs_slave]["upload_docs"] = True

    if instance_info["upload_dist"]:
        config["slaves"][docs_slave]["upload_dist"] = True

    config_json = StringIO.StringIO()
    json.dump(config, config_json, indent=4, sort_keys=True)
    put(config_json, "config.json")
    sudo("cp config.json ~/%s" % instance_info["master_dir"])
    run("rm config.json")


@task
@roles("master")
@with_settings(**master_settings)
def start(instance_name=get_instance_name()):
    with prefix(get_virtualenv_activate(instance_name)):
        sudo("buildbot start ~/%s" % instances[instance_name]["master_dir"])


@task
@roles("master")
@with_settings(**master_settings)
def stop(instance_name=get_instance_name()):
    with prefix(get_virtualenv_activate(instance_name)):
        sudo("buildbot stop ~/%s" % instances[instance_name]["master_dir"])


@task
@roles("master")
@with_settings(**master_settings)
def reconfig(instance_name=get_instance_name()):
    with prefix(get_virtualenv_activate(instance_name)):
        sudo("buildbot reconfig ~/%s" % instances[instance_name]["master_dir"])


@task
@roles("master")
@with_settings(**master_settings)
def restart(instance_name=get_instance_name()):
    with prefix(get_virtualenv_activate(instance_name)):
        sudo("buildbot restart ~/%s" % instances[instance_name]["master_dir"])
