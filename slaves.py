from buildbot.buildslave import BuildSlave

def setup(c, config):
    c["slaves"] = []

    for name, password in config["slaves"].items():
        c["slaves"].append(BuildSlave(name, password))
    
    c["slavePortnum"] = 9989
