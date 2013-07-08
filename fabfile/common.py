from fabric.api import local


instances = {"production":
             {"master_dir": "master-chroot",
              "slave_dir": "slave-chroot",
              "sandbox_dir": "sandbox-chroot",
              "branch": "chroot",
              "upload_docs": True,
              "upload_dist": True,
              "config":
              {"repo": "git://github.com/sugarlabs/sugar-build.git",
               "branch": "chroot",
               "nightly_builds": True,
               "slaves_port": 9990,
               "web_port": 8081}}}

slaves = {"buildbot@bs-freedom-x86-64.local":
          {"name": "freedom-x86-64",
           "gateway": "dnarvaez@freedom.sugarlabs.org"}}

docs_slave = "freedom-x86-64"
dist_slave = "freedom-x86-64"

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
        if branch == "chroot":
            _instance_name = "production"
        else:
            _instance_name = "testing"

    return _instance_name
