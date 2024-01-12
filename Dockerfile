FROM python:3.9

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0", "datadrone:create_app()"]
