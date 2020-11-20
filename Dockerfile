FROM cybexp-priv-libs

# setup environment & install dependencies
COPY ./requirements.txt /backend-server/requirements.txt
RUN pip3 install -r /backend-server/requirements.txt

# misc
RUN mkdir -p /secrets

# copy backend-server last
COPY ./backend-server /backend-server

WORKDIR /backend-server
EXPOSE 5000

CMD ["/usr/bin/python3", "/backend-server/server.py"] 

