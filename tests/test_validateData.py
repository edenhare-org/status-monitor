from functions.validateData import app


test_data = {}
# test_data["Name"] = "my name"
# test_data["Email"] = "chris.hare@icloud.com"
# test_data["Gender"] = "male"
# test_data["BirthYear"] = "1962"
# test_data["School"] = "N"
# test_data["Institution"] = "None"
# test_data["Previous"] = "Yes"
# test_data["Country"] = "United States"


def test_catch_no_data():

    data = app.lambda_handler({}, "")

    assert "validate" in data['Status']

    assert data['Status']["validate"] == 400


def test_catch_no_Name():

    test_data = {}
    # test_data["Name"] = "my name"
    test_data["Email"] = "chris.hare@icloud.com"
    test_data["Gender"] = "male"
    test_data["BirthYear"] = "1962"
    test_data["School"] = "N"
    test_data["Institution"] = "None"
    test_data["Previous"] = "Yes"
    test_data["Country"] = "United States"

    data = app.lambda_handler(test_data, "")

    assert "validate" in data['Status']

    assert data['Status']["validate"] == 801


def test_catch_blank_Name():

    test_data = {}
    test_data["Name"] = ""
    test_data["Email"] = "chris.hare@icloud.com"
    test_data["Gender"] = "male"
    test_data["BirthYear"] = "1962"
    test_data["School"] = "N"
    test_data["Institution"] = "None"
    test_data["Previous"] = "Yes"
    test_data["Country"] = "United States"

    data = app.lambda_handler(test_data, "")

    assert "validate" in data['Status']

    assert data['Status']["validate"] == 801


def test_catch_no_Email():

    test_data = {}
    test_data["Name"] = "my name"
    # test_data["Email"] = "chris.hare@icloud.com"
    test_data["Gender"] = "male"
    test_data["BirthYear"] = "1962"
    test_data["School"] = "N"
    test_data["Institution"] = "None"
    test_data["Previous"] = "Yes"
    test_data["Country"] = "United States"

    data = app.lambda_handler(test_data, "")

    assert "validate" in data['Status']

    assert data['Status']["validate"] == 801


def test_catch_blank_Email():

    test_data = {}
    test_data["Name"] = ""
    test_data["Email"] = ""
    test_data["Gender"] = "male"
    test_data["BirthYear"] = "1962"
    test_data["School"] = "N"
    test_data["Institution"] = "None"
    test_data["Previous"] = "Yes"
    test_data["Country"] = "United States"

    data = app.lambda_handler(test_data, "")

    assert "validate" in data['Status']

    assert data['Status']["validate"] == 801


def test_catch_invalid_Email():

    test_data = {}
    test_data["Name"] = ""
    test_data["Email"] = "chris.hare#icloud.com"
    test_data["Gender"] = "male"
    test_data["BirthYear"] = "1962"
    test_data["School"] = "N"
    test_data["Institution"] = "None"
    test_data["Previous"] = "Yes"
    test_data["Country"] = "United States"

    data = app.lambda_handler(test_data, "")

    assert "validate" in data['Status']

    assert data['Status']["validate"] == 801


def test_catch_missing_Institution():

    test_data = {}
    test_data["Name"] = "my name"
    test_data["Email"] = "chris.hare@icloud.com"
    test_data["Gender"] = "male"
    test_data["BirthYear"] = "1962"
    test_data["School"] = "N"
    #test_data["Institution"] = "None"
    test_data["Previous"] = "Yes"
    test_data["Country"] = "United States"

    data = app.lambda_handler(test_data, "")

    assert "validate" in data['Status']

    assert data['Status']["validate"] == 801

# blocked out - blank institution name is for now ok.
# def test_catch_blank_Institution():

    # test_data = {}
    # test_data["Name"] = "my name"
    # test_data["Email"] = "chris.hare@icloud.com"
    # test_data["Gender"] = "male"
    # test_data["BirthYear"] = "1962"
    # test_data["School"] = "N"
    # test_data["Institution"] = ""
    # test_data["Previous"] = "Yes"
    # test_data["Country"] = "United States"

    # data = app.lambda_handler(test_data, "")

    # assert "statusCode" in data
    # assert data["statusCode"] == 400


def test_verify_version2():

    test_data = {}
    test_data["Name"] = "my name"
    test_data["Email"] = "chris.hare@icloud.com"
    test_data["Gender"] = "male"
    test_data["BirthYear"] = "1962"
    test_data["School"] = "N"
    test_data["Institution"] = ""
    test_data["Previous"] = "Yes"
    test_data["Country"] = "United States"

    data = app.lambda_handler(test_data, "")

    assert "validate" in data['Status']

    assert data['Status']["validate"] == 200

    assert "Version" in data
    assert data["Version"] == "2"


def test_verify_good_set():

    event = {}
    event["Name"] = "my name"
    event["Email"] = "chris.hare@icloud.com"
    event["Gender"] = "male"
    event["BirthYear"] = "1962"
    event["School"] = "N"
    event["Institution"] = "None"
    event["Previous"] = "Yes"
    event["Country"] = "United States"
    event["q1a"] = 1
    event["q1b"] = 2
    event["q1c"] = 3
    event["q1d"] = 1
    event["q1e"] = 4
    event["q2a"] = 5
    event["q2b"] = 6
    event["q2c"] = 7
    event["q2d"] = 2
    event["q2e"] = 1
    event["q3a"] = 4
    event["q3b"] = 3
    event["q3c"] = 2
    event["q3d"] = 5
    event["q3e"] = 2
    event["q4a"] = 6
    event["q4b"] = 7
    event["q4c"] = 1
    event["q4d"] = 7
    event["q4e"] = 2
    event["q5a"] = 6
    event["q5b"] = 3
    event["q5c"] = 5
    event["q5d"] = 4
    event["q5e"] = 4
    event["q6a"] = 5
    event["q6b"] = 3
    event["q6c"] = 6
    event["q6d"] = 2
    event["q6e"] = 7
    event["q7a"] = 1
    event["q7b"] = 1
    event["q7c"] = 2
    event["q7d"] = 3
    event["q7e"] = 4
    event["q8a"] = 5
    event["q8b"] = 6
    event["q8c"] = 7
    event["q8d"] = 1
    event["q8e"] = 2
    event["q9a"] = 3
    event["q9b"] = 4
    event["q9c"] = 5
    event["q9d"] = 6
    event["q9e"] = 7
    event["q10a"] = 7
    event["q10b"] = 6
    event["q10c"] = 5
    event["q10d"] = 4
    event["q10e"] = 3
    event["q11a"] = 2
    event["q11b"] = 1
    event["q11c"] = 1
    event["q11d"] = 1
    event["q11e"] = 2
    event["q12a"] = 3
    event["q12b"] = 4
    event["q12c"] = 5
    event["q12d"] = 6
    event["q12e"] = 7
    event["q13a"] = 6
    event["q13b"] = 7
    event["q13c"] = 6
    event["q13d"] = 5
    event["q13e"] = 4
    event["q14a"] = 3
    event["q14b"] = 2
    event["q14c"] = 1
    event["q14d"] = 7
    event["q14e"] = 2
    event["q15a"] = 3
    event["q15b"] = 4
    event["q15c"] = 5
    event["q15d"] = 6
    event["q15e"] = 7

    data = app.lambda_handler(event, "")

    assert "validate" in data['Status']

    assert data['Status']["validate"] == 200
