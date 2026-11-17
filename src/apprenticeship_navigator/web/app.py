from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

from apprenticeship_navigator.models.applicant_view import RunView
from apprenticeship_navigator.runs import NotAwaitingReview, resume_run, start_run
from apprenticeship_navigator.web.views import run_view

app = FastAPI(title="Apprenticeship Navigator (demonstration)")


class StartRequest(BaseModel):
    postcode: str = Field(max_length=10)
    distance_in_miles: int = Field(default=10, ge=1)


@app.post("/runs")
async def start(request: StartRequest) -> RunView:
    run_id, result = await start_run(request.postcode, request.distance_in_miles)
    return run_view(result, run_id)


class DecisionRequest(BaseModel):
    decision: Literal["approve", "reject"]


@app.post("/runs/{run_id}/decision")
async def decide(run_id: str, request: DecisionRequest) -> RunView:
    try:
        result = await resume_run(run_id, request.decision)
    except NotAwaitingReview:
        raise HTTPException(status_code=409, detail="This run is not awaiting review.")
    return run_view(result, run_id)
