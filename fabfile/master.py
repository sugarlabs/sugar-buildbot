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
        sudo("pip install "
             "git+git://github.com/buildbot/buildbot.git/master@9b76190207")

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

            config = instance_info["config"]

            for branch in config["branches"]:
                repo_name = "sugar-build-%s" % branch

                sudo("git clone %s %s" % (config["repo"], repo_name))

                with cd(repo_name):
                    sudo("git checkout %s" % branch)

        with cd("~/git/sugar-buildbot"):
            master_dir = instance_info["master_dir"]
            sudo("cp *.py master.cfg ~/%s" % master_dir)
            sudo("cp -r commands ~/%s" % master_dir)

        for branch in config["branches"]:
            with cd("~/git/sugar-build-%s" % branch):
                sudo("cp -R build/modules.json ~/%s/modules-%s.json" %
                    (instance_info["master_dir"], branch))


@task
@roles("master")
@with_settings(**master_settings)
def configure(instance_name=get_instance_name()):
    instance_info = instances[instance_name]

    config = {"slaves": {}}
    config.update(instance_info["config"])

    tac = StringIO.StringIO()

    for host, info in slaves.items():
        slave_config = {"arch": info["arch"]}

        config["slaves"][info["name"]] = slave_config

        with settings(host_string=host, gateway=info["gateway"]):
            get(os.path.join(instance_info["slave_dir"], "buildbot.tac"), tac)
            for line in tac.getvalue().split("\n"):
                start = "passwd = "
                if line.startswith(start):
                    password = line[len(start) + 1:-1]
                    slave_config["password"] = password

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
