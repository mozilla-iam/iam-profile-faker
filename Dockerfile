FROM python:3-slim
COPY . /code
WORKDIR /code
RUN pip install . flask==1.0.2 flask_restful==0.3.6 
CMD ["python", "iam_profile_faker/v2_api.py"]
