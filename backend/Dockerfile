FROM continuumio/miniconda3

WORKDIR /app

# Copy just the conda environment file first
COPY environment.yml ./

# Create the conda environment
RUN conda env create -v -f environment.yml

# Copy remaining files to workdir
COPY . .

HEALTHCHECK --interval=5m --timeout=2m --start-period=45s \
   CMD curl -f --retry 6 --max-time 5 --retry-delay 10 --retry-max-time 60 "http://localhost:8000/health" || bash -c 'kill -s 15 -1 && (sleep 10; kill -s 9 -1)'

CMD conda run --no-capture-output -vvv -n breaching uvicorn main:app --host 0.0.0.0 --port 8000
