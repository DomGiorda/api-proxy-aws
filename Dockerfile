FROM python:3.13.2-alpine3.21

WORKDIR /proxy
COPY . /proxy
RUN pip install -r requirements.txt

EXPOSE 8080
CMD ["python", "main.py"]