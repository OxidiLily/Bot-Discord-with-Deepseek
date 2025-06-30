FROM python:3.12-alpine

WORKDIR /BotDiscord

COPY *.env .

# Install dependencies only
RUN pip install --no-cache-dir discord.py openai python-dotenv

COPY . .

CMD ["python", "main.py"]