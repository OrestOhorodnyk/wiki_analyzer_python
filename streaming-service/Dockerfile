# set base image (host OS)
FROM python:3.9

# set the working directory in the container
WORKDIR /streaming-service

# install netcat
RUN apt-get update && apt-get install -y netcat

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY app/ ./app

# command to run on container start
CMD [ "python", "-m", "app.main" ]