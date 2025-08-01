---
description: Different Ways to Deploy the omniparse API endpoint
---

# Deployment

## 🛳️ Docker

To use OmniParse with Docker, execute the following commands:

1. Pull the OmniParse API Docker image from Docker Hub:
2. Run the Docker container, exposing port 8000: 👉🏼[Docker Image](https://hub.docker.com/r/savatar101/omniparse)

```bash
docker pull savatar101/omniparse:0.1
# if you are running on a gpu 
docker run --gpus all -p 8000:8000 savatar101/omniparse:0.1
# else
docker run -p 8000:8000 savatar101/omniparse:0.1
```

Alternatively, if you prefer to build the Docker image locally: Then, run the Docker container as follows:

```bash
docker build -t omniparse .
# if you are running on a gpu
docker run --gpus all -p 8000:8000 omniparse
# else
docker run -p 8000:8000 omniparse

```