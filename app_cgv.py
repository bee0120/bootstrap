# from flask import Flask, request, render_template
# app = Flask(__name__)

# # @app.route('/')
# # def hello():
# #     return 'Hello, World!'

# @app.route('/method', methods=['GET', 'POST'])
# def method():
#     if request.method == 'GET':
#         # args_dict = request.args.to_dict()
#         # print(args_dict)
#         num = request.args["num"]
#         name = request.args.get("name")
#         return "GET으로 전달된 데이터({}, {})".format(num, name)
#     else:
#         num = request.form["num"]
#         name = request.form["name"]
#         return "POST로 전달된 데이터({}, {})".format(num, name)

# @app.route('/hello/<name>')
# def hello(name):
#     return "hello {}".format(name)

# # render_templates: templates 폴더에 있는 html 파일들을 렌더링,HTML 페이지를 동적으로 만들 수 있음
# @app.route('/hello/')
# def hellohtml():
#     return render_template("hello.html")

# # ('/input/<int:num>') url뒤에 <variavle_name>형태로 나타내며 url요청시 변수를 전달할수 있음(타입지정도 가능)
# @app.route('/input/<int:num>')
# def input(num):
#     name = ''
#     if num == 1:
#         name = '도라에몽'
#     elif num == 2:
#         name = '진구'
#     elif num == 3:
#         name = '퉁퉁이'
#     return "hello {}".format(name)

# if __name__ == '__main__':
#     app.run(debug=True)
from datetime import datetime
import requests
import os
from bs4 import BeautifulSoup
from flask import Flask, redirect, render_template, url_for, request, flash, session
from DB_handler_cgv import DBModule

app = Flask(__name__)
app.secret_key ="dfafadfasdfaf!" #로그인시 필요
DB = DBModule()

def crawl_cgv():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    base_url = "https://www.cgv.co.kr/movies/?lt=1&ft=0"
    cookie = {"a": "b"}

    req = requests.get(base_url, headers=headers, timeout=5, cookies=cookie)
    html = req.text
    soup = BeautifulSoup(html, "html.parser")

    sect_movie_chart = soup.select_one(".sect-movie-chart")
    movie_chart = sect_movie_chart.select("li")

    movie_list = []
    for rank, movie in enumerate(movie_chart, 1):
        title = movie.select_one(".title")
        score = movie.select_one(".score")
        boximg = movie.select_one(".thumb-image > img")
        ticketing = score.select_one(".percent")
        egg_gage = score.select_one(".egg-gage.small > .percent")
        info = movie.select_one(".txt-info > strong").next_element.strip()
        link = movie.a['href']
        link = f"https://www.cgv.co.kr{link}"


        detail_req = requests.get(link, headers=headers, timeout=5, cookies=cookie)
        detail_html = detail_req.text
        detail_soup = BeautifulSoup(detail_html, "html.parser")

        dt_elements = detail_soup.select(".spec > dl > dt")

        if len(dt_elements) >= 3:
            genre_text = dt_elements[2].text.strip()

            if '장르 :' in genre_text:
                genre = genre_text.split('장르 :')[1].strip()  # 장르 텍스트에서 "장르 :" 이후의 부분 추출
                # print(genre)

            if '장르 :' not in genre_text or not genre:
                genre = "없음"
        else:
            genre = "없음"

        print(f"<<<{rank}위>>>")
        print(title.text)
        print(ticketing.get_text(" : "))
        print(f"실관람지수: {egg_gage.text}")
        # print(info.text.strip())
        print(f"{info.strip()} 개봉")
        print(link)
        print(genre)
        print()

        img_url = boximg["src"] if boximg and 'src' in boximg.attrs else ""

        movie_info = {
            "movie_rank": rank,
            "title": title.text,
            "boximg": boximg.text,
            "score": score.text,
            "ticketing": ticketing.get_text(" : "),
            "egg_gage": egg_gage.text,
            "info": info.strip(),
            "link": link,
            "genre": genre,
            "img_url": img_url
        }

        movie_list.append(movie_info)

        if rank == 11:
            break

    return movie_list

@app.route("/") #첫 메인 화면 연결
def index():
    if "uid" in session: #세션안에 로그인id가 저장되어있으면
        user = session["uid"] # uid를 통해 사용자 정보user를 가져올수 있음
    else:
        user = "Login" #세션안에 로그인정보가 없으면 login 하라고 뜸
    # return render_template("index_copy.html", user = user) #template안에 있는거 불러오기

    # relative_path = "C:/DNBI/STCproject/python/hello/bootstrap/html5up-telephasic/index.html"
    # absolute_path = os.path.abspath(relative_path)

    # 크롤링 함수 호출
    movie_list = crawl_cgv()[:10] #전체 영화정보

    if session is not None: #세션에 값이 있으면
        user_mtype = DB.get_movie_by_uid(session.get("uid")) #uid를 이용해서 유저의 개인 영화 선호도 데이터 얻음


    # 크롤링한 데이터를 데이터베이스에 저장
    for rank, movie_info in enumerate(movie_list, 1): #크롤링해온 데이터를 movie_info에 1개씩 총 10개 담음
    # 중복된 데이터 체크
        existing_movie = DB.get_movie_by_rank(movie_info["movie_rank"])
        if not existing_movie:

            info_strip = movie_info["info"].strip() #개봉일 제대로 나오게 하기위함
            DB.save_movie_info( # 이름은 어뜨케 가져오는건지
                movie_info["title"],
                movie_info["score"],
                movie_info["img_url"],
                movie_info["ticketing"],
                movie_info["movie_rank"],
                movie_info["egg_gage"],
                info_strip,
                movie_info["genre"],
                movie_info["img_url"],
                movie_info["link"]
            )
    # 데이터베이스에서 영화 정보 검색
    num_param = request.args.get('num') #request는 화면에서 서버에 요청하는 변수(num을 화면에서 만든후 여기서 설정해줌)). 선택정렬에 있는거 변수값 가져오게
    # print(num_param)
    num_param = int(num_param) if num_param is not None else None  # 문자열을 정수로 변환, 있으면 그대로 두고 없으면 none처리

    if num_param == 1:
        movies_from_db = DB.get_movies(None,num_param)
    elif num_param == 2:
        movies_from_db = DB.get_movies(None,num_param)
    elif num_param == 3:
        movies_from_db = DB.get_movies(None,num_param)
    elif user_mtype is not None:
        movies_from_db = DB.get_movies(user_mtype["mtype"]) #DB.get_movies에서 if mtype is not None:  일떄 쿼리를 돌림
    else:  movies_from_db = DB.get_movies() # SELECT * FROM movies"쿼리값 가져옴
    # 만약 movies_from_db가 None이면 빈 리스트로 초기화
    movies_from_db = movies_from_db or []
    info_strip = None  # 변수 초기화
    # 영화 정보를 HTML 문자열로 변환하여 전달
    # main_text_cgv1 = ""
    # main_text_cgv2 = ""
    for rank, movie_info2 in enumerate(movies_from_db): #DB에서 끌고온 데이터를 화면에 뿌려줄떄 사용, 화면에 뿌려줄 DB정보를 배열에 담음
        title = movie_info2["title"]
        score = movie_info2["score"]
        img_url = movie_info2["img_url"]
        movie_rank = movie_info2["movie_rank"]
        egg_gage = movie_info2["egg_gage"]
          # info 필드가 datetime 형식인 경우에만 strip() 메서드 적용
    # if isinstance(movie_info2["info"], datetime):
    #     info_strip = movie_info2["info"].strftime("%Y-%m-%d")
    # else:
    #     info_strip = movie_info2["info"].strip()
        isinstance(movie_info2["info"], datetime)
        info_strip = movie_info2["info"].strftime("%Y-%m-%d")

        genre = movie_info2["genre"]
        img_url = movie_info2["img_url"]
        link = movie_info2["link"]

    return render_template("index_copy.html", user=user,movies_from_db=movies_from_db) #.HTML은 화면 구조 설계된

@app.route("/login") #/는 주소 , html은 건물(구조)
def login():
    if "uid" in session:
        return redirect(url_for("index")) #REDIRECT는 이전페이지로 돌아감 , URL 주소
    else:
        return render_template("login2.html",alert_message="해당 아이디는 존재하지 않습니다.")
    # return render_template("login.html",alert_message="해당 아이디는 존재하지 않습니다.")

@app.route("/login_done", methods=["get"])
def login_done():

    uid = request.args.get("id")
    pwd = request.args.get("pwd")
    # mtype = request.args.get("mtype")

    if DB.login(uid, pwd):
        session["uid"] = uid
        # session["mtype"] = user_mtype
        return redirect(url_for("index"))
    else:
        flash("아이디나 비밀번호가 없습니다.")
        return render_template("signin.html")

@app.route("/logout")
def logout():
    if "uid" in session:
        session.pop("uid")
        return redirect(url_for("index"))
    else:
        return render_template(url_for("login"))

# @app.route("/login_done", methods = ["get"])
# def login_done():

#     uid = request.args.get("id")
#     pwd = request.args.get("pwd")
#     if DB.login(uid, pwd):
#         session["uid"] = uid
#         return redirect(url_for("index"))
#     else:
#         flash("아이디나 비밀번호가 없습니다.")
#         return redirect(url_for("login"))

@app.route("/signin")
def signin():

    return render_template("signin.html")

@app.route("/signin_done", methods=["get"])
def signin_done():
    # email = request.args.get("email")
    uid = request.args.get("id")
    pwd = request.args.get("pwd")
    name = request.args.get("name")
    mtype = request.args.get("mtype")

    if DB.signin(_id_=uid, pwd=pwd, name=name, mtype=mtype):
        return redirect(url_for("index"))
    else:
        flash("이미 존재하는 아이디입니다.")
        return redirect(url_for("signin"))

@app.route("/add_list", methods=["GET"])
def add_list():
    if "uid" in session:
        user = session["uid"]
    else:
        user = "Login"

    return render_template("add_list.html",user=user)

@app.route("/add_list_done", methods=["POST"])
def add_list_done():
       if request.method == "POST":
        rank = request.form.get("rank")
        title = request.form.get("title")
        info = request.form.get("info")
        egg_gage = request.form.get("egg_gage")
        genre = request.form.get("genre")


            # title이 None이 아닌 경우에만 데이터베이스에 추가
        DB.add_movie_info(movie_rank=rank, title=title, info=info, egg_gage=egg_gage, genre=genre)
        flash("영화 정보가 성공적으로 추가되었습니다.")
        return redirect(url_for("manager"))

@app.route("/manager")
def manager():
    if "uid" in session:
        user = session["uid"]
    else:
        user = "Login"

    # 삭제 기능 수정
    title_to_delete = request.args.get('title')
    if title_to_delete is not None:
        DB.delete_movie_by_title(title_to_delete)

    # 크롤링 대신 데이터베이스에서 정보 가져오기
    movies_from_db = DB.get_movies() or []

    movie_info_list = []
    for rank, movie_info in enumerate(movies_from_db, 1):
        movie_rank = movie_info["movie_rank"]
        title = movie_info["title"]
        info = movie_info["info"]
        score = movie_info["score"]
        egg_gage = movie_info["egg_gage"]
        genre = movie_info["genre"]
        link = movie_info["link"]

        movie_info_list.append({
            # "index": index,
            "movie_rank": movie_rank,  # 순위 추가
            "title": title,
            "info": info,
            "score": score,
            "egg_gage": egg_gage,
            "genre": genre,
            "link": link  # link 변수 추가
        })

    return render_template("manager.html", user=user, movies_from_db=movie_info_list)


@app.route("/manage_list/<int:index>")
def manage_list(index):
    if "uid" in session:
        user = session["uid"]
    else:
        user = "Login"

    movies_from_db_list = DB.get_movies() or []

    if not movies_from_db_list:
        flash("정보가 없습니다.")
        return redirect(url_for("manager"))

      # index에 해당하는 영화 정보만 가져오기
    if 0 <= index < len(movies_from_db_list):
        movie_info = movies_from_db_list[index]
    else:
        flash(f"인덱스 {index}에 해당하는 영화 정보가 없습니다.")
        return redirect(url_for("manager"))

    movie_info_list = [{
        "index": index,
        "rank": movie_info["movie_rank"],
        "title": movie_info["title"],
        "info": movie_info["info"],
        "score": movie_info["score"],
        "egg_gage": movie_info["egg_gage"],
        "genre": movie_info["genre"]
    }]

    return render_template("manage_list.html",  user=user, movie_info_list=movie_info_list)
# 관리자 페이지 영화 수정
@app.route("/update_movie", methods=["POST"])
def update_movie():  # 영화 정보 수정하기
    # 폼에서 전송된 데이터 가져오기
    index_str = request.form.get("index")
    try:
        index = int(index_str)
    except ValueError:
        flash(f"잘못된 인덱스 값입니다.")
        return redirect(url_for("manager"))

    # 폼에서 전송된 데이터 가져오기
    # rank = request.form.get("movie_rank")
    title = request.form.get("title")
    info = request.form.get("info")
    egg_gage = request.form.get("egg_gage")
    genre = request.form.get("genre")

    # 데이터 유효성 검사 (필요에 따라 추가적인 검증 필요)
    if not title or not info or not egg_gage or not genre:
        flash("입력값이 부족합니다.")
        return redirect(url_for("manager"))

    # 영화 정보 업데이트
    DB.update_movie_info(
        # movie_index=index,
        # movie_rank=rank,
        title=title,
        info=info,
        egg_gage=egg_gage,
        genre=genre
    )

    flash("영화 정보가 업데이트 되었습니다.")
    return redirect(url_for("manager"))

@app.route("/userpage")
def userpage():
    if "uid" in session:
        user = session["uid"]
    else:
        user = "Login"

    # 세션에서 사용자가 입력한 값 가져오기
    user_mtype = DB.get_movie_by_uid(session["uid"])
    # print(session)

    # user_mtype가 None이 아니라면 사용자가 입력한 값이 존재함
    if user_mtype is not None:
        print(f"사용자가 입력한 장르: {user_mtype}")

    # 크롤링 함수 호출
    movie_list = crawl_cgv()[:10]

    # 크롤링한 데이터를 데이터베이스에 저장
    for rank, movie_info in enumerate(movie_list, 1):
        # 중복된 데이터 체크
        existing_movie = DB.get_movie_by_rank(movie_info["movie_rank"])
        if not existing_movie:
            DB.save_movie_info(
                movie_info["title"],
                movie_info["score"],
                movie_info["img_url"],
                movie_info["ticketing"],
                movie_info["movie_rank"],
                movie_info["egg_gage"],
                movie_info["info"].strip(),
                movie_info["genre"],
                movie_info["img_url"],
                movie_info["link"]
            )
    # print(user_mtype)
    # 데이터베이스에서 영화 정보 검색
    movies_from_users = DB.get_user_movie(user_mtype["mtype"])
    print("Debug - movies_from_users:", movies_from_users)

    # 만약 movies_from_users가 None이면 빈 리스트로 초기화
    movies_from_users = movies_from_users or []
    print(movies_from_users)

    return render_template("user_page.html", user=user, movies_from_users=movies_from_users)



@app.route("/user/<uid>")
def user(uid):
    pass

if __name__ =="__main__":
    app.run(host="0.0.0.0", debug=True)
# @app.route("/list") #\뒤에 이름은 html의 a태그와 연결
# def post_list():
#     pass

# @app.route("/post/<int:pid>")
# def post(pid):


# @app.route("/write")
# def write():
#     pass

# @app.route("/write_done", methods = ["GET"])
# def write_done():
#     pass

