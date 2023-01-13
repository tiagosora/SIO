FROM tiangolo/uwsgi-nginx:python3.8

COPY . /api_sec
WORKDIR /api_sec

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV STATIC_URL ./static
ENV STATIC_PATH /api_sec/static

ENV FLASK_APP=api
ENV FLASK_DEBUG=0

EXPOSE 5000

CMD ["python3", "api.py"]