from functions.generateAssessmentDate import app
import datetime

now = datetime.datetime.now()
current = f"{now.month}/{now.day}/{now.year}"
event = {}
event['Report'] = {}
event['Status'] = {}
event['Report']['AssessmentDate'] = f"{now.month}/{now.day}/{now.year}"

def test_assessment_date_exists():

    data = app.lambda_handler(event, "")

    assert "date" in data['Status']
    assert "AssessmentDate" in data['Report']

    assert data["Status"]['date'] == 200
    assert data["Report"]['AssessmentDate'] != ""


def test_assessment_date_match():

    data = app.lambda_handler(event, "")

    assert "date" in data['Status']
    assert "AssessmentDate" in data['Report']

    assert data["Status"]['date'] == 200
    assert data["Report"]['AssessmentDate'] == current
