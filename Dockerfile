FROM osgeo/gdal:ubuntu-small-3.4.1
RUN apt-get update && apt-get install python3-pip -y
RUN adduser user
USER user
COPY requirements.txt /tmp/requirements.txt
ENV PATH=/home/user/.local/bin/:$PATH
RUN pip install -r /tmp/requirements.txt
COPY --chown=user ./app /home/user/app
WORKDIR /home/user/app
EXPOSE 8888
CMD [ "jupyter", "notebook", "--ip", "0.0.0.0"]