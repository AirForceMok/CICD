FROM python:3.10.4-slim-bullseye


ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


WORKDIR /code

COPY . .
RUN pip install -r requirements.txt

CMD python manage.py runserver 0.0.0.0:8000
