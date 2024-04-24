from email_validator import EmailNotValidError, validate_email
from flask import  ( Flask, 
                    render_template, 
                    url_for, 
                    request, 
                    redirect, 
                    flash 
                )

import logging
from flask_debugtoolbar import DebugToolbarExtension
import os
from flask_mail import Mail, Message

# 서버 프로그램 객체를 만든다. 
# __name__ : 실행 중인 모듈의 시스템 상의 이름 
app = Flask(__name__)
app.config["SECRET_KEY"] = "wlrmaqnxjtlwkrgoqhk"
app.logger.setLevel(logging.DEBUG)
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER")
app.config["MAIL_PORT"] = os.environ.get("MAIL_PORT")
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS")
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")

mail = Mail(app)
toolbar = DebugToolbarExtension(app)

# 기본 주소로 요청이 왔을 때 무엇을 할지 정의하기 
@app.route("/")
def index() :
    return "Hello, Flask!!"

# 메소드에 따른 처리를 원한다면 구별해서 정의할 수 있다
# 엔드포인트명을 지정하지 않으면 함수명이 엔드포인트명이 된다
@app.route("/hello/<name>", 
           methods=["GET"], 
           endpoint="hello-endpoint")
def hello(name) :
    return f'Hello, {name}!!'

# http://localhost:5000/name/gookhee
@app.route("/name/<name>")
def show_name(name) :
    # 변수를 템플릿 엔진에게 건넨다
    return render_template("index.html", name=name)

with app.test_request_context():
    # /
    print(url_for("index"))
    # /hello/world
    print(url_for("hello-endpoint", name="world"))
    # /name/Ak?page=1
    print(url_for("show_name", name="AK", code="005300"))

with app.test_request_context("/users?updated=true"):

    print(request.args.get("updated"))


# http://127.0.0.1:5000/contact
# 플라스크의 템플릿 문서는 앱 내 templates 폴더에 있다고 가정한다
@app.route("/contact")
def contact():
    return render_template("contact.html")

# http://127.0.0.1:5000/contact/complete
# post 요청이 오면, 필요한 데이터 관련 처리를 하고나서 
# contact_complete.html 템플릿을 주는 get 처리를 하면서 마무리
@app.route("/contact/complete", methods=["GET", "POST"])
def contact_complete():
    if request.method == "POST":
        # form 속성을 사용해서 폼의 값을 취득한다 
        username = request.form["username"]
        email = request.form["email"]
        description = request.form["description"]

        # 유효성 검사 파트 
        is_valid = True
        if not username:
            flash("사용자명은 필수입니다")
            is_valid = False

        if not email:
            flash("메일 주소는 필수입니다")
            is_valid = False

        try:
            validate_email(email) # 이메일 형식 검사 
        except EmailNotValidError:
            flash("메일 주소의 형식으로 입력해 주세요")
            is_valid = False

        if not description:
            flash("문의 내용은 필수입니다")
            is_valid = False

        if not is_valid:
            return redirect(url_for("contact"))

        # 이메일 보내기 함수 
        send_email(
            email, # 이메일 주소
            "문의 감사합니다.", # 이메일 답장의 제목 
            "contact_mail", # 이메일 내용의 템플릿 
            username=username, # 사용자 이름
            description=description, # 문의 내용
        )

        flash("문의해 주셔서 감사합니다.")
        
        return redirect(url_for("contact_complete"))

    return render_template("contact_complete.html")

# 이메일 보내기 위해서 API 사용하는 함수 
def send_email(to, subject, template, **kwargs):
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)