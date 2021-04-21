from functions.database import app

event = {}
from .sample import event

event['action'] = "insert"

def test_connectToDatabase():

    data = app.lambda_handler(event, "")

    # assert "number" in data['Status']
    # assert "AssessmentNumber" in data['Report']

    assert data["Status"]['Database'] == 200
    # assert data["Report"]['AssessmentNumber'] != ""

def test_insert():
    
    data = app.lambda_handler(event, "")

    # assert "number" in data['Status']
    # assert "AssessmentNumber" in data['Report']

    assert data["Status"]['Database'] == 200
    # assert data["Report"]['AssessmentNumber'] != ""