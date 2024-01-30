from datetime import datetime
import ftplib

import requests
from bs4 import BeautifulSoup
from flask import Flask, redirect, render_template, url_for, request, flash, session
from DB_handler_cgv import DBModule


headers = {
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
           }

base_url = "https://www.cgv.co.kr/movies/?lt=1&ft=0"

# detail_url = "http://www.cgv.co.kr/movies/detail-view/?midx=87554"


url = base_url

cookie = {"a" : "b"}

req = requests.get(url, headers=headers, timeout=5, cookies=cookie)

html = req.text

soup = BeautifulSoup(html,"html.parser")

sect_movie_chart = soup.select_one(".sect-movie-chart")

movie_chart = sect_movie_chart.select("li")

main_text_cgv = ""
main_text_cgv1 = "" #홀수
main_text_cgv2 = "" #짝수
for rank, movie in enumerate (movie_chart, 1):
    title = movie.select_one(".title")
    score = movie.select_one(".score")
    boximg = movie.select_one(".thumb-image > img") #영화포스터
    ticketing = score.select_one(".percent")
    egg_gage = score.select_one(".egg-gage.small > .percent")
    info = movie.select_one(".txt-info > strong").next_element
    link = movie.a['href'] #영화정보 연결
    link = f"https://www.cgv.co.kr{link}"

    detail_req = requests.get(link, headers=headers, timeout=5, cookies=cookie)
    detail_html = detail_req.text
    detail_soup = BeautifulSoup(detail_html, "html.parser")
    # genre = detail_soup.select_one(".spec > dl > dt").text.strip()

    dt_elements = detail_soup.select(".spec > dl > dt")  # detail에서 모든 dt 요소를 가져오기

    if len(dt_elements) >= 3:  # 만약 dt_elements에 3개 이상의 요소가 있다면, 세 번째 dt의 텍스트를 가져오기
        genre = dt_elements[2].text.strip()

        if '장르' not in genre or not genre.split("장르")[1].strip():
          genre = "장르 : 없음"

    else:
        genre = "장르 : 없음"    # dt_elements가 3개 미만인 경우 "장르 없음"으로 처리

    print(f"<<<{rank}위>>>")
    print(title.text)
    print(ticketing.get_text(" : "))
    print(f"실관람지수: {egg_gage.text}")
    # print(info.text.strip())
    print(f"{info.strip()} 개봉")
    print(link)
    print(genre)
    # print(f"https://www.cgv.co.kr{link}") #영화정보로 연결

    # if boximg["src"]:
    #     img_url = boximg["src"]
    #     print(img_url)
    #     print()
    if boximg and 'src' in boximg.attrs:
        img_url = boximg["src"]
        # img_url = img_url.replace("1200x1710ex", "230x230ex")
        print(img_url)
        print()
        if rank % 2 == 1:
            main_text_cgv1 += f"<div class='image-wrapper'><a href='{link}' target='_blank' class='image featured'><img src='{img_url}' alt='' /></a></div><p><h3>{rank}위: {title.text}</h3><b>개봉일: {info.text}</b><br><b>실관람지수(평점): {egg_gage.text}</b></br><b>{genre}</b></p>"
        else:
            rank % 2 == 0
            main_text_cgv2 += f"<div class='image-wrapper'><a href='{link}' target='_blank' class='image featured'><img src='{img_url}' alt='' /></a></div><p><h3>{rank}위: {title.text}</h3><b>개봉일: {info.text}</b><br><b>실관람지수(평점): {egg_gage.text}</b></br><b>{genre}</b></p>"
    rank += 1

    if rank == 11:
       break
    # main_text_cgv += f"<div class='image-wrapper'><a href='{link}' target='_blank' class='image featured'><img src='{img_url}' alt='' /></a></div><p><h2>{rank}위: {title.text}</h2><b>개봉일: {info.text}</b></p>"



    # if img.get("thumb-image"):
    #   img_url = f"http:{img.get('thumb-image')}"

    # print(img_url)
    # print()

# print(len(movie_chart))

# rank += 1


# if rank == 11:
#    break


# now = datetime.now()

# today_date = f"{now.year}년 {now.month}월 {now.day}일"

file_name = "index.html"
# file_name = "index copy.html"
title_text = f"오늘의 영화 Top10입니다."
summary_text = ""

html_text = f"""<!DOCTYPE HTML>
<!--
   Telephasic by HTML5 UP
   html5up.net | @ajlkn
   Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
-->
<html>
   <head>
        <title>{title_text}</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" />

        <!-- Google Fonts -->
        <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap" rel="stylesheet">

        <!-- MDB -->
        <link href="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/7.1.0/mdb.min.css" rel="stylesheet">

        <!-- Custom CSS (Assuming this is your custom stylesheet) -->
        <link rel="stylesheet" href="assets/css/main.css" />
    </head>
   <body class="homepage is-preload">
      <div id="page-wrapper">

         <!-- Header -->
            <div id="header-wrapper">
               <div id="header" class="container">

                  <!-- Logo -->
                     <h1 id="logo"><a href="index.html">Main</a></h1>

                  <!-- Nav -->
                     <nav id="nav">
                        <ul>
                           <li>
                              <a href="#">선택</a>
                              <ul>
                                 <li><a href="#">예매율순</a></li>
                                 <li><a href="#">평점순</a></li>
                                 <li><a href="#">관람객순</a></li>
                                    <!-- <li>
                                    <a href="#">Phasellus consequat</a>
                                     <ul>
                                        <li><a href="#">Lorem ipsum dolor</a></li>
                                        <li><a href="#">Phasellus consequat</a></li>
                                        <li><a href="#">Magna phasellus</a></li>
                                        <li><a href="#">Etiam dolore nisl</a></li>
                                     </ul>
                                  </li>   -->
                              </ul>
                           </li>
                           <li><a href="#"></a></li>
                           <li class="break"><a href="right-sidebar.html" id="btnSignin">
                              <i class="fas fa-sign-in-alt"></i>Manage</a></li>
                           <li><a href="no-sidebar.html" data-mdb-modal-init data-mdb-target="#basicExampleModal">SignIn</a></li>
                        </ul>
                     </nav>
                            <!-- Modal -->
                        <div class="modal top fade" id="basicExampleModal" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true" data-mdb-backdrop="true" data-mdb-keyboard="true">
                        <div class="modal-dialog  ">
                            <div class="modal-content">
                            <div class="modal-header">
                                <h3 class="modal-title" id="exampleModalLabel"><strong><i class="i.fas.fa-sign-in-alt"></i>Sign In</strong></h3>
                                <button type="button" class="btn-close" data-mdb-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">

                                <form style="width: 29rem;">
                                <!-- Name input -->
                                <div data-mdb-input-init class="form-outline mb-4">
                                    <input type="text" id="form4Example1" class="form-control" />
                                    <label class="form-label" for="form4Example1">Name</label>
                                </div>

                                <!-- Email input -->
                                <div data-mdb-input-init class="form-outline mb-4">
                                    <input type="email" id="form4Example2" class="form-control" />
                                    <label class="form-label" for="form4Example2">Email address</label>
                                </div>

                                <!-- Message input -->
                                <div data-mdb-input-init class="form-outline mb-4">
                                    <textarea class="form-control" id="form4Example3" rows="4"></textarea>
                                    <label class="form-label" for="form4Example3">Message</label>
                                </div>

                                <!-- Checkbox -->
                                <div class="form-check d-flex justify-content-center mb-4">
                                    <input
                                    class="form-check-input me-2"
                                    type="checkbox"
                                    value=""
                                    id="form4Example4"
                                    checked
                                    />
                                    <label class="form-check-label" for="form4Example4">
                                    Send me a copy of this message
                                    </label>
                                </div>

                                <!-- Submit button -->
                                <button data-mdb-ripple-init type="button" class="btn btn-primary btn-block mb-4">Send</button>
                                </form>
                            </div>
                           <!--  <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-mdb-dismiss="modal">
                                Close
                                </button>
                                <button type="button" class="btn btn-primary">Save changes</button>
                            </div> -->
                            </div>
                        </div>
                        </div>

               </div>

               <!-- Hero -->
                  <section id="hero" class="container">
                     <header>
                        <h2>{title_text}</h2>
                     </header>
                     <!-- <ul class="actions">
                        <li><a href="#" class="button">Get this party started</a></li>
                     </ul> -->
                  </section>

            </div>

         <!-- Features 1 -->
            <div class="wrapper">
               <div class="container">
                  <div class="row">
                     <section class="col-6 col-12-narrower feature">

                        <header>
                           <h2></h2>
                        </header>
                         {main_text_cgv1}
                        <ul class="actions">
                           <!--<li><a href="#" class="button">Elevate my awareness</a></li> -->
                        </ul>
                     </section>
                     <section class="col-6 col-12-narrower feature">
                        <header>
                           <!--<h2>Amet lorem ipsum dolor<br />
                           sit consequat magna</h2>-->
                        </header>
                                    {main_text_cgv2}
                        <!--p>Lorem ipsum dolor sit amet consectetur et sed adipiscing elit. Curabitur vel
                        sem sit dolor neque semper magna. Lorem ipsum dolor sit amet consectetur et sed
                        adipiscing elit. Curabitur vel sem sit.</p> -->
                        <ul class="actions">
                           <!--<li><a href="#" class="button">Elevate my awareness</a></li> -->
                        </ul>
                     </section>
                  </div>
               </div>
            </div>

         <!-- Features 2 -->
            <!-- <div class="wrapper">
               <section class="container">
                  <header class="major">
                     <h2>Sed magna consequat lorem curabitur tempus</h2>
                     <p>Elit aliquam vulputate egestas euismod nunc semper vehicula lorem blandit</p>
                  </header>
                  <!--{main_text_cgv} -->
                  <ul class="actions major">
                     <li><a href="#" class="button">Elevate my awareness</a></li>
                  </ul>
               </section>
            </div> -->

         <!-- Footer -->
            <!-- <div id="footer-wrapper">
               <div id="footer" class="container">
                  <header class="major">
                     <h2>Euismod aliquam vehicula lorem</h2>
                     <p>Lorem ipsum dolor sit amet consectetur et sed adipiscing elit. Curabitur vel sem sit<br />
                     dolor neque semper magna lorem ipsum feugiat veroeros lorem ipsum dolore.</p>
                  </header>
                  <div class="row">
                     <section class="col-6 col-12-narrower">
                        <form method="post" action="#">
                           <div class="row gtr-50">
                              <div class="col-6 col-12-mobile">
                                 <input name="name" placeholder="Name" type="text" />
                              </div>
                              <div class="col-6 col-12-mobile">
                                 <input name="email" placeholder="Email" type="text" />
                              </div>
                              <div class="col-12">
                                 <textarea name="message" placeholder="Message"></textarea>
                              </div>
                              <div class="col-12">
                                 <ul class="actions">
                                    <li><input type="submit" value="Send Message" /></li>
                                    <li><input type="reset" value="Clear form" /></li>
                                 </ul>
                              </div>
                           </div>
                        </form>
                     </section>
                     <section class="col-6 col-12-narrower">
                        <div class="row gtr-0">
                           <ul class="divided icons col-6 col-12-mobile">
                              <li class="icon brands fa-twitter"><a href="#"><span class="extra">twitter.com/</span>untitled</a></li>
                              <li class="icon brands fa-facebook-f"><a href="#"><span class="extra">facebook.com/</span>untitled</a></li>
                              <li class="icon brands fa-dribbble"><a href="#"><span class="extra">dribbble.com/</span>untitled</a></li>
                           </ul>
                           <ul class="divided icons col-6 col-12-mobile">
                              <li class="icon brands fa-instagram"><a href="#"><span class="extra">instagram.com/</span>untitled</a></li>
                              <li class="icon brands fa-youtube"><a href="#"><span class="extra">youtube.com/</span>untitled</a></li>
                              <li class="icon brands fa-pinterest"><a href="#"><span class="extra">pinterest.com/</span>untitled</a></li>
                           </ul>
                        </div>
                     </section>
                  </div>
               </div>
               <div id="copyright" class="container">
                  <ul class="menu">
                     <li>&copy; Untitled. All rights reserved.</li><li>Design: <a href="http://html5up.net">HTML5 UP</a></li>
                  </ul>
               </div>
            </div> -->
      </div>

        <!-- Scripts -->
        <script src="assets/js/jquery.min.js"></script>
        <script src="assets/js/jquery.dropotron.min.js"></script>
        <script src="assets/js/browser.min.js"></script>
        <script src="assets/js/breakpoints.min.js"></script>
        <script src="assets/js/util.js"></script>
        <script src="assets/js/main.js"></script>
        <!-- MDB -->
        <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/7.1.0/mdb.umd.min.js"></script>

        $('#basicExampleModal').modal('show');
   </body>
</html>"""
with open(f"html5up-telephasic/{file_name}", "w", encoding="utf8") as f:
    f.write(f"{html_text}")