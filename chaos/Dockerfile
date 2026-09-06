FROM docker:26-cli AS dockercli

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

COPY --from=dockercli /usr/local/bin/docker /usr/local/bin/docker

COPY chaos.py .

CMD ["python", "chaos.py"]
