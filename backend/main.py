import uuid
import tempfile
import shutil
from fastapi import FastAPI, File, Form, UploadFile

from common import AttackParameters
from attack_worker import attack_worker

from BackgroundTasks import BackgroundTasks

app = FastAPI()
program_state = BackgroundTasks()

@app.on_event("startup")
def startup_event():
    program_state.setup(app, attack_worker)
    program_state.start()


@app.on_event("shutdown")
def shutdown_event():
    program_state.shutdown()

@app.get("/api")
def read_root():
    return {"message": "Hello from the backend!"}


# Save the uploaded file to a temporary file on the server
# and return the path to the temporary file
# This under the assumption that PyTorch will be able to load the file from the path
# but cannot load it from the SpooledTemporaryFile (which underlies the UploadFile)
# TODO: check if zip files are needed, or if we can just extract them and use the extracted files
async def save_upload_file_to_temp(upload_file: UploadFile):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    shutil.copyfileobj(upload_file.file, temp_file)
    return temp_file.name


# Since this is for receiving files, the content type should be multipart/form-data
# This means that Swagger UI cannot generate a form for this endpoint, and
# documentation will need to be written manually
# This takes all the parameters necessary for initiating an attack,
# and returns a request token which should be used for subscribing to a websocket endpoint
#   - the endpoint will publish updates on the how the attack is going
@app.post("/api/submit-attack")
async def submit_attack(
    ptFile: UploadFile = File(None),
    zipFile: UploadFile = File(None),
    model: str = Form(...),
    datasetStructure: str = Form(...),
    csvPath: str = Form(None),
    datasetSize: int = Form(...),
    numClasses: int = Form(...),
    batchSize: int = Form(...),
    numRestarts: int = Form(...),
    stepSize: int = Form(...),
    maxIterations: int = Form(...),
    callbackInterval: int = Form(...),
):
    request_token = str(uuid.uuid4())

    # Register the route for the request token, so that the frontend can subscribe to it

    attack_params = AttackParameters(
        model,
        datasetStructure,
        csvPath,
        datasetSize,
        numClasses,
        batchSize,
        numRestarts,
        stepSize,
        maxIterations,
        callbackInterval,
    )

    if ptFile is not None:
        ptTempFilePath = await save_upload_file_to_temp(ptFile)
        attack_params.ptFilePath = ptTempFilePath

    if zipFile is not None:
        zipTempFilePath = await save_upload_file_to_temp(zipFile)
        attack_params.zipFilePath = zipTempFilePath

    program_state.worker_queues.put_task(request_token, attack_params)
    await program_state._psw.register_route(request_token)

    return request_token
