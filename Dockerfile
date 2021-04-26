FROM python:3.8.9-alpine as Env
WORKDIR /app
COPY requirements.txt .
RUN set -x \
    && apk add --no-cache --upgrade -t build-deps gcc musl-dev \
    && python3 -m pip install --no-cache-dir -r ./requirements.txt \
    && apk del --no-cache --purge build-deps

FROM Env as Server
COPY . .
RUN chmod +x ./start.sh
CMD ./start.sh
