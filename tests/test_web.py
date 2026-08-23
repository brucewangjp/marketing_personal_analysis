"""The pages must show what the contract requires a reader to see."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app import main
from app.sample import all_records
from app.store import EvidenceStore


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = tmp_path / "evidence.db"
    with EvidenceStore(db) as store:
        store.add_all(all_records())
    monkeypatch.setattr(main, "get_store", lambda: EvidenceStore(db))
    return TestClient(main.app)


@pytest.fixture
def empty_client(tmp_path, monkeypatch):
    db = tmp_path / "empty.db"
    EvidenceStore(db).close()
    monkeypatch.setattr(main, "get_store", lambda: EvidenceStore(db))
    return TestClient(main.app)


def test_index_lists_subjects_and_windows(client):
    body = client.get("/").text
    assert "US technology" in body
    assert "US healthcare" in body
    assert "most recent one month" in body
    assert "most recent three months" in body


def test_index_shows_source_connection_state(client):
    body = client.get("/").text
    assert "connected" in body
    assert "not connected" in body


def test_index_warns_when_the_store_is_empty(empty_client):
    assert "evidence store is empty" in empty_client.get("/").text


def test_report_renders(client):
    response = client.get("/report", params={"subject": "US technology", "window": "3m"})
    assert response.status_code == 200
    assert "Attention trend" in response.text


def test_report_shows_the_gate_message_for_unconnected_sources(client):
    body = client.get("/report", params={"subject": "US technology"}).text
    assert "Insufficient evidence" in body
    assert "Public discussion" in body
    assert "which is not connected" in body


def test_report_labels_sample_data(client):
    body = client.get("/report", params={"subject": "US technology"}).text
    assert "sample evidence" in body


def test_report_distinguishes_record_types(client):
    body = client.get("/report", params={"subject": "US technology", "window": "3m"}).text
    assert "tag-observation" in body
    assert "tag-derived-metric" in body


def test_report_shows_confidence_levels_and_reasons(client):
    body = client.get("/report", params={"subject": "US technology", "window": "3m"}).text
    assert "Why this level" in body
    assert "conf-medium" in body or "conf-low" in body


def test_report_shows_the_evidence_table_with_periods_and_retrieval_dates(client):
    body = client.get("/report", params={"subject": "US technology", "window": "3m"}).text
    assert "Evidence and confidence" in body
    assert "Retrieved" in body
    assert "sample.fred" in body


def test_report_renders_a_chart(client):
    body = client.get("/report", params={"subject": "US technology", "window": "3m"}).text
    assert "<svg" in body
    assert 'class="chart"' in body


def test_report_accepts_a_custom_question(client):
    body = client.get(
        "/report", params={"subject": "US technology", "question": "Who is hiring?"}
    ).text
    assert "Who is hiring?" in body


def test_unknown_subject_falls_back_rather_than_erroring(client):
    response = client.get("/report", params={"subject": "US energy"})
    assert response.status_code == 200
    assert "US technology" in response.text


def test_report_on_an_empty_store_still_renders_every_section(empty_client):
    body = empty_client.get("/report", params={"subject": "US technology"}).text
    assert "Executive summary" in body
    assert "Attention trend" in body
    assert "Monitoring list" in body
    assert "Insufficient evidence" in body


def test_static_css_is_served(client):
    response = client.get("/static/style.css")
    assert response.status_code == 200
    assert "--conf-high" in response.text


def test_monitoring_items_render_without_a_record_type_tag(client):
    body = client.get("/report", params={"subject": "US technology", "window": "3m"}).text
    monitoring = body.split('id="monitoring"')[1].split("</section>")[0]
    assert "search interest" in monitoring.lower()
    assert "tag-observation" not in monitoring
