import pytest

import app as app_module


@pytest.fixture
def client():
    app = app_module.app

    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key-for-download-tests",
    )

    with app.test_client() as test_client:
        yield test_client


def valid_analysis():
    return {
        "ats_score": {
            "score": 72,
            "breakdown": [
                {
                    "factor": "Skills",
                    "points": 30,
                    "max_points": 40,
                    "note": "Good technical skill coverage.",
                },
                {
                    "factor": "Experience",
                    "points": 20,
                    "max_points": 30,
                    "note": "Relevant experience detected.",
                },
            ],
        },
        "match_score": {
            "match_percent": 65,
            "matched_keywords": ["python", "sql"],
            "missing_keywords": ["aws"],
        },
        "missing_skills": {
            "missing_by_category": {
                "cloud_platforms": ["aws"],
            },
            "total_missing": 1,
        },
        "keyword_analysis": {
            "resume_keywords": ["python", "sql"],
            "jd_keywords": ["python", "sql", "aws"],
        },
    }


def valid_ai_suggestions():
    return {
        "overall_feedback": (
            "Your resume has a solid technical foundation."
        ),
        "strengths": [
            "Clear technical skills",
            "Relevant project experience",
        ],
        "priority_improvements": [
            {
                "area": "Cloud",
                "suggestion": "Add practical AWS experience.",
                "example": "Mention an AWS deployment project.",
            }
        ],
        "skills_to_highlight": ["Python", "SQL"],
        "tone_notes": "Professional and concise.",
    }


def put_report_in_session(client):
    with client.session_transaction() as session:
        session["analysis"] = valid_analysis()
        session["ai_suggestions"] = valid_ai_suggestions()


def test_download_report_route_exists(client):
    routes = [
        rule.rule
        for rule in app_module.app.url_map.iter_rules()
    ]

    assert "/download-report" in routes


def test_download_report_requires_post(client):
    response = client.get("/download-report")

    assert response.status_code in (405, 302)


def test_download_report_success(client, monkeypatch):
    put_report_in_session(client)

    expected_pdf = b"%PDF-1.4\nHireLens test PDF\n"

    def fake_generate_pdf_report(
        analysis,
        ai_suggestions,
    ):
        assert analysis == valid_analysis()
        assert ai_suggestions == valid_ai_suggestions()

        return expected_pdf

    monkeypatch.setattr(
        app_module,
        "generate_pdf_report",
        fake_generate_pdf_report,
    )

    response = client.post("/download-report")

    assert response.status_code == 200
    assert response.data == expected_pdf
    assert response.mimetype == "application/pdf"
    assert "attachment" in response.headers["Content-Disposition"]
    assert (
        "HireLens_Report.pdf"
        in response.headers["Content-Disposition"]
    )


def test_download_report_missing_analysis(client):
    with client.session_transaction() as session:
        session["ai_suggestions"] = valid_ai_suggestions()

    response = client.post("/download-report")

    assert response.status_code != 500
    assert response.status_code in (302, 400)


def test_download_report_missing_ai_suggestions(client):
    with client.session_transaction() as session:
        session["analysis"] = valid_analysis()

    response = client.post("/download-report")

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"


def test_download_report_empty_session(client):
    response = client.post("/download-report")

    assert response.status_code != 500
    assert response.status_code in (302, 400)


def test_download_report_malformed_analysis(client):
    with client.session_transaction() as session:
        session["analysis"] = "not-a-dictionary"
        session["ai_suggestions"] = valid_ai_suggestions()

    response = client.post("/download-report")

    assert response.status_code != 500
    assert response.status_code in (302, 400)


def test_download_report_malformed_ai_suggestions(client):
    with client.session_transaction() as session:
        session["analysis"] = valid_analysis()
        session["ai_suggestions"] = "not-a-dictionary"

    response = client.post("/download-report")

    assert response.status_code != 500
    assert response.status_code in (302, 400)


def test_download_report_none_analysis(client):
    with client.session_transaction() as session:
        session["analysis"] = None
        session["ai_suggestions"] = valid_ai_suggestions()

    response = client.post("/download-report")

    assert response.status_code != 500
    assert response.status_code in (302, 400)


def test_download_report_none_ai_suggestions(client):
    with client.session_transaction() as session:
        session["analysis"] = valid_analysis()
        session["ai_suggestions"] = None

    response = client.post("/download-report")

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"


def test_home_route_still_works(client):
    response = client.get("/")

    assert response.status_code == 200


def test_health_route_still_works(client):
    response = client.get("/health")

    assert response.status_code == 200


def test_download_report_does_not_expose_secret(client):
    put_report_in_session(client)

    with client.application.test_request_context():
        client.application.config["SECRET_KEY"] = (
            "super-secret-test-value"
        )

    response = client.post("/download-report")

    assert b"super-secret-test-value" not in response.data


def test_download_report_does_not_expose_internal_exception(
    client,
    monkeypatch,
):
    put_report_in_session(client)

    def failing_generator(
        analysis,
        ai_suggestions,
    ):
        raise RuntimeError(
            "internal PDF generation failure"
        )

    monkeypatch.setattr(
        app_module,
        "generate_pdf_report",
        failing_generator,
    )

    response = client.post("/download-report")

    assert response.status_code != 500
    assert (
        b"internal PDF generation failure"
        not in response.data
    )


def test_download_report_uses_pdf_generator(
    client,
    monkeypatch,
):
    put_report_in_session(client)

    called = {"value": False}

    def fake_generate_pdf_report(
        analysis,
        ai_suggestions,
    ):
        called["value"] = True

        return b"%PDF-1.4\n"

    monkeypatch.setattr(
        app_module,
        "generate_pdf_report",
        fake_generate_pdf_report,
    )

    response = client.post("/download-report")

    assert response.status_code == 200
    assert called["value"] is True


def test_download_report_returns_bytes(
    client,
    monkeypatch,
):
    put_report_in_session(client)

    monkeypatch.setattr(
        app_module,
        "generate_pdf_report",
        lambda analysis, ai_suggestions: bytes(
            b"%PDF-1.4\n"
        ),
    )

    response = client.post("/download-report")

    assert isinstance(response.data, bytes)


def test_download_report_preserves_analysis_data(
    client,
    monkeypatch,
):
    put_report_in_session(client)

    captured = {}

    def fake_generate_pdf_report(
        analysis,
        ai_suggestions,
    ):
        captured["analysis"] = analysis
        captured["ai_suggestions"] = ai_suggestions

        return b"%PDF-1.4\n"

    monkeypatch.setattr(
        app_module,
        "generate_pdf_report",
        fake_generate_pdf_report,
    )

    response = client.post("/download-report")

    assert response.status_code == 200
    assert captured["analysis"]["ats_score"]["score"] == 72
    assert (
        captured["ai_suggestions"]["skills_to_highlight"]
        == ["Python", "SQL"]
    )


def test_download_report_content_type(
    client,
    monkeypatch,
):
    put_report_in_session(client)

    monkeypatch.setattr(
        app_module,
        "generate_pdf_report",
        lambda analysis, ai_suggestions: b"%PDF-1.4\n",
    )

    response = client.post("/download-report")

    assert response.headers["Content-Type"].startswith(
        "application/pdf"
    )


def test_download_report_content_disposition(
    client,
    monkeypatch,
):
    put_report_in_session(client)

    monkeypatch.setattr(
        app_module,
        "generate_pdf_report",
        lambda analysis, ai_suggestions: b"%PDF-1.4\n",
    )

    response = client.post("/download-report")

    disposition = response.headers["Content-Disposition"]

    assert "attachment" in disposition
    assert "HireLens_Report.pdf" in disposition


def test_download_report_pdf_signature(
    client,
    monkeypatch,
):
    put_report_in_session(client)

    monkeypatch.setattr(
        app_module,
        "generate_pdf_report",
        lambda analysis, ai_suggestions: (
            b"%PDF-1.7\nTest\n%%EOF"
        ),
    )

    response = client.post("/download-report")

    assert response.status_code == 200
    assert response.data.startswith(b"%PDF")


def test_download_report_does_not_store_resume_text(client):
    put_report_in_session(client)

    with client.session_transaction() as session:
        assert "extracted_text" not in session
        assert "resume_text" not in session


def test_download_report_session_contains_required_data(
    client,
):
    put_report_in_session(client)

    with client.session_transaction() as session:
        assert isinstance(session["analysis"], dict)
        assert isinstance(
            session["ai_suggestions"],
            dict,
        )
        assert "ats_score" in session["analysis"]
        assert (
            "overall_feedback"
            in session["ai_suggestions"]
        )


def test_download_report_does_not_modify_session_data(
    client,
    monkeypatch,
):
    put_report_in_session(client)

    monkeypatch.setattr(
        app_module,
        "generate_pdf_report",
        lambda analysis, ai_suggestions: b"%PDF-1.4\n",
    )

    client.post("/download-report")

    with client.session_transaction() as session:
        assert (
            session["analysis"]["ats_score"]["score"]
            == 72
        )
        assert (
            session["ai_suggestions"]["overall_feedback"]
            == "Your resume has a solid technical foundation."
        )


def test_download_report_handles_empty_pdf_bytes(
    client,
    monkeypatch,
):
    put_report_in_session(client)

    monkeypatch.setattr(
        app_module,
        "generate_pdf_report",
        lambda analysis, ai_suggestions: b"",
    )

    response = client.post("/download-report")

    assert response.status_code != 500
    assert response.status_code in (302, 400)