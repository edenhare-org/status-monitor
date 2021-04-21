from functions.generateAssessmentNumber import app

event = {}
event['Report'] = {}
event['Status'] = {}

def test_assessment_number():

    data = app.lambda_handler(event, "")

    assert "number" in data['Status']
    assert "AssessmentNumber" in data['Report']

    assert data["Status"]['number'] == 200
    assert data["Report"]['AssessmentNumber'] != ""

