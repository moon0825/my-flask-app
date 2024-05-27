from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import datetime
import time
app = Flask(__name__)

# 오늘 날짜
today = datetime.date.today()

# 신청날의 다음날 계산
next_day = today + datetime.timedelta(days=1)

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

        # driver.find_element(By.ID, "wr_7").click()  # 드롭다운 메뉴 열기
        # time.sleep(1)  # 대기
        # driver.find_element(By.XPATH, "//option[contains(text(), '외박')]").click()  # 외박 선택
        time.sleep(1)  # 대기



        # 행선지 선택
        driver.find_element(By.ID, "wr_3").click()  # 드롭다운 메뉴 열기
        time.sleep(2)  # 대기
        driver.find_element(By.XPATH, "//option[contains(text(), '본가')]").click()  # 행선지 선택
        time.sleep(1)  # 대기

        # 신청일 입력
        driver.find_element(By.ID, "wr_4").send_keys(datetime.now().strftime("%Y-%m-%d"))
        time.sleep(1)  # 입력 대기


        # 귀사 예정일 입력란 클릭
        driver.find_element(By.ID, "wr_5").click()
        time.sleep(1)  # 대기

            # 달력에서 사용자가 입력한 날짜의 년도와 월을 선택
        while True:
            calendar_year = int(driver.find_element(By.CLASS_NAME, "ui-datepicker-year").text)
            calendar_month = datetime.datetime.strptime(driver.find_element(By.CLASS_NAME, "ui-datepicker-month").text, "%B").month

            if calendar_year == year and calendar_month == month:
                break
            elif target_date < today:
                print("이미 지난 날짜입니다. 유효한 날짜를 다시 입력하세요.")
                driver.quit()
                exit()
            elif calendar_year < year or (calendar_year == year and calendar_month < month):
                # 다음 달로 이동
                driver.find_element(By.CLASS_NAME, "ui-datepicker-next").click()
            else:
                # 이전 달로 이동
                driver.find_element(By.CLASS_NAME, "ui-datepicker-prev").click()
    
        # 사용자가 입력한 날짜 선택
        driver.find_element(By.XPATH, f"//a[contains(text(), '{day}')]").click()  # 귀사 예정일 선택
        time.sleep(1)  # 대기

        # 달력에서 다음날 날짜 선택
        driver.find_element(By.XPATH, f"//a[contains(text(), '{next_day.day}')]").click()  # 귀사 예정일 선택
        time.sleep(1)  # 대기

        # 사유 입력
        driver.find_element(By.ID, "wr_content").send_keys("외박 신청합니다.")
        time.sleep(1)  # 입력 대기z

        # 작성완료 버튼 클릭
        driver.find_element(By.ID, "btn_submit").click()
        time.sleep(3)  # 작성 완료 대기

        print("외박신청이 성공적으로 작성되었습니다.")

        return jsonify({"status": "success", "message": "Night out application submitted"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

