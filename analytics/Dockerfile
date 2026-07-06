# Hugging Face Space (Docker SDK) — AZ Restaurant Partners "Analytics"
# Runs the guarded Flask GA4 dashboard. HF serves on port 7860.
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV PORT=7860
EXPOSE 7860

# Secrets are provided as Space Secrets (env vars), never baked into the image:
#   GA4_PROPERTY_ID, GA4_SA_JSON, AUTH_USER, AUTH_PASS, (optional) GROQ_API_KEY
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:7860", "--timeout", "120", "--workers", "2"]
