FROM python:3.5.1

# System packages
RUN apt-key update && apt-get update
#Supervisor for running application in production
RUN apt-get install supervisor -y
# Clean up package manager
RUN apt-get autoremove -y
RUN rm -rvf /var/cache/apt

# Environment variables
ENV PYTHONUNBUFFERED 1

# Directories
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt

# Default entrypoint
ENTRYPOINT "/code/scripts/run_prod.sh"
