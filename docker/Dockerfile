# vim: ft=dockerfile
FROM python:3.11-alpine AS builder
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade poetry
COPY  ./backupr /backupr/backupr
COPY  ./poetry.lock /backupr/poetry.lock
COPY  ./pyproject.toml /backupr/pyproject.toml
COPY  ./README.md /backupr/README.md
RUN cd /backupr && poetry build --format=wheel

FROM python:3.11-alpine AS backupr
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
COPY --from=builder /backupr/dist /tmp/backupr
RUN pip install /tmp/backupr/*.whl && rm -rf /tmp/backupr
COPY docker/entrypoint.sh /usr/bin
CMD /usr/bin/entrypoint.sh
