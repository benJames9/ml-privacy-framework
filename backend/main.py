import uuid
import tempfile
import shutil
from fastapi import FastAPI, File, Form, UploadFile

from common import AttackParameters, BreachingParams, MiaParams
from attack_worker import attack_worker

from BackgroundTasks import BackgroundTasks

app = FastAPI()
background_task_manager = BackgroundTasks()


@app.on_event("startup")
def startup_event():
    background_task_manager.setup(app, attack_worker)
    background_task_manager.start()


@app.on_event("shutdown")
def shutdown_event():
    background_task_manager.shutdown()


@app.get("/health")
def health_check():
    return 1


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
    attack: str = Form(...),
    modality: str = Form(...),
    # Model Inversion Params
    batchSize: int = Form(None),
    mean: str = Form(None),
    std: str = Form(None),
    numRestarts: int = Form(None),
    stepSize: float = Form(None),
    maxIterations: int = Form(None),
    # Text attack parameters
    textDataset: str = Form(None),
    textDataPoints: int = Form(None),
    seqLength: int = Form(None),
    tokenizer: str = Form(None),
    # MIA attack parameters
    labelDict: UploadFile = File(None),
    targetImage: UploadFile = File(None),
    targetLabel: str = Form(None),
    numShadowModels: int = Form(None),
    numDataPoints: int = Form(None),
    numEpochs: int = Form(None),
    shadowBatchSize: int = Form(None),
    learningRate: float = Form(None),
):
    request_token = str(uuid.uuid4())

    # Register the route for the request token, so that the frontend can subscribe to it

    ptTempFilePath, zipTempFilePath = None, None
    if ptFile is not None:
        ptTempFilePath = await save_upload_file_to_temp(ptFile)
    if zipFile is not None:
        zipTempFilePath = await save_upload_file_to_temp(zipFile)

    breaching_params = None
    mia_params = None

    if attack == "mia":
        if labelDict is not None:
            labelDictPath = await save_upload_file_to_temp(labelDict)
        if targetImage is not None:
            targetImagePath = await save_upload_file_to_temp(targetImage)

        mia_params = MiaParams(
            N=numShadowModels,
            data_points=numDataPoints,
            epochs=numEpochs,
            batch_size=shadowBatchSize,
            lr=learningRate,
            target_label=targetLabel,
            target_image_path=targetImagePath,
            path_to_label_csv=labelDictPath,
        )

    else:
        if modality == "images":
            breaching_params = BreachingParams(
                modality=modality,
                batchSize=batchSize,
                means=[float(i) for i in mean.strip("[]").split(",")],
                stds=[float(i) for i in std.strip("[]").split(",")],
                numRestarts=numRestarts,
                stepSize=stepSize,
                maxIterations=maxIterations,
            )
        elif modality == "text":
            print(
                f"modality: {modality}, textDataset: {textDataset}, textDataPoints: {textDataPoints}, seqLength: {seqLength}, tokenizer: {tokenizer}, numRestarts: {numRestarts}, stepSize: {stepSize}, maxIterations: {maxIterations}"
            )
            breaching_params = BreachingParams(
                modality=modality,
                textDataset=textDataset,
                textDataPoints=textDataPoints,
                seqLength=seqLength,
                tokenizer=tokenizer,
                numRestarts=numRestarts,
                stepSize=stepSize,
                maxIterations=maxIterations,
            )

    attack_params = AttackParameters(
        model=model,
        attack=attack,
        breaching_params=breaching_params,
        mia_params=mia_params,
        ptFilePath=ptTempFilePath,
        zipFilePath=zipTempFilePath,
    )

    await background_task_manager.submit_task(request_token, attack_params)
    await background_task_manager._psw.register_route(request_token)

    return request_token


# Cancel an attack associated with token
@app.post(f"/api/cancel/{{request_token}}")
async def cancel_attack(request_token: str):
    await background_task_manager.cancel_task(request_token)
