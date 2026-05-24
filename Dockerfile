FROM python:3.11-slim

WORKDIR /app

COPY python/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY python ./python
COPY data ./data

EXPOSE 5000

CMD ["python", "python/app.py"]
