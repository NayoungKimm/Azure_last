from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
import jwt
import requests
from flask_cors import CORS
import logging


app = Flask(__name__)
CORS(app)


# 데이터베이스 설정
password = "Kknnyy0819@@!"
url_encoded_password = quote_plus(password)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql+pymysql://root:{url_encoded_password}@localhost/Azure_db"
db = SQLAlchemy(app)


# User 모델 정의
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(20), nullable=False)


# 사용자 정보를 데이터베이스에 저장
def create_user(email, gender, nickname):
    user = Users.query.filter_by(email=email).first()
    if user:
        return "existing_user"

    new_user = Users(email=email, gender=gender, name=nickname)
    db.session.add(new_user)
    db.session.commit()
    return "new_user"


@app.route("/login", methods=["POST"])
def login():
    kakao_token = request.json.get("access_token")
    if kakao_token is None:
        return jsonify({"error": "No access token"}), 400

    headers = {"Authorization": f"Bearer {kakao_token}"}
    response = requests.get("https://kapi.kakao.com/v2/user/me", headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Invalid access token"}), 400
    kakao_user = response.json()

    # kakao_user 정보를 출력합니다.
    print(f"Received token: {kakao_token}")
    print(f"User Info: {kakao_user}")

    email = kakao_user["kakao_account"]["email"]
    gender = kakao_user["kakao_account"]["gender"]
    try:
        name = kakao_user["kakao_account"]["profile"]["nickname"]
    except KeyError:
        name = "default_name"  # Set default name if nickname does not exist

    message = create_user(email, gender, name)

    token = jwt.encode(
        {"email": email, "gender": gender, "name": name},
        "Kknnyy0819@@!",
        algorithm="HS256",
    )

    print(f"Generated JWT Token: {token}")

    return jsonify({"message": message, "token": token})


logging.basicConfig(level=logging.INFO)

@app.route("/welcome", methods=["GET"])
def welcome():
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Invalid token"}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(token, "Kknnyy0819@@!", algorithms=["HS256"])
        email = payload['email']
        name = payload['name']
        # 여기서 사용자에 대한 추가 정보를 데이터베이스에서 가져올 수 있습니다.
        # 현재 예시에서는 JWT 토큰에 이미 사용자 이름(name)이 저장되어 있으므로, 이를 그대로 사용합니다.

        return jsonify({"message": f"{name}님 환영합니다!"})

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        return jsonify({"error": "Invalid token"}), 401

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=2200)
