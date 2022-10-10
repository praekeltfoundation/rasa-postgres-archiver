FROM ghcr.io/praekeltfoundation/python-base-nw:3.9-bullseye

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "run.py"]
