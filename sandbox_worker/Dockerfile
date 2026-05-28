FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY worker.py /workspace/worker.py
COPY policy/allowed_hosts.yaml /workspace/policy/allowed_hosts.yaml
COPY policy/filesystem_policy.yaml /workspace/policy/filesystem_policy.yaml

RUN useradd -m worker && chown -R worker:worker /workspace
USER worker

CMD ["python3", "/workspace/worker.py"]
