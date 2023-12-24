# Modified Dockerfile based on: https://github.com/danbooru/autotagger/tree/master
FROM python:3.10.13

WORKDIR /autotagger

# https://github.com/python-poetry/poetry/discussions/1879#discussioncomment-216865
ENV \
  # https://stackoverflow.com/questions/59812009/what-is-the-use-of-pythonunbuffered-in-docker-file
  PYTHONUNBUFFERED=1 \
  # https://python-docs.readthedocs.io/en/latest/writing/gotchas.html#disabling-bytecode-pyc-files
  PYTHONDONTWRITEBYTECODE=1 \
  # https://stackoverflow.com/questions/45594707/what-is-pips-no-cache-dir-good-for
  PIP_NO_CACHE_DIR=1 \
  # https://stackoverflow.com/questions/46288847/how-to-suppress-pip-upgrade-warning
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PATH=/autotagger:$PATH

RUN \
  apt-get update && \
  apt-get install -y --no-install-recommends tini build-essential gfortran libatlas-base-dev wget && \
  pip install "poetry==1.7.1"

COPY pyproject.toml poetry.lock ./
RUN \
  python -m poetry install --no-dev && \
  rm -rf /root/.cache/pypoetry/artifacts /root/.cache/pypoetry/cache

COPY wd-v1-4-moat-tagger-v2 ./wd-v1-4-moat-tagger-v2
COPY gunicorn.conf.py main.py ./

EXPOSE 5000
ENTRYPOINT ["tini", "--", "poetry", "run"]
CMD ["gunicorn"]
