from fabric.api import local


instances = {"production":
             {"master_dir": "master",
              "slave_dir": "slave",
              "sandbox_dir": "sandbox",
              "config":
              {"distribute": True,
               "nightly_builds": True,
               "slaves_port": 9989,
               "snapshot": True,
               "web_port": 8080}},
             "testing":
             {"master_dir": "master-testing",
              "slave_dir": "slave-testing",
              "sandbox_dir": "sandbox-testing",
              "config":
              {"branch": "testing",
               "check_system": False,
               "slaves_port": 9990,
               "sub_repos_changes": False,
               "web_port": 8081}}}

slaves = {"buildbot@debian-wheezy-32bit.local": "debian-wheezy-32bit",
          "buildbot@debian-wheezy-64bit.local": "debian-wheezy-64bit",
          "buildbot@fedora-17-32bit.local": "fedora-17-32bit",
          "buildbot@fedora-17-64bit.local": "fedora-17-64bit",
          "buildbot@fedora-18-32bit.local": "fedora-18-32bit",
          "buildbot@fedora-18-64bit.local": "fedora-18-64bit",
          "buildbot@ubuntu-12-10-32bit.local": "ubuntu-12-10-32bit",
          "buildbot@ubuntu-12-10-64bit.local": "ubuntu-12-10-64bit"}

slave_gateway = "dnarvaez@bender.sugarlabs.org"

_instance_name = None


def get_virtualenv_activate(instance_name):
    return "source ~/%s/bin/activate" % instances[instance_name]["sandbox_dir"]


def get_instance_name():
    global _instance_name

    if _instance_name is None:
        branch = local("git rev-parse --abbrev-ref HEAD", capture=True)
        if branch == "master":
            _instance_name = "production"
        else:
            _instance_name = "testing"

    return _instance_name
