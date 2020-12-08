FROM praekeltfoundation/python-base:3.7

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "run.py"]
