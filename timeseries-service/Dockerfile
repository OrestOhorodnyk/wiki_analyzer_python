FROM python:3.9-slim

WORKDIR /timeseries-service

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python" , "-m", "app" ]