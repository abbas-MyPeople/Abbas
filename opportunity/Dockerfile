FROM python:3.12-slim

WORKDIR /app

COPY opportunity/requirements.txt opportunity/requirements.txt
RUN pip install --no-cache-dir -r opportunity/requirements.txt

# The pipeline reuses outreach/collect.py, so both packages ship.
COPY opportunity/ opportunity/
COPY outreach/ outreach/

ENV PYTHONUNBUFFERED=1 OPP_STATE_DIR=/data

EXPOSE 8080

# One worker on purpose: the rate-limit window is in-process, so extra workers
# would each keep their own and the effective limit would multiply.
CMD ["gunicorn", "--workers", "1", "--threads", "8", "--timeout", "120", \
     "--bind", "0.0.0.0:8080", "opportunity.server:app"]
