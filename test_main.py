from fastapi.testclient import TestClient
import io
import cv2
import os

from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_put_user():

    image_bytes = None
    with open("test_assets/test-4.jpg", "rb") as image_file:
        image_bytes = image_file.read()

    file_name = "test-4.jpg"
    file_content = io.BytesIO(image_bytes)
    file_content_type = "text/plain"
    file_headers = {"Content-Type": "image/jpeg"}

    files = {"file": (file_name, file_content, file_content_type, file_headers)}

    # convert image_bytes to raw byte array  
    response = client.put("/users/104", files=files)
    assert response.status_code == 200, response.text
    assert response.json() == "Image successfully added to the database"

def test_get_user():

    response = client.get("/users/104")
    assert response.status_code == 200, response.text
    assert response.json() == [
            [
                -0.18304648995399475,
                0.12221451848745346,
                0.07869056612253189,
                -0.04536474868655205,
                -0.061457179486751556,
                -0.0064706942066550255,
                -0.11946699768304825,
                -0.056769415736198425,
                0.12573939561843872,
                -0.13877655565738678,
                0.25433820486068726,
                0.048685625195503235,
                -0.1884589046239853,
                -0.03813108429312706,
                -0.1109016090631485,
                0.10066558420658112,
                -0.1728605031967163,
                -0.10348059982061386,
                -0.059406816959381104,
                -0.09149583429098129,
                0.050297945737838745,
                0.05411330237984657,
                0.011170575395226479,
                0.0058601778000593185,
                -0.13395142555236816,
                -0.3376421332359314,
                -0.07618686556816101,
                -0.05605112016201019,
                0.109146848320961,
                -0.1389857977628708,
                -0.00011703744530677795,
                -0.025892868638038635,
                -0.1851382553577423,
                0.04882638901472092,
                -0.017650626599788666,
                0.07403528690338135,
                -0.025316845625638962,
                -0.06451453268527985,
                0.23074600100517273,
                0.03337223827838898,
                -0.11112687736749649,
                0.04588385298848152,
                0.03662735968828201,
                0.2963261604309082,
                0.2086552530527115,
                -0.028654228895902634,
                0.020938877016305923,
                -0.09854577481746674,
                0.0919293463230133,
                -0.24489179253578186,
                0.07230037450790405,
                0.17831672728061676,
                0.08435557782649994,
                0.07129403203725815,
                0.07336588948965073,
                -0.13608622550964355,
                0.0005188509821891785,
                0.12137486040592194,
                -0.14229507744312286,
                0.07388762384653091,
                0.06749139726161957,
                -0.021433740854263306,
                -0.025157473981380463,
                -0.02658342570066452,
                0.19202017784118652,
                0.16002894937992096,
                -0.1452464759349823,
                -0.1531800627708435,
                0.09348919987678528,
                -0.19267581403255463,
                0.02596161514520645,
                0.09024917334318161,
                -0.07669506967067719,
                -0.1326841115951538,
                -0.2201584279537201,
                0.05578982084989548,
                0.4130047559738159,
                0.1881779283285141,
                -0.11964867264032364,
                0.01183397602289915,
                -0.09190347790718079,
                -0.08894297480583191,
                0.07874633371829987,
                0.048725590109825134,
                -0.1735832542181015,
                -0.049995675683021545,
                -0.06642656773328781,
                0.11423696577548981,
                0.19999255239963531,
                0.11576749384403229,
                -0.04207873344421387,
                0.17831681668758392,
                0.025603078305721283,
                0.029049886390566826,
                0.028341833502054214,
                0.025528402999043465,
                -0.15364788472652435,
                -0.07496203482151031,
                -0.05337391793727875,
                -0.002673720009624958,
                -0.07166601717472076,
                -0.10450881719589233,
                0.011508142575621605,
                0.131027489900589,
                -0.12273842096328735,
                0.15841037034988403,
                -0.02822108380496502,
                -0.018303653225302696,
                0.008913754485547543,
                0.0685441866517067,
                -0.08483467996120453,
                -0.007475349120795727,
                0.10570619255304337,
                -0.212018683552742,
                0.19471092522144318,
                0.1199721246957779,
                0.08070424944162369,
                0.13887697458267212,
                0.12887074053287506,
                0.07525502145290375,
                -0.04182268679141998,
                0.017219942063093185,
                -0.09713458269834518,
                -0.03335878625512123,
                -0.059637486934661865,
                -0.07345589250326157,
                0.1388857662677765,
                -0.020430458709597588
            ]
        ]

def test_post_session():
    image_bytes = None
    with open("test_assets/test-4.jpg", "rb") as image_file:
        image_bytes = image_file.read()

    file_name = "test-4.jpg"
    file_content = io.BytesIO(image_bytes)
    file_content_type = "text/plain"
    file_headers = {"Content-Type": "image/jpeg"}

    files = {"file": (file_name, file_content, file_content_type, file_headers)}

    response = client.post("/sessions?session_id=1&user_id=104&timestamp=1", files=files)
    assert response.status_code == 200, response.text
    assert response.json() == "Image received"

def test_get_session():

    response = client.get("/sessions/1")
    assert response.status_code == 200, response.text
    assert response.json() == {
        "session_id": "1",
        "user_id": 104,
        "pct_present": 1.0,
        "avg_distance": 0.0,
        "std_distance": 0.0
    }

def test_delete_session():

    response = client.delete("/sessions/1")
    assert response.status_code == 200, response.text
    assert response.json() == "Session deleted"

    response = client.get("/sessions/1")
    assert response.status_code == 200, response.text
    assert response.json() == "Session not found"

def test_delete_user():
    
    response = client.delete("/users/104")
    assert response.status_code == 200, response.text
    assert response.json() == "User successfully deleted"

    response = client.get("/users/104")
    assert response.status_code == 200, response.text
    assert response.json() == "User not found"

def test_end_to_end_session():

    image_bytes = None
    with open("test_assets/test-10.jpg", "rb") as image_file:
        image_bytes = image_file.read()

    file_name = "test-10.jpg"
    file_content = io.BytesIO(image_bytes)
    file_content_type = "text/plain"
    file_headers = {"Content-Type": "image/jpeg"}

    files = {"file": (file_name, file_content, file_content_type, file_headers)}

    # convert image_bytes to raw byte array  
    response = client.put("/users/110", files=files)
    assert response.status_code == 200, response.text
    assert response.json() == "Image successfully added to the database"

    # open video and post every 10th frame to session
    cap = cv2.VideoCapture("test_assets/test-2.mp4")
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        if frame_count % 10 == 0:
            _, buffer = cv2.imencode('.jpg', frame)
            file_content = io.BytesIO(buffer)
            file_content_type = "text/plain"
            file_headers = {"Content-Type": "image/jpeg"}
            files = {"file": ("test-10.jpg", file_content, file_content_type, file_headers)}
            response = client.post(f"/sessions?session_id=2&user_id=110&timestamp={frame_count}", files=files)
            assert response.status_code == 200, response.text
            assert response.json() == "Image received"
    
    # get session
    response = client.get("/sessions/2")
    assert response.status_code == 200, response.text
    assert response.json() == {
        "session_id": "2",
        "user_id": 110,
        "pct_present": 1.0,
        "avg_distance": 0.2381553674843698,
        "std_distance": 0.017191096220264004
    }

    # delete session
    response = client.delete("/sessions/2")
    assert response.status_code == 200, response.text
    assert response.json() == "Session deleted"

    # delete user
    response = client.delete("/users/110")
    assert response.status_code == 200, response.text
    assert response.json() == "User successfully deleted"