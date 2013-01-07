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

from slave import slaves
from slave import slave_gateway

instances = {"master": {"slavedir": "slave",
                        "port": 9989},
             "master-testing": {"slavedir": "slave-testing",
                                "port": 9990}}

repos = ["git://git.sugarlabs.org/sugar-buildbot/sugar-buildbot.git",
         "git://git.sugarlabs.org/sugar-build/sugar-build.git"]

activate_virtualenv = "source ~/sandbox/bin/activate"

env.roledefs["master"] = ["dnarvaez@shell.sugarlabs.org"]

master_settings = {"sudo_user": "buildbot",
                   "sudo_prefix": "sudo -H"}

@task
@roles("master")
@with_settings(**master_settings)
def create():
    sudo("rm -rf ~sandbox")

    sudo("virtualenv ~/sandbox")

    with prefix(activate_virtualenv):
        sudo("pip install SQLAlchemy==0.7.9")
        sudo("pip install buildbot")
        
        for basedir in instances.keys():
            sudo("rm -rf ~/%s" % basedir)
            sudo("buildbot create-master ~/%s" % basedir)

    execute(update)

@task
@roles("master")
@with_settings(**master_settings)
def update():
    with prefix(activate_virtualenv):
        sudo("rm -rf ~/git")
        sudo("mkdir ~/git")

        with cd("~/git"):
            for url in repos:
                sudo("git clone %s" % url)

        for basedir in instances.keys():
             with cd("~/git/sugar-buildbot"):
                sudo("cp *.py master.cfg ~/%s" % basedir)

             with cd("~/git/sugar-build"):
                sudo("cp -R config/modules ~/%s" % basedir)


@task
@roles("master")
@with_settings(**master_settings)
def configure():
    config = {"slaves": {}}
    tac = StringIO.StringIO()
    
    for basedir, info in instances.items():
        for host, name in slaves.items():
            with settings(host_string=host, gateway=slave_gateway):
                get(os.path.join(info["slavedir"], "buildbot.tac"), tac)
                for line in tac.getvalue().split("\n"):
                    start = "passwd = "
                    if line.startswith(start):
                        password = line[len(start) + 1:-1]
                        config["slaves"][name] = {"password": password}

        config_json = StringIO.StringIO()
        json.dump(config, config_json, indent=4, sort_keys=True)
        put(config_json, "config.json")
        sudo("cp config.json ~/%s" % basedir)
        run("rm config.json")


@task
@roles("master")
@with_settings(**master_settings)
def start(basedir="master"):
    with prefix(activate_virtualenv):
        sudo("builbot start ~/%s" % basedir) 


@task
@roles("master")
@with_settings(**master_settings)
def stop(basedir="master"):
    with prefix(activate_virtualenv):
        sudo("buildbot stop ~/%s" % basedir) 


@task
@roles("master")
@with_settings(**master_settings)
def restart(basedir="master"):
    with prefix(activate_virtualenv):
        sudo("buildbot restart ~/%s" % basedir) 
