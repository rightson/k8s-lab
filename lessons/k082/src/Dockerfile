ARG BASE_IMAGE
FROM ${BASE_IMAGE}
WORKDIR /app
COPY api.py /app/api.py
USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["python", "-u", "/app/api.py"]

