#!/usr/bin/env python

import requests
import sys
import json

url = "https://hub.docker.com/v2/repositories/library/?page=1&page_size=15"

output = { "containers": [] }

while True:
    response = requests.get(url)

    container_data = response.json()

    for i in container_data['results']:
        output["containers"].append(i['name'])

    if container_data['next'] is None:
        with open("top-containers.json", "w") as fh:
            fh.write(json.dumps(output, indent=2))
            fh.write("\n")
            sys.exit(0)

    url = container_data['next']

