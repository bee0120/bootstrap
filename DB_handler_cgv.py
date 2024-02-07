
import pymysql
import json

class DBModule: #DB와 연결하는 부분
    def __init__(self):
        # with open("./auth/firebaseAuth.json") as f:
        #     config = json.load(f)
        # firebase = pyrebase.initialize_app(config)
        # self.db = firebase.database()
            # MariaDB 연결 정보
        db_config = {
            'host': '13.209.89.41',
            'user': 'user1',
            'password': 'dnbi0120',
            'database': 'project1',
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

        self.connection = pymysql.connect(**db_config)
        self.cursor = self.connection.cursor()
#크롤링한 영화정보 저장
    def save_movie_info(self, title, score, boximg, ticketing, movie_rank, egg_gage, info, genre, img_url, link):
        try:
            # 쿼리 문자열을 작성하여 영화 정보를 데이터베이스에 추가
            query = """
                INSERT INTO movies (title, score, boximg, ticketing, movie_rank, egg_gage, info, genre, img_url, link)
                VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s, %s )
            """
            self.cursor.execute(query, (title, score, boximg, ticketing, movie_rank, egg_gage, info, genre, img_url, link)) # 데이터베이스 커서를 사용하여 쿼리를 실행하고, 주어진 영화 정보를 데이터베이스에 삽입
            self.connection.commit()  # 데이터베이스에 대한 변경사항을 커밋(적용)
            print("데이터가 데이터베이스에 성공적으로 삽입되었습니다.")
        except Exception as e:
            # 예외가 발생했을 때에도 커서를 닫지 않고 예외를 다시 던짐
            print(f"Error: {e}")
            raise e
        # 테스트 코드
        # if __name__ == "__main__":
        #     # 적절한 데이터로 replace
        #     db = DBModule()
        #     db.save_movie_info("Movie Title",  "image_url", "movie_link")
#크롤링한 영화 정보 호출
    # def get_movies(self):
    #     try:
    #         query = "SELECT * FROM movies"
    #         self.cursor.execute(query)
    #         movies = self.cursor.fetchall()
    #         return movies if movies is not None else []  # None이면 빈 리스트 반환
    #     except Exception as e:
    #         print(f"Error: {e}")
        # finally:
        #     self.cursor.close()
#영화 정보 가져오기
    def get_movies(self, mtype=None, num_param=None, uid=None):
        try:
            if mtype is not None and uid is not None: #mtype값이 있을떄
               # 특정 장르(mtype)와 사용자 아이디(uid)에 따라 데이터베이스에서 영화 및 사용자 정보를 조회
                query = """
                    SELECT *
                    FROM users A, movies B
                    WHERE B.genre LIKE %s  AND A.mtype =%s And A.uid = %s
                    ORDER BY B.movie_rank;
                """
                self.cursor.execute(query, (('%' + mtype + '%', mtype, uid)))
                movies = self.cursor.fetchall()#fetchall()은 실행된 쿼리의 결과를 모두 가져오는 메소드, 가져온 결과는 리스트 형태로 반환되어 movies 변수에 저장
                return movies if movies is not None else []
            #영화목록 반환 종류3개
            #CAST()는 괄호 안의 표현식을 실수로 변환하는데 사용, DECIMAL(5,2)5자리중 2자리를 소수점으로 가지는 형태,REGEXP_REPLACE(ticketing, '[^0-9.]', ') 주어진 ticketing 데이터에서 숫자와 소수점이외의 모든 문자 제거
            elif num_param == 1:
                #숫자와 소수점만 추출하여 값을 실수로 변환한뒤 orderby 지정순서대로 정렬( 예매율을 기준으로 내림차순으로 정렬하여 영화 목록을 가져옴)
                query = """
                    SELECT *,  CAST(REGEXP_REPLACE(ticketing, '[^0-9.]', '') AS DECIMAL(5, 2)) AS booking_rate FROM movies ORDER BY booking_rate desc ;
                """
                self.cursor.execute(query)
                movies = self.cursor.fetchall() #쿼리 실행 결과값 가져오기
                return movies if movies is not None else []
            elif num_param == 2:  # 평점을 기준으로 내림차순으로 정렬하여 영화 목록을 가져옴
                query = """
                    SELECT *,  CAST(REGEXP_REPLACE(egg_gage, '[^0-9.]', '') AS DECIMAL(5, 2)) AS booking_rate FROM movies ORDER BY booking_rate desc ;
                """
                self.cursor.execute(query)
                movies = self.cursor.fetchall()
                return movies if movies is not None else []
            elif num_param == 3:   # 영화 개봉일을 기준으로 내림차순으로 정렬하여 영화 목록을 가져옴
                query = """
                    SELECT * FROM movies ORDER BY info desc ;
                """
                self.cursor.execute(query)
                movies = self.cursor.fetchall()
                return movies if movies is not None else []
            else:
                # 기본적으로 모든 영화를 가져오는 쿼리
                query = "SELECT * FROM movies"
                self.cursor.execute(query)
                movies = self.cursor.fetchall()
                return movies if movies is not None else []
        except Exception as e:
            print(f"Errorget_movies: {e}")


    def get_movie_by_rank(self, movierank):
        try:
            query = "SELECT * FROM movies WHERE movie_rank = %s"
            self.cursor.execute(query, (movierank,))
            movie = self.cursor.fetchone() # 첫 번째 결과 행을 가져오고 반환
            return movie
        except Exception as e:
            print(f"Error: {e}")

    def get_movie_by_uid(self, uid):
        try:
            query = "SELECT * FROM users WHERE uid = %s"
            self.cursor.execute(query, (uid,))
            movie = self.cursor.fetchone()
            return movie
        except Exception as e:
            print(f"Error: {e}")
#로그인 기능
    def login(self, uid, pwd):
        try:
            # if self.cursor.closed:
            #     self.cursor = self.connection.cursor()

            query = "SELECT * FROM users WHERE uid=%s AND pwd=%s" # 주어진 사용자 아이디와 비밀번호로 데이터베이스에서 조회
            self.cursor.execute(query, (uid, pwd)) #데이터베이스에 쿼리를 실행
            user_info = self.cursor.fetchone() #쿼리 실행 결과 중 첫 번째 레코드를 가져와 user_info에 저장

            if user_info: #사용자 정보가 있으면
                return True #true반환
            else:
                return False
        except Exception as e:  # 예외가 발생하면 에러 메시지를 출력하고 예외를 다시 던집니다.
            print(f"에러: {e}") # 에러 메시지를 출력하고
            raise e #예외를 다시 던짐

#회원가입 여부 검사
    def signin_verification(self, uid):
        # users = self.db.child("users").get().val()
        # for i in users:
        #     if uid == i:
        #         return False
        # return True
    #  print(users)
    # 주어진 사용자 아이디로 이미 가입되어 있는지 여부를 데이터베이스에서 확인
        query = "SELECT * FROM users WHERE uid=%s"
        self.cursor.execute(query, (uid,))#DB에 쿼리 전송
        user_info = self.cursor.fetchone() #: 실행된 쿼리 결과 중 첫 번째 레코드를 가져와서 user_info에 저장
        if user_info: ## 저장된 아이디가 존재하면 (이미 가입되어 있다면)
            return False
        else:
            return True

#회원가입
    def signin(self, _id_, pwd, name, mtype):
            # information = {
            #     "pwd": pwd,
            #     "uname": name,
            #     "email": email
            # }
            # if self.signin_verification(_id_):
            #     self.db.child("users").child(_id_).set(information)
            #     return True
            # else:
            #     return False
        #회원가입 전에 중복된 아이디가 있는지 검증
        if self.signin_verification(_id_):
            # 회원가입 정보를 데이터베이스에 추가 실제db에 uid로 저장, 여기서 내가 임의로 지정한 매개변수명은 _id_
            query = "INSERT INTO users (uid, pwd, uname, mtype) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (_id_, pwd, name, mtype))#데이터베이스에 값넘겨주고 쿼리를 실행
            self.connection.commit()
            return True
        else:
            return False

# 관리자 페이지 영화 수정
    def update_movie_info(self, info, egg_gage, genre, title):
        try:
             # 주어진 제목의 영화 정보를 수정 한후 업데이트
            query = """
                UPDATE movies
                SET info = %s, egg_gage = %s, genre = %s
                WHERE title = %s
            """
            self.cursor.execute(query, (info, egg_gage, genre, title))
            self.connection.commit()
            print("영화정보가 성공적으로 수정되었습니다.")
        except Exception as e:
            print(f"Error: {e}")
        # 예외가 발생했을 때에도 커서를 닫지 않고 예외를 다시 던짐
            raise e

# 관리자 페이지 영화 삭제
    def delete_movie_by_title(self, title):
        try:
            query = "DELETE FROM movies WHERE title = %s"
            self.cursor.execute(query, (title))
            self.connection.commit()
            print("영화정보가 성공적으로 삭제되었습니다.")
        except Exception as e:
            print(f"Error: {e}")
            raise e
#관리자 페이지 영화 추가
    def add_movie_info(self, movie_rank, title, info, egg_gage, genre, img_url):
            try:
                query = """
                    INSERT INTO movies (movie_rank, title, info, egg_gage, genre, img_url) VALUES (%s, %s, %s, %s, %s, %s)"""
                self.cursor.execute(query, (movie_rank, title, info, egg_gage, genre, img_url))
                self.connection.commit()
                print("영화정보가 성공적으로 추가되었습니다.")
            except Exception as e:
                print(f"Error: {e}")
            # 예외가 발생했을 때에도 커서를 닫지 않고 예외를 다시 던짐
                raise e

# #개인 사용자별 영화정보
#     def get_user_movie(self, mtype):
#         try:
#             query = """
#                 SELECT *
#                 FROM users A, movies B
#                 WHERE B.genre LIKE %s  AND A.mtype =%s
#                 ORDER BY B.movie_rank;
#             """
#             self.cursor.execute(query, (('%' + mtype + '%', mtype)))
#             movies = self.cursor.fetchall()
#             print("Debug - movies:", movies)
#             return movies if movies is not None else []  # None이면 빈 리스트 반환
#         except Exception as e:
#             print(f"Error: {e}")


    # def write_post(self, user, contents):
    #     pass
    # def post_list(self):
    #     pass
    # def post_detail(self, pid):
    #     pass
    # def get_user(self, uid):
    #     pass