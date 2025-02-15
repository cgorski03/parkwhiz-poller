FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

# Make the script executable
RUN chmod +x parkwhiz_bot.py

# Command to run the application
CMD ["python3", "parkwhiz_bot.py"]
