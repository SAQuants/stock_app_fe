FROM python:3.10-slim as compiler
ENV PYTHONUNBUFFERED 1
RUN apt update && apt install python3-pip -y

WORKDIR /app/

RUN python -m venv /app/venv
# Enable venv
ENV PATH="/app/venv/bin:$PATH"

COPY ./requirements.txt /app/requirements.txt
# RUN pip install -Ur requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt


FROM python:3.10-slim as runner
WORKDIR /app/
COPY --from=compiler /app/venv /app/venv

# Enable venv
ENV PATH="/app/venv/bin:$PATH"

ENTRYPOINT []
COPY . /app/
CMD python -m streamlit run frontend_streamlit.py
