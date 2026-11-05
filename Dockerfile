FROM python:3.9.16-slim-bullseye

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["flask", "--app", "app", "--debug", "run", "--host=0.0.0.0", "--port=8000"]
