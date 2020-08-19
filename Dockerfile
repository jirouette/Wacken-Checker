FROM python:3-alpine

ADD requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ADD wacken-checker.py .

VOLUME reports

CMD ["python", "-u", "wacken-checker.py"]
