from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/api/apply-night-out', methods=['POST'])
def apply_night_out():
    data = request.get_json()
    
    if data['isNearJangHakSuk']:
        return jsonify({"status": "error", "message": "User is near JangHakSuk, no application needed"}), 400

    username = data['username']
    password = data['password']
    name = data['name']
    room = data['room']
    destination = data['destination']

    # Selenium 설정
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 로그인 페이지 열기
        driver.get("https://jeonju.jbiles.or.kr/bbs/login.php")
        
        # 로그인 수행
        driver.find_element(By.ID, "login_id").send_keys(username)
        driver.find_element(By.ID, "login_pw").send_keys(password)
        driver.find_element(By.ID, "btn_submit").click()

        # 외박 신청 페이지 열기
        driver.get("https://jeonju.jbiles.or.kr/bbs/write.php?bo_table=sub03_03")

        # 외박 신청 정보 입력
        driver.find_element(By.ID, "wr_name").send_keys(name)
        driver.find_element(By.ID, "wr_7").send_keys("외박")
        driver.find_element(By.ID, "wr_2").send_keys(room)
        driver.find_element(By.ID, "wr_3").send_keys(destination)

        # 귀사 예정일 계산 및 입력
        current_date = datetime.now()
        next_date = current_date + timedelta(days=1)
        return_date = next_date.strftime("%Y-%m-%d")
        driver.find_element(By.ID, "wr_5").send_keys(return_date)

        # 사유 입력
        driver.find_element(By.ID, "wr_content").send_keys("개인 사정")

        # 작성 완료 버튼 클릭
        driver.find_element(By.ID, "btn_submit").click()

        return jsonify({"status": "success", "message": "Night out application submitted"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
