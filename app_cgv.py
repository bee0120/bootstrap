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
import time
from bs4 import BeautifulSoup
from flask import Flask, redirect, render_template, url_for, request, flash, session
from DB_handler_cgv import DBModule

app = Flask(__name__)# Flask 클래스의 인스턴스를 생성하고, 이를 변수 app에 할당하는 역할, Flask 애플리케이션을 생성하고 초기화 설정하는 기본적인 단계
app.secret_key ="dfafadfasdfaf!" #로그인시 필요
DB = DBModule()

# CGV 사이트에서 영화 정보를 크롤링하는 함수를 정의
def crawl_cgv():
    # HTTP 요청 헤더를 설정
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    base_url = "https://www.cgv.co.kr/movies/?lt=1&ft=0" # CGV 사이트의 베이스 URL을 설정
    cookie = {"a": "b"}     # HTTP 쿠키를 설정

    req = requests.get(base_url, headers=headers, timeout=5, cookies=cookie)  # CGV 사이트에 HTTP GET 요청을 보냄 (requests는 http요청 관련 작업 처리)
    html = req.text # HTTP 응답의 HTML 내용을 가져옴
    soup = BeautifulSoup(html, "html.parser")    # BeautifulSoup을 사용하여 HTML을 파싱 (크롤링할 페이지?)
    #BeautifulSoup은 HTML 또는 XML 문서를 쉽게 파싱하고 검색할 수 있게 도와주는 도구

    sect_movie_chart = soup.select_one(".sect-movie-chart") # 영화 차트가 있는 섹션을 선택
    movie_chart = sect_movie_chart.select("li")    # 섹션 내의 각 영화 아이템을 선택
    movie_list = []  # 크롤링한 영화 정보를 저장할 리스트를 초기화
    # 영화 차트의 각 순위별로 정보를 추출 movie_chart순회 하며 인덱스를 1부터 지정해 아래 정보 저장
    for rank, movie in enumerate(movie_chart, 1): #인덱스를 rank변수에 항목을 movie변수에 할당
        title = movie.select_one(".title") #movie_chart에 담긴 정보중 title정보 크롤링
        score = movie.select_one(".score")
        boximg = movie.select_one(".thumb-image > img")  # 영화의 썸네일 이미지
        ticketing = score.select_one(".percent")  # 영화의 예매율
        egg_gage = score.select_one(".egg-gage.small > .percent")# 영화의 평점 선택
        info = movie.select_one(".txt-info > strong").next_element.strip() #개봉일 선택하고 텍스트 정제
        link = movie.a['href']  # 영화의 상세 페이지 링크를 추출
        link = f"https://www.cgv.co.kr{link}" # 문자열 포맷팅 방법  f-string을 사용 =>동적으로 문자열 생성가능 cgv주소 뒤에 /movies/detail-view/?midx=87999이런식의 경로 붙여줌

        #장르 정보를 얻기 위한 상세페이지 html 파싱
        detail_req = requests.get(link, headers=headers, timeout=5, cookies=cookie)# 영화의 상세 페이지로 추가적인 정보를 크롤링하기 위해 상세 페이지로 요청을 보냄(장르정보)
        detail_html = detail_req.text   # 상세 페이지의 HTML 내용을 가져옴
        detail_soup = BeautifulSoup(detail_html, "html.parser")# BeautifulSoup을 사용하여 상세 페이지의 HTML을 파싱 html.parser은 파서 종류
        dt_elements = detail_soup.select(".spec > dl > dt") # 상세 페이지에서 dt내의 정보를 추출
         #HTML 요소에서 "src" 속성의 값을 가져오는 표현식
        img_url = boximg["src"] if boximg and 'src' in boximg.attrs else "" #만약 boximg가 존재하고 boximg가 "src" 속성을 가지고 있다면, 해당 속성의 값을 가져옴. 그렇지 않으면 빈 문자열("")을 반환

        if len(dt_elements) >= 3: # dt 정보가 존재하고 그 개수가 3보다 크면
            genre_text = dt_elements[2].text.strip() #dt2에 해당하는 장르 정보를 추출하고 genre_text에 담기

            if '장르 :' in genre_text: #'장르:' 가 dt2에서 추출해온 데이터에 있으면
                genre = genre_text.split('장르 :')[1].strip()  # 해당 텍스트에서 "장르 :" 이후의 부분 추출하여 genre변수에 저장
                # print(genre)

            if '장르 :' not in genre_text or not genre: #'장르:' 라는 텍스트가 genre_text에 없거나 genre변수에도 없으면
                genre = "없음" #장르가 없다고 표시
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
        # print(img_url)
        # print(boximg)

        # 하나의 영화 정보를 딕셔너리로 저장,딕셔너리(dictionary)는 파이썬에서 사용되는 데이터 구조 중 하나로, 키(key)와 값(value)으로 이루어진 쌍(pair)을 저장하는 컨테이너
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
         # 영화 정보를 리스트에 추가
        movie_list.append(movie_info)

    # 상위 11위까지만 크롤링하도록 설정
        if rank == 11:
            break
        # time.sleep(delay_seconds)
    # 크롤링한 영화 정보를 반환
    return movie_list
# result = crawl_cgv()

 #첫 메인 화면
@app.route("/")# @app.route 은 / 경로에 대한 라우팅 및 뷰 정의
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
        user_mtype = DB.get_movie_by_uid(session.get("uid")) #uid가 있는 유저의 전체 정보를 가져와서 그중 필요한 개인 영화 선호도 데이터 얻음


    # 크롤링한 데이터를 데이터베이스에 저장
    for rank, movie_info in enumerate(movie_list, 1): #크롤링해온 데이터를 movie_info에 1개씩 총 10개 담음
    # 중복된 데이터 체크
        existing_movie = DB.get_movie_by_rank(movie_info["movie_rank"]) #순위 기준으로 이미 있는 순위는 안들어오게
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
    num_param = int(num_param) if num_param is not None else None  # 문자열을 정수로 변환, 있으면 그대로 두고 없으면 none처리

    uid = session.get("uid")

    if num_param == 1:
        movies_from_db = DB.get_movies(None,num_param, uid)
    elif num_param == 2:
        movies_from_db = DB.get_movies(None,num_param, uid)
    elif num_param == 3:
        movies_from_db = DB.get_movies(None,num_param, uid)
    elif user_mtype is not None:
        movies_from_db =  DB.get_movies(user_mtype["mtype"],None, uid)  #DB.get_movies에서 if mtype is not None:  일떄 쿼리를 돌림
    else:
        movies_from_db = DB.get_movies(None, None, uid) # SELECT * FROM movies"쿼리값 가져옴
    # 만약 movies_from_db가 None이면 빈 리스트로 초기화
    movies_from_db = movies_from_db or []
    info_strip = None  # 변수 초기화
    # 영화 정보를 HTML 문자열로 변환하여 전달
    # main_text_cgv1 = ""
    # main_text_cgv2 = ""
    for rank, movie_info2 in enumerate(movies_from_db): #DB에서 끌고온 데이터를 템플릿에 전달할떄 사용(HTML안에서 아래 변수 사용), 화면에 뿌려줄 DB정보를 배열에 담음
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
        genre = movie_info2["genre"]
        img_url = movie_info2["img_url"]
        link = movie_info2["link"]

        isinstance(movie_info2["info"], datetime)
        info_strip = movie_info2["info"].strftime("%Y-%m-%d")

    return render_template("index_copy.html", user=user,movies_from_db=movies_from_db) #HTML 템플릿을 렌더링하여 클라이언트에게 전송하는 역할 뒤에는 템플릿에 전달할 변수, 템플릿에서 db에서 가져온 정보들을 동적으로 활용 가능
#로그인 페이지 화면
@app.route("/login") # url_For뒤의(/)는 주소 , html은 건물(구조)
def login():
    if "uid" in session: #세션안에 로그인id가 저장되어있으면 (로그인된 상태)
        return redirect(url_for("index")) #REDIRECT는 이전페이지로 돌아감 메인페이지로 리디렉션 , URL 주소
    else:
        return render_template("login2.html",alert_message="해당 아이디는 존재하지 않습니다.") #로그인 페이지를 렌더링 =>모달창
    # return render_template("login.html",alert_message="해당 아이디는 존재하지 않습니다.")
#로그인 처리
@app.route("/login_done", methods=["get"])
def login_done():

    uid = request.args.get("id") #입력한 id
    pwd = request.args.get("pwd") #입력한 pwd
    # mtype = request.args.get("mtype")

    if DB.login(uid, pwd): #제출된 아이디(uid)와 비밀번호(pwd)를 이용하여 데이터베이스에서 로그인을 확인
        session["uid"] = uid #성공 시 세션에 "uid"를 저장
        # session["mtype"] = user_mtype
        return redirect(url_for("index")) #메인페이지로 리디렉션
    else:
        flash("아이디나 비밀번호가 없습니다.") #로그인에 실패하면 플래시 메시지를 설정
        return render_template("signin.html") #회원가입 페이지로 리디렉션 => 로그인 모달창으로 리디렉션 시키도록
#로그아웃 처리
@app.route("/logout")
def logout(): #사용자 로그아웃 요청시
    if "uid" in session:
        session.pop("uid") #세션에서 "uid"를 삭제
        return redirect(url_for("index")) #로그아웃후 메인 페이지로 리디렉션합
    else:
        return render_template(url_for("login"))# 세션에 "uid"가 없는 경우에는 로그인 페이지로 이동
#회원가입페이지
@app.route("/signin") #signin경로로 get요청이 오면
def signin():
    return render_template("signin.html") #signin.html 템플릿을 렌더링하여 사용자에게 회원가입 페이지를 보여줌
#회원가입처리
@app.route("/signin_done", methods=["get"])
def signin_done():
    # email = request.args.get("email")
    #사용자가 입력한 회원정보 받아오기
    uid = request.args.get("id")#괄호 안의 변수명 html이랑 맞춰주기
    pwd = request.args.get("pwd")
    name = request.args.get("name")
    mtype = request.args.get("mtype")

    if DB.signin(_id_=uid, pwd=pwd, name=name, mtype=mtype): #db메서드를 통해 회원가입 정보를 db에 저장(키워드 인자로 이름+값 전달) + signin_verification 에 대한 TURE/FALSE처리도 여기서 해줌
        return redirect(url_for("index")) #저장후 메인페이지(index 라우트)로 리다이렉트
    else:
        flash("이미 존재하는 아이디입니다.") #이미 존재 할 경우 메시지 띄우고 회원가입 실패
        return redirect(url_for("signin")) #회원가입페이지로 이동
    #관리자 페이지
@app.route("/manager")
def manager():
    if "uid" in session:  #admin이 세션에 있다
        user = session["uid"]
    else:
        user = "Login"

    # 삭제 기능 수정
    # equest.args.get URL의 쿼리 문자열(Query String)에서 파라미터 값을 가져오기 위한 메서드
    title_to_delete = request.args.get('title') # 쿼리 문자열에서 'title' 파라미터를 가져와서 영화삭제 기능을 수행
    if title_to_delete is not None: # 'title' 파라미터가 존재한다면,
        DB.delete_movie_by_title(title_to_delete) #db를 호출하여 해당 제목의 영화 값을 가진 정보를 db에서 삭제함

    # 크롤링x 데이터베이스에서 정보 가져오기
    movies_from_db = DB.get_movies() or []
    movie_info_list = []
 #반복문을 통해 movies_from_db에서 가지고온 영화 정보를 movie_info에 담음
    for rank, movie_info in enumerate(movies_from_db, 1): #enumerate 몇번째 반복인지 rank도 함꼐 가져옴
        movie_rank = movie_info["movie_rank"] #movie_rank필드를 가져와 변수에 할당
        title = movie_info["title"]
        info = movie_info["info"]
        score = movie_info["score"]
        egg_gage = movie_info["egg_gage"]
        genre = movie_info["genre"]
        link = movie_info["link"]

        movie_info_list.append({ #위에서 불러온 영화 정보를 딕셔너리로 만들어 movie_info_list에 추가(매번movies_from_db에서 전체 정보를 가져오는게 아니라 가공하여  배열에 담긴 정보를 통으로 가져오기위함)
            # "index": index,
            "movie_rank": movie_rank,  # 순위 추가
            "title": title,
            "info": info,
            "score": score,
            "egg_gage": egg_gage,
            "genre": genre,
            "link": link  # link 변수 추가
        })
    #이 정보들을 HTML 템플릿인 "manager.html"에 렌더링해서 보여줌(동적으로 생성),사용자 정보와 영화 정보 리스트를 전달
    return render_template("manager.html", user=user, movies_from_db=movie_info_list)

#관리자에서 선택한 영화 정보를 상세히 보여주는 페이지
@app.route("/manage_list/<int:index>") #<int:index> 부분은 동적 라우팅으로, 사용자가 선택한 영화의 인덱스를 나타냄
def manage_list(index):
    if "uid" in session:
        user = session["uid"]#세션에서 사용자 아이디(uid)를 가져와 user에 할당
    else:
        user = "Login"

    movies_from_db_list = DB.get_movies() or [] #데이터베이스에서 모든 영화 정보를 가져오거나, 없을 경우 빈 리스트를 가지게됨

    if not movies_from_db_list: #만약 영화 정보가 없으면
        flash("정보가 없습니다.") #메시지
        return redirect(url_for("manager"))# 관리자 페이지로 돌아감


    if 0 <= index < len(movies_from_db_list): #유효한 범위 내에 있는지 확인한후 선택한 인덱스에 해당하는 영화 정보를 movie_info에 저장
        movie_info = movies_from_db_list[index] # 위에 조건이 참일경우 index에 해당하는 영화 정보만 db에서 가져와서 movie_info에 저장
    else:
        flash(f"인덱스 {index}에 해당하는 영화 정보가 없습니다.")
        return redirect(url_for("manager"))#관리자 페이지로 리다이렉트

    movie_info_list = [{ #movie_info_list에 추가
        "index": index,
        "rank": movie_info["movie_rank"],
        "title": movie_info["title"],
        "info": movie_info["info"],
        "score": movie_info["score"],
        "egg_gage": movie_info["egg_gage"],
        "genre": movie_info["genre"]
    }]
    #HTML 템플릿인 "manage_list.html"에 렌더링하여 사용자에 보여줌
    return render_template("manage_list.html",  user=user, movie_info_list=movie_info_list)

#영화 목록 추가 페이지
@app.route("/add_list", methods=["GET"]) #add_list" 경로에 대한 GET 메서드 요청을 처리하는 라우트를 등록
def add_list():
    if "uid" in session: #세션에 "uid"가 있다면
        user = session["uid"] #사용자의 아이디를 가져와 user 변수에 할당
    else:
        user = "Login" #"Login" 문자열을 user에 할당합

    return render_template("add_list.html",user=user)#이 정보를 이용하여 "add_list.html" 템플릿을 렌더링
#영화 목록 추가 수행
@app.route("/add_list_done", methods=["POST"]) #add_list_done" 경로에 대한 POST 메서드 요청을 처리하는 라우트를 등록
def add_list_done():
       if request.method == "POST": # 현재 요청이 POST 메서드인지 확인
        #POST 요청으로 전송된 form 데이터에서 각각의 필드에 해당하는 값을 가져옴
        rank = request.form.get("rank")
        title = request.form.get("title")
        info = request.form.get("info")
        egg_gage = request.form.get("egg_gage")
        genre = request.form.get("genre")
        img_url = request.form.get("img_url")

        # title이 None이 아닌 경우에만? 영화 정보 추가하는 함수 호출에 각 필드에 해당하는 값을 인자로 넘겨 데이터베이스에 저장
        DB.add_movie_info(movie_rank=rank, title=title, info=info, egg_gage=egg_gage, genre=genre, img_url=img_url)#앞에 변수는 db함수의 매개변수 이름(movie_rank) 뒤에 변수는 위에서 저장된 값(rank)을 담고있음
        flash("영화 정보가 성공적으로 추가되었습니다.") #메시지 저장
        return redirect(url_for("manager")) #영화 정보 추가후 영화 목록 보이게 manager페이지로 리다이렉트

# 관리자 페이지 영화 수정
@app.route("/update_movie", methods=["POST"]) #POST 방식으로 데이터를 받아와서 영화 정보를 수정
def update_movie():  # 영화 정보 수정하기
    # 폼에서 전송된 데이터 가져오기
    index_str = request.form.get("index")#수정하고자 하는 영화의 인덱스(index)를 폼에서 전송받아 이를 처리
    try: #문자열로 받아온 index_str 값을 정수형으로 변환하려고 시도
        index = int(index_str) #전송된 데이터 중 "index"라는 이름의 값을 가져와 index_str 변수에 할당, 문자열 형태에서 정수로 변환 가능한지 확인
    except ValueError: #index_str이 정수로 변환할 수 없는 문자열이라면 ValueError가 발생
        flash(f"잘못된 인덱스 값입니다.") #잘못된 인덱스 메시지를 플래시 메시지로 설정
        return redirect(url_for("manager"))# 관리자 페이지로 리다이렉트

    # 폼에서 전송된 데이터 가져오기
    # rank = request.form.get("movie_rank")
    title = request.form.get("title")
    info = request.form.get("info")
    egg_gage = request.form.get("egg_gage")
    genre = request.form.get("genre")

    # 데이터 유효성 검사 (필요에 따라 추가적인 검증 필요)
    if not title or not info or not egg_gage or not genre: #4개 중 하나의 값이라도 폼에서 못가져오면
        flash("입력값이 부족합니다.") #플래시 메시지를 설정
        return redirect(url_for("manager")) #관리자 페이지 리다이렉ㅌ

    # 영화 정보 업데이트
    DB.update_movie_info( #폼에서 가져온 정보로 데이터베이스의 해당 영화 정보를 업데이트
        # movie_index=index,
        # movie_rank=rank,
        title=title, #흰색-DB에서의 변수명, 파란색-여기서 지정해준 변수명
        info=info,
        egg_gage=egg_gage,
        genre=genre
    )

    flash("영화 정보가 업데이트 되었습니다.")
    return redirect(url_for("manager"))

if __name__ =="__main__": #파이썬 스크립트를 실행, 현재 스크립트가 직접 실행되었을 때(if문이 참일 때) 아래의 코드 블록을 실행
    app.run(host="0.0.0.0", debug=True) #Flask 애플리케이션을 실행

#사용자 페이지
# @app.route("/userpage")
# def userpage():
#     if "uid" in session:
#         user = session["uid"] #로그인한 경우 세션에서 사용자 아이디(uid)를 가져옴
#     else:
#         user = "Login"

#     # 세션에서 사용자가 입력한 mtype값 가져오기
#     user_mtype = DB.get_movie_by_uid(session["uid"])
#     # print(session)


#     if user_mtype is not None: # user_mtype가 None이 아니라면 사용자가 입력한 값이 존재함
#         print(f"사용자가 입력한 장르: {user_mtype}")

#     # 크롤링 함수 호출, 영화정보 가져옴
#     movie_list = crawl_cgv()[:10]

#     # 크롤링한 데이터를 데이터베이스에 저장
#     for rank, movie_info in enumerate(movie_list, 1):#크롤링한 영화정보의(movie_list) 각 요소에 대해 인덱스와 값을 반환해  rank에 index, movie_info에 영화정보 저장
#         # 중복된 데이터 체크
#         existing_movie = DB.get_movie_by_rank(movie_info["movie_rank"])# 현재 가져온 영화 정보의 순위(movie_rank)를 사용하여 데이터베이스에서 해당 순위의 영화를 가져옴
#         if not existing_movie:  #이미 순위 정보가 db에 들어있는게 아닌경우
#             DB.save_movie_info(  #위에 가져온 영화 정보(기존 rank에 없는 )를 새로 db에 저장
#                 movie_info["title"],
#                 movie_info["score"],
#                 movie_info["img_url"],
#                 movie_info["ticketing"],
#                 movie_info["movie_rank"],
#                 movie_info["egg_gage"],
#                 movie_info["info"].strip(),
#                 movie_info["genre"],
#                 movie_info["img_url"],
#                 movie_info["link"]
#             )
#     # print(user_mtype)
#     # 데이터베이스에서 영화 정보 검색
#     # movies_from_users = DB.get_user_movie(user_mtype["mtype"]) # 사용자가 선택한 선호 장르(mtype)에 해당하는 영화 정보를 가져옴
#     # print("Debug - movies_from_users:", movies_from_users)

#     # # 만약 movies_from_users가 None이면 빈 리스트로 초기화
#     # movies_from_users = movies_from_users or []
#     # print(movies_from_users)

#     return render_template("index_copy.html", user=user)



# @app.route("/user/<uid>")
# def user(uid):
#     pass

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

