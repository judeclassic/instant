FROM python:3.9
COPY ./ ./
RUN pip install schedule
RUN pip install instagrapi

CMD [ "python", "./app/__init__.py" ]