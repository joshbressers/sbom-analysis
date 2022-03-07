# sbom-analysis
Scripts to conduct SBOM analysis

# Putting it all together
We use the docker daemon to control authentication and cache the images.
If you're not logged into docker you will hit your pull limit pretty quick.
Make sure you "docker login"

This also takes up a fair bit of space because of all the images, make sure
you have enough disk space.

The order of operations are basically:
Run Elasticsearch
Create a python virtual environment
Install https://github.com/joshbressers/es-bulk-stream
Run get-containers.py
Run build-sbom.py
Run load-sbom.py
Run load-vulns.py

Each of these steps isn't as simple as a quick run. I'll write this up
nicer if there's interest. It's a very bespoke system right now, the
learning curve is a straight line that goes up very very high.
