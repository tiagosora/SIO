FROM tiangolo/uwsgi-nginx:python3.8

COPY . /api
WORKDIR /api

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV STATIC_URL ./static
ENV STATIC_PATH /api/static

ENV FLASK_APP=api
ENV FLASK_DEBUG=1

EXPOSE 5000

CMD ["python3", "api.py"]