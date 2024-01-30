# import pyrebase
import pymysql
import json

class DBModule: #DB와 연결하는 부분
    #cursor는 데이터베이스 객체
    #%s는 플레이스 홀더로 튜플의 값으로 대체
    #execute 메서드는 데이터베이스 커서 객체에서 제공하는 메서드 sql실행, 두개의 인자 필요 (쿼리문, 파라미터 담는 튜플)
    #__init__은 파이썬 클래스 생성자 =>mariadb와 연결할떄 사용
    def __init__(self):
        # firebase사용부분
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

        self.connection = pymysql.connect(**db_config) #딕셔너리의 키-값 쌍을 함수의 인수로 전달
        self.cursor = self.connection.cursor() #커서는 SQL 쿼리를 실행하고 결과를 다룸

#로그인 기능
    def login(self, uid, pwd):
        try:
            # if self.cursor.closed:
            #     self.cursor = self.connection.cursor()

            query = "SELECT * FROM users WHERE uid=%s AND pwd=%s" # 주어진 사용자 아이디와 비밀번호로 데이터베이스에서 조회
            self.cursor.execute(query, (uid, pwd)) #데이터베이스에 쿼리를 실행
            user_info = self.cursor.fetchone() #쿼리 실행 결과 중 첫 번째 레코드를 가져와 user_info에 저장 =>여기선 db에저장된 사용자의 정보 반환
            # print(user_info)
            if user_info: #사용자 정보가 있으면
                return True #true반환
            else:
                return False
        except Exception as e:  # 어떤 예외가 발생하면 해당예외를 변수 e에 할당
            print(f"에러: {e}") # 콘솔에 에러 메시지를 출력,f-string으로 예외 메시지를 문자열에 삽입
            raise e #예외를 다시 호출자로 던짐

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
        self.cursor.execute(query, (uid,))
        user_info = self.cursor.fetchone()
        if user_info:
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
            # 회원가입 정보를 데이터베이스에 추가 실제db에 uid로 저장, 여기서 매개변수명은 _id_
            query = "INSERT INTO users (uid, pwd, uname, mtype) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (_id_, pwd, name, mtype))#데이터베이스에 쿼리를 실행
            self.connection.commit()
            return True
        else:
            return False

# 관리자 페이지 영화 수정
    def update_movie_info(self, info, egg_gage, genre, title):
        try:
             # 주어진 제목의 영화 정보를 업데이트
            query = """
                UPDATE movies
                SET info = %s, egg_gage = %s, genre = %s
                WHERE title = %s
            """
            self.cursor.execute(query, (info, egg_gage, genre, title))
            self.connection.commit()
            print("영화정보가 성공적으로 수정되었습니다.")
        except Exception as e:
            print(f"Error1: {e}")
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
            print(f"Error2: {e}")
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
                print(f"Error3: {e}")
            # 예외가 발생했을 때에도 커서를 닫지 않고 예외를 다시 던짐
                raise e


#크롤링한 영화정보 저장
    def save_movie_info(self, title, score, boximg, ticketing, movie_rank, egg_gage, info, genre, img_url, link):
        try:
            # 주어진 정보로 영화 정보를 데이터베이스에 추가합니다
            query = """
                INSERT INTO movies (title, score, boximg, ticketing, movie_rank, egg_gage, info, genre, img_url, link)
                VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s, %s )
            """
            self.cursor.execute(query, (title, score, boximg, ticketing, movie_rank, egg_gage, info, genre, img_url, link))
            self.connection.commit()
            print("데이터가 데이터베이스에 성공적으로 삽입되었습니다.")
        except Exception as e:
            print(f"Error4: {e}")
        # 예외가 발생했을 때에도 커서를 닫지 않고 예외를 다시 던짐
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
    def get_movies(self, mtype=None, num_param=None):
        try:
            if mtype is not None: #mtype값이 있을떄
                #데이터베이스에서 영화정보와 사용자 정보 조회
                query = """
                    SELECT *
                    FROM users A, movies B
                    WHERE B.genre LIKE %s  AND A.mtype =%s
                    ORDER BY B.movie_rank;
                """
                self.cursor.execute(query, (('%' + mtype + '%', mtype)))
                movies = self.cursor.fetchall()
                return movies if movies is not None else []
            #영화목록 반환 종류3개
            elif num_param == 1:
                #숫자와 소수점만 추출하여 순자로 변환한뒤 orderby 지정순서대로 정렬
                query = """
                    SELECT *,  CAST(REGEXP_REPLACE(ticketing, '[^0-9.]', '') AS DECIMAL(5, 2)) AS booking_rate FROM movies ORDER BY booking_rate desc ;
                """
                self.cursor.execute(query)
                movies = self.cursor.fetchall() #쿼리 실행 결과값 가져오기
                return movies if movies is not None else []
            elif num_param == 2:
                query = """
                    SELECT *,  CAST(REGEXP_REPLACE(egg_gage, '[^0-9.]', '') AS DECIMAL(5, 2)) AS booking_rate FROM movies ORDER BY booking_rate desc ;
                """
                self.cursor.execute(query)
                movies = self.cursor.fetchall()
                return movies if movies is not None else []
            elif num_param == 3:
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
            print(f"Error5: {e}")


    def get_movie_by_rank(self, movierank):
        try:
            query = "SELECT * FROM movies WHERE movie_rank = %s"
            self.cursor.execute(query, (movierank))
            movie = self.cursor.fetchone() # 첫 번째 결과 행을 가져오고 반환
            return movie
        except Exception as e:
            print(f"Error6: {e}")

    def get_movie_by_uid(self, uid):
        try:
            query = "SELECT * FROM users WHERE uid = %s"
            self.cursor.execute(query, (uid,))
            movie = self.cursor.fetchone()
            return movie
        except Exception as e:
            print(f"Error7: {e}")

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
