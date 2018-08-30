FROM python:3-slim
COPY . /code
WORKDIR /code
RUN pip install -e .[api]
CMD ["python", "iam_profile_faker/v2_api.py"]
