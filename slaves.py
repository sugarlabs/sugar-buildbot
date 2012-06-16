from buildbot.buildslave import BuildSlave

def setup(c, slaves_config):
    c["slaves"] = []

    for name, password in slaves_config.items():
        c["slaves"].append(BuildSlave(name, password))
    
    c["slavePortnum"] = 9989
