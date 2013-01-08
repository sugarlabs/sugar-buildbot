instances = {"production":
             {"master_dir": "master",
              "slave_dir": "slave",
              "config":
              {"distribute": True,
               "nightly_builds": True,
               "slaves_port": 9989,
               "snapshot": True,
               "web_port": 8080}},
             "testing":
             {"master_dir": "master-testing",
              "slave_dir": "slave-testing",
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

activate_virtualenv = "source sandbox/bin/activate"

def get_instance_name():
    branch = local("git rev-parse --abbrev-ref HEAD", capture=True)
    if branch == "master":
        return "production"
    else:
        return "testing"
