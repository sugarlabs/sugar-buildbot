from fabric.api import local


instances = {"production":
             {"master_dir": "master",
              "slave_dir": "slave",
              "sandbox_dir": "sandbox",
              "branch": "master",
              "upload_docs": True,
              "config":
              {"repo": "git://git.sugarlabs.org/sugar-build/sugar-build.git",
               "branch": "master",
               "nightly_builds": True,
               "slaves_port": 9989,
               "snapshot": True,
               "web_port": 8080}},
             "testing":
             {"master_dir": "master-html",
              "slave_dir": "slave-html",
              "sandbox_dir": "sandbox-html",
              "branch": "html",
              "upload_docs": False,
              "config":
              {"repo": "git://git.sugarlabs.org/sugar-build/sugar-build.git",
               "branch": "html",
               "check_system": False,
               "slaves_port": 9991,
               "web_port": 8082}},
             "testing":
             {"master_dir": "master-testing",
              "slave_dir": "slave-testing",
              "sandbox_dir": "sandbox-testing",
              "branch": "testing",
              "upload_docs": False,
              "config":
              {"repo": "git://git.sugarlabs.org/sugar-build/sugar-build.git",
               "branch": "testing",
               "check_system": False,
               "slaves_port": 9990,
               "sub_repos_changes": False,
               "web_port": 8081}}}

slaves = {"buildbot@bs-wheezy-amd64.local":
          {"name": "wheezy-amd64",
           "lock": "freedom",
           "gateway": "dnarvaez@freedom.sugarlabs.org"},
          "buildbot@bs-quantal-amd64.local":
          {"name": "quantal-amd64",
           "lock": "freedom",
           "gateway": "dnarvaez@freedom.sugarlabs.org"},
          "buildbot@bs-sphcow-x86-64.local":
          {"name": "sphcow-x86-64",
           "lock": "freedom",
           "gateway": "dnarvaez@freedom.sugarlabs.org"},
          "buildbot@bs-wheezy-i386.local":
          {"name": "wheezy-i386",
           "lock": "bender",
           "gateway": "dnarvaez@bender.sugarlabs.org"},
          "buildbot@bs-quantal-i386.local":
          {"name": "quantal-i386",
           "lock": "bender",
           "gateway": "dnarvaez@bender.sugarlabs.org"},
          "buildbot@bs-sphcow-i386.local":
          {"name": "sphcow-i386",
           "lock": "bender",
           "gateway": "dnarvaez@bender.sugarlabs.org"}}

docs_slave = "sphcow-x86-64"

_instance_name = None


def get_virtualenv_activate(instance_name):
    return "source ~/%s/bin/activate" % instances[instance_name]["sandbox_dir"]


def get_instance_name():
    global _instance_name

    if _instance_name is None:
        _instance_name == "production"

        branch = local("git rev-parse --abbrev-ref HEAD", capture=True)
        for name, info in instances.items():  
            if info["branch"] == branch:
                _instance_name = name

    return _instance_name
