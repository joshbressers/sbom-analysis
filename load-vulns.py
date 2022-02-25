#!/usr/bin/env python

import docker
import json
import uuid
from esbulkstream import Documents

def main():

    docker_client = docker.from_env()

    es = Documents('vulns')

    with open("top-containers.json") as fh:
        container_names = json.load(fh)['containers']

    for c in container_names:
        output = docker_client.containers.run("anchore/grype", \
            "-c /grype.yaml -o json %s" % c, volumes=['/home/bress/src/sbom-analysis/grype.yaml:/grype.yaml'])

        json_data = json.loads(output)


        for p in json_data['matches']:

            the_doc = {}
            the_doc['vuln_id'] = p['vulnerability']['id']
            the_doc['severity'] = p['vulnerability']['severity']
            the_doc['fix'] = p['vulnerability']['fix']
            the_doc['package'] = p['artifact']['name']
            the_doc['version'] = p['artifact']['version']
            the_doc['type'] = p['artifact']['type']
            the_doc['container'] = c
            the_doc['related'] = p['relatedVulnerabilities']

            es.add(the_doc, uuid.uuid4())

    es.done()


if __name__ == "__main__":
    main()
