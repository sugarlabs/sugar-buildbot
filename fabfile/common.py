from fabric.api import local


instances = {"production":
             {"master_dir": "master",
              "slave_dir": "slave",
              "sandbox_dir": "sandbox",
              "branch": "master",
              "upload_docs": True,
              "config":
              {"repo": "git://github.com/sugarlabs/sugar-build.git",
               "branch": "master",
               "nightly_builds": True,
               "slaves_port": 9989,
               "web_port": 8080}},
             "testing":
             {"master_dir": "master-testing",
              "slave_dir": "slave-testing",
              "sandbox_dir": "sandbox-testing",
              "branch": "testing",
              "upload_docs": False,
              "config":
              {"repo": "git://github.com/sugarlabs/sugar-build.git",
               "branch": "testing",
               "check_system": False,
               "slaves_port": 9990,
               "sub_repos_changes": False,
               "web_port": 8081}}}

slaves = {"buildbot@bs-jessie-amd64.local":
          {"name": "jessie-amd64",
           "lock": "freedom",
           "gateway": "dnarvaez@freedom.sugarlabs.org"},
          "buildbot@bs-raring-amd64.local":
          {"name": "raring-amd64",
           "lock": "freedom",
           "gateway": "dnarvaez@freedom.sugarlabs.org"},
          "buildbot@bs-schroedinger-x86-64.local":
          {"name": "schroedinger-x86-64",
           "lock": "freedom",
           "gateway": "dnarvaez@freedom.sugarlabs.org"},
          "buildbot@bs-sphcow-x86-64.local":
          {"name": "sphcow-x86-64",
           "lock": "freedom",
           "gateway": "dnarvaez@freedom.sugarlabs.org"},
          "buildbot@bs-jessie-i386.local":
          {"name": "jessie-i386",
           "lock": "bender",
           "gateway": "dnarvaez@bender.sugarlabs.org"},
          "buildbot@bs-raring-i386.local":
          {"name": "raring-i386",
           "lock": "bender",
           "gateway": "dnarvaez@bender.sugarlabs.org"},
          "buildbot@bs-sphcow-i386.local":
          {"name": "sphcow-i386",
           "lock": "bender",
           "gateway": "dnarvaez@bender.sugarlabs.org"}}

docs_slave = "raring-amd64"

_instance_name = None


def get_virtualenv_activate(instance_name):
    return "source ~/%s/bin/activate" % instances[instance_name]["sandbox_dir"]


def get_virtualenv_bin(instance_name, bin_name="python"):
    sandbox_dir = instances[instance_name]["sandbox_dir"]
    return "~/%s/bin/%s" % (sandbox_dir, bin_name)


def get_instance_name():
    global _instance_name

    if _instance_name is None:
        branch = local("git rev-parse --abbrev-ref HEAD", capture=True)
        if branch == "master":
            _instance_name = "production"
        else:
            _instance_name = "testing"

    return _instance_name
