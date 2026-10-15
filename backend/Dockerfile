FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home cybercare && chown -R cybercare:cybercare /app
USER cybercare
CMD ["python", "-m", "app.start"]
