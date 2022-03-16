FROM osgeo/gdal:ubuntu-small-3.4.1
RUN apt-get update && apt-get install python3-pip python3-rtree python3-gdal -y
RUN adduser user
USER user
COPY requirements.txt /tmp/requirements.txt
ENV PATH=/home/user/.local/bin/:$PATH
RUN pip install -r /tmp/requirements.txt
RUN mkdir ~/app
COPY --chown=user ./app /home/user/app
WORKDIR /home/user/app
# EXPOSE 8888
CMD ["python3", "map_tiles_downloader.py"]
# CMD [ "jupyter", "notebook", "--ip", "0.0.0.0"]