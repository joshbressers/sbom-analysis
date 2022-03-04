#!/usr/bin/env python

import docker
import json
import os
import uuid
import glob
from esbulkstream import Documents

def main():

    cwd = os.getcwd()
    es = Documents('sbom')
    files = Documents('sbom-files')

    the_files = glob.glob(f"{cwd}/SBOMs/*.json")
    for sbom_file in the_files:

        # Get just the container name
        c = os.path.split(sbom_file)[-1][:-5]
        print(c)

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


                    if 'files' in p['metadata']:
                        for f in p['metadata']['files']:
                            file_doc = {}
                            file_doc['container_name'] = c
                            file_doc['package_name'] = p['name']
                            if type(f) is dict:
                                # Only load dicts (there are other things
                                # here sometimes
                                file_doc.update(f)
                                files.add(file_doc, uuid.uuid4())


                es.add(the_doc, uuid.uuid4())

    es.done()
    files.done()


if __name__ == "__main__":
    main()
