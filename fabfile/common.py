from fabric.api import local


instances = {"production":
             {"master_dir": "master",
              "slave_dir": "slave",
              "sandbox_dir": "sandbox",
              "config":
              {"repo": "git://github.com/sugarlabs/sugar-build.git",
               "branch": "master",
               "slaves_port": 9990,
               "web_port": 8080,
               "architectures": ["i386", "x86_64"]
               "branches": ["master", "sucrose-0.100"]}}}

slaves = {"buildbot@freedom-buildslave.local":
          {"name": "freedom",
           "gateway": "dnarvaez@freedom.sugarlabs.org",
           "arch": "x86_64"},
          "buildbot@bender-buildslave.local":
          {"name": "bender",
           "gateway": "dnarvaez@bender.sugarlabs.org",
           "arch": "i386"}}

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
