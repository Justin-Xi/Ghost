# Use the specified base image
FROM python:3.11-slim

# Set the author label
LABEL authors="xiajiayi"

# Any additional instructions or configurations can be added here
# 添加环境变量
ENV OPENAI_API_TYPE=azure
ENV OPENAI_API_VERSION=2023-12-01-preview
ENV OPENAI_API_KEY=2e11e2c0e0e041f2b46f6be90b0fb712
ENV OPENAI_API_BASE=https://loox-australia-east.openai.azure.com
# Example: Copy your application code into the image
COPY . /app

# Example: Set the working directory
WORKDIR /app
RUN pip3 install --upgrade pip -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
# Example: Install dependencies
RUN pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# Example: Expose a port
EXPOSE 8004

# Example: Define the command to run your application
#CMD ["uvicorn", "websocket:app", "--ssl-keyfile=/app/gui-gpt.key", "--ssl-certfile=/app/gui-gpt.crt", "--timeout-keep-alive", "0", "--host", "0.0.0.0", "--port", "8004"]
CMD ["uvicorn", "websocket:app", "--host", "0.0.0.0", "--port", "8004"]
#CMD ["python3", "websocket.py"]