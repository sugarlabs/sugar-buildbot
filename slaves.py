from buildbot.buildslave import BuildSlave

def setup(c, config):
    c["slaves"] = []

    for name, info in config["slaves"].items():
        c["slaves"].append(BuildSlave(name, info["password"]))
    
    c["slavePortnum"] = 9989
