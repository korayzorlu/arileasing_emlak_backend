FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# No apt packages needed — every dependency in requirements.txt ships a prebuilt wheel
# for this image's platform, so there's nothing here that actually needs a C compiler.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh && python manage.py collectstatic --noinput

EXPOSE 8000

# Invoked via "sh" rather than executed directly: the app dir is now bind-mounted live
# (see docker-compose.yml), so the executable bit baked in above no longer travels with
# it — the host's copy of entrypoint.sh is what actually runs, and its permissions can
# vary (e.g. a fresh git checkout). Reading it as a shell script sidesteps that entirely.
ENTRYPOINT ["sh", "./entrypoint.sh"]
