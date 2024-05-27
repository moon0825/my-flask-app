from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import datetime
import time
import tempfile


app = Flask(__name__)

@app.route('/api/apply-night-out', methods=['POST'])
def apply_night_out():
    data = request.get_json()

    if data['isNearJangHakSuk']:
        return jsonify({"status": "error", "message": "User is near JangHakSuk, no application needed"}), 400

    username = data['username']
    password = data['password']
    destination = data['destination']

    # 신청일 가져오기
    application_date_str = data['application_date']
    application_date = datetime.datetime.strptime(application_date_str, "%Y-%m-%d")
    next_day = application_date + datetime.timedelta(days=1)

    # Selenium 설정
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    temp_dir = tempfile.TemporaryDirectory()
    chrome_options.add_argument(f"--user-data-dir={temp_dir.name}")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 로그인 페이지 열기
        driver.get("https://jeonju.jbiles.or.kr/bbs/login.php")
        time.sleep(1)
        # 로그인 수행
        driver.find_element(By.ID, "login_id").send_keys(username)
        time.sleep(1)
        driver.find_element(By.ID, "login_pw").send_keys(password)
        time.sleep(1)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_submit"))).click()       
        time.sleep(2)
        
        # 외박 신청 페이지 열기
        driver.get("https://jeonju.jbiles.or.kr/bbs/write.php?bo_table=sub03_03")
        time.sleep(2)
        
        # 신청 종류 선택
        driver.find_element(By.ID, "wr_7").send_keys("외박")  # 외박 선택
        time.sleep(1)  # 대기

        # 행선지 선택
        driver.find_element(By.ID, "wr_3").click()  # 드롭다운 메뉴 열기
        time.sleep(2)  # 대기
        driver.find_element(By.XPATH, "//option[contains(text(), '본가')]").click()  # 행선지 선택
        time.sleep(1)  # 대기

        # 귀사 예정일 입력란 클릭
        driver.find_element(By.ID, "wr_5").click()
        time.sleep(1)  # 대기

        # 달력에서 년도 선택
        Select(driver.find_element(By.CLASS_NAME, "ui-datepicker-year")).select_by_value(str(next_day.year))
        time.sleep(1)
        
        # 달력에서 월 선택
        Select(driver.find_element(By.CLASS_NAME, "ui-datepicker-month")).select_by_value(str(next_day.month - 1))  # 월은 0부터 시작
        time.sleep(1)
        
        # 달력에서 다음날 날짜 선택
        driver.find_element(By.XPATH, f"//a[text()='{next_day.day}']").click()
        time.sleep(1)  # 대기

        # 사유 입력
        driver.find_element(By.ID, "wr_content").send_keys("외박 신청합니다.")
        time.sleep(1)  # 입력 대기

        # 작성완료 버튼 클릭
        driver.find_element(By.ID, "btn_submit").click()
        time.sleep(3)  # 작성 완료 대기

        print("외박신청이 성공적으로 작성되었습니다.")

        return jsonify({"status": "success", "message": "Night out application submitted"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        driver.quit()

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"status": "error", "message": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
