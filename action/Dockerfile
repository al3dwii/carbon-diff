# ---------- build layer ----------
FROM python:3.12-slim AS build
WORKDIR /code

# 1. bring in project metadata **including the README**
COPY pyproject.toml poetry.lock README.md /code/

RUN pip install --no-cache-dir poetry

# 2. copy source so Poetry can build the wheel & console-script
COPY carbon_diff /code/carbon_diff

# 3. install *with* the root package
RUN poetry config virtualenvs.create false \
&& poetry install --no-interaction --no-ansi

# ---------- runtime layer ----------
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/code
WORKDIR /code

COPY --from=build /usr/local /usr/local
COPY --from=build /code /code
ENTRYPOINT ["carbon-diff"]
