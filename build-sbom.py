#!/usr/bin/env python

import docker
import json
import os
import uuid
from esbulkstream import Documents

def main():

    cwd = os.getcwd()

    docker_client = docker.from_env()

    es = Documents('sbom')

    with open("top-containers.json") as fh:
        container_names = json.load(fh)['containers']

    for c in container_names:
        print("Scanning %s" % c)

        if c == "elasticsearch":
            c = "elasticsearch:8.0.0"
        elif c == "logstash":
            c = "logstash:8.0.0"
        elif c == "kibana":
            c = "kibana:8.0.0"
        elif c == "jenkins":
            c = "jenkins:2.60.3"
        elif c == "oraclelinux":
            c = "oraclelinux:8"
        elif c == "opensuse":
            continue
        elif c == "ubuntu-debootstrap":
            continue
        elif c == "notary":
            c = "notary:signer"
        elif c == "docker-dev":
            continue
        elif c == "ibm-semeru-runtimes":
            c = "ibm-semeru-runtimes:open-8u322-b06-jre-centos7"
        elif c == "scratch":
            continue
        elif c == "clefos":
            # Syft doesn't like this image, just skip it
            continue
        else:
            c = f"{c}:latest"

        docker_client.images.pull(c)
        output = docker_client.containers.run("anchore/syft", \
            "-o json --file /SBOMs/%s.json packages docker:%s" % (c, c), \
            auto_remove=True, \
            environment=["SYFT_FILE_METADATA_CATALOGER_ENABLED=true"], \
            volumes=[f"{cwd}/SBOMs:/SBOMs", "/var/run/docker.sock:/var/run/docker.sock"])

if __name__ == "__main__":
    main()
