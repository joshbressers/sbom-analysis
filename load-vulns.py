#!/usr/bin/env python

import docker
import json
import uuid
import os
import glob
import tempfile
from esbulkstream import Documents

def main():

    cwd = os.getcwd()
    es = Documents('vulns')
    docker_client = docker.from_env()

    # Pull down a new GrypeDB
    grype_env = [
        "GRYPE_DB_CACHE_DIR=/grype_cache",
        "GRYPE_DB_AUTO_UPDATE=false"
    ]
    temp_dir = tempfile.TemporaryDirectory()
    grype_db_location = temp_dir.name
    output = docker_client.containers.run("anchore/grype", "db update" ,volumes=[f"{grype_db_location}:/grype_cache"], environment=grype_env)

    print(output)

    the_files = glob.glob(f"{cwd}/SBOMs/*.json")
    for sbom_file in the_files:

        # Get just the container name
        sbom_name = os.path.split(sbom_file)[-1]
        c = sbom_name[:-5]
        print(c)

        output = docker_client.containers.run("anchore/grype", \
            "-o json sbom:/SBOMs/%s" % sbom_name, volumes=[f"{cwd}/SBOMs:/SBOMs", f"{grype_db_location}:/grype_cache"], environment=grype_env)

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

    # We have to clean up the temporary directory, the DB is owned by root
    output = docker_client.containers.run("alpine", "rm -rf /grype_cache/*"
,volumes=[f"{grype_db_location}:/grype_cache"])

    es.done()


if __name__ == "__main__":
    main()
