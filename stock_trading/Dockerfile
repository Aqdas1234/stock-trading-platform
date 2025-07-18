FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip && pip install poetry

WORKDIR /app

COPY . /app/

RUN poetry config virtualenvs.create false \
  && poetry install --only main --no-root


EXPOSE 8000

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
