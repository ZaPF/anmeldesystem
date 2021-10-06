FROM python:3
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt
COPY ./app /app/app
COPY ./config.py /app/config.py
ENV FLASK_APP=app
ENV FLASK_ENV=development
EXPOSE 5000
ENTRYPOINT [ "flask" ]
CMD [ "run", "-h", "0.0.0.0" ]