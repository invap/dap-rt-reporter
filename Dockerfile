FROM ubuntu:24.10

RUN apt update && apt install -y \
python3 \
pipx \
build-essential \
gdb \
python-is-python3


RUN pipx install poetry 

ENV PATH="$PATH:~/.local/bin"

WORKDIR /home/workspace
