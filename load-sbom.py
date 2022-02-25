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

        sbom_file = f"{cwd}/SBOMs/{c}.json"

        with open(sbom_file) as sfh:
            spdx_data = json.loads(sfh.read())


            for p in spdx_data['artifacts']:

                the_doc = {}
                the_doc['container_name'] = c
                the_doc['package_name'] = p['name']
                the_doc['type'] = p['type']
                the_doc['version'] = p['version']
                the_doc['licenses'] = p['licenses']
                if 'metadata' in p and p['metadata']:
                    if 'size' in p['metadata']:
                        the_doc['size'] = p['metadata']['size']
                    if 'installedSize' in p['metadata']:
                        the_doc['installedSize'] = p['metadata']['installedSize']
                    if 'description' in p['metadata']:
                        the_doc['description'] = p['metadata']['description']

                es.add(the_doc, uuid.uuid4())

    es.done()


if __name__ == "__main__":
    main()
