"""Routes: the selector and the report page."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import sources
from .reports import industry_sentiment as sentiment
from .store import DEFAULT_DB, EvidenceStore

BASE_DIR = Path(__file__).parent

app = FastAPI(title="Research workspace", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def get_store() -> EvidenceStore:
    return EvidenceStore(DEFAULT_DB)


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    with get_store() as store:
        empty = store.count() == 0
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "subjects": sentiment.SUBJECTS,
            "windows": sentiment.WINDOWS,
            "all_sources": list(sources.REGISTRY.values()),
            "unconnected": sources.unconnected_sources(),
            "store_empty": empty,
        },
    )


@app.get("/report", response_class=HTMLResponse)
def report(
    request: Request,
    subject: str = Query(default=sentiment.SUBJECTS[0]),
    window: str = Query(default="1m"),
    question: str = Query(default=""),
    as_of: date | None = Query(default=None),
) -> HTMLResponse:
    if subject not in sentiment.SUBJECTS:
        subject = sentiment.SUBJECTS[0]
    if window not in sentiment.WINDOWS:
        window = "1m"

    with get_store() as store:
        built = sentiment.build(
            store,
            sentiment.ReportRequest(
                subject=subject,
                window=window,
                research_question=question.strip() or sentiment.default_question(subject),
                # A fixed as_of keeps a report reproducible; it defaults to the latest
                # period the store actually covers rather than to today, so a report
                # generated after a quiet week is not silently empty.
                as_of=as_of or _latest_period(store, subject),
            ),
        )
        return templates.TemplateResponse(
            request=request, name="report.html", context={"report": built}
        )


def _latest_period(store: EvidenceStore, subject: str) -> date:
    records = store.query(subject=subject)
    return max((r.period_end for r in records), default=date.today())
