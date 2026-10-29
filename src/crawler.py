import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 💡 유저님이 직접 찾아주신 정확한 규정 게시판 URL!
TARGET_BOARD_URL = "https://www.comwel.or.kr/comwel/info/laws/rule.jsp?mode=list&board_no=69&pager.offset=0"

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    # 혹시 모를 브라우저 튕김 방지 옵션 추가
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def crawl_kcomwel_rules():
    driver = setup_driver()
    print("🚀 근로복지공단 규정 게시판 크롤링을 시작합니다...")

    try:
        driver.get(TARGET_BOARD_URL)
        time.sleep(3) 

        # 공단 홈페이지 구조에 맞는 패턴 찾기 (td 태그 안의 a 태그)
        elements = driver.find_elements(By.CSS_SELECTOR, "table tbody tr td a")
        
        link_scripts = []
        for el in elements:
            text = el.text.strip()
            href = el.get_attribute('href')
            
            # 'mode=view'가 포함되어 있거나 일반적인 게시물 링크 구조인 경우만 수집
            if href and len(text) > 2 and ("view" in href or "javascript" in href or "board" in href):
                link_scripts.append((text, href))

        # 중복 링크 제거
        unique_links = []
        seen_hrefs = set()
        for text, href in link_scripts:
            if href not in seen_hrefs:
                unique_links.append((text, href))
                seen_hrefs.add(href)

        # 테스트용으로 맨 위 최신 글 3개만 추출
        test_links = unique_links[:3]

        if not test_links:
            print("❌ 링크를 찾지 못했습니다. 게시판 HTML 구조가 변경되었을 수 있습니다.")
            return

        print(f"✅ 총 {len(test_links)}개의 게시물을 성공적으로 찾았습니다!")

        for idx, (text, url) in enumerate(test_links):
            print(f"\n[{idx+1}] 게시물 접속 중... (제목: {text[:20]}...)")
            
            # 자바스크립트 링크인지 일반 링크인지 구분하여 클릭
            if "javascript:" in url:
                driver.execute_script(url.replace("javascript:", ""))
            else:
                driver.get(url)
                
            time.sleep(3) # 글 내용이 뜰 때까지 대기

            # 본문 텍스트 추출
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # 공공기관 게시판 본문 영역 주로 쓰이는 클래스 찾기
            view_area = soup.select_one(".board_view, .board-view, table.view, .bbs_view")
            if view_area:
                content = view_area.text.strip()
            else:
                content = soup.text.strip()
            
            # 파일명으로 쓸 수 없는 특수문자 제거
            safe_title = "".join(c for c in text if c.isalnum() or c in " _-").strip()
            file_path = os.path.join(DATA_DIR, f"{safe_title}.txt")
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content[:1500]) # 확인용으로 우선 1500자만 저장
            print(f"  - 📄 본문 텍스트 저장 완료: {safe_title}.txt")
            
            # 다음 글을 수집하기 위해 다시 목록 페이지로 돌아가기
            driver.get(TARGET_BOARD_URL)
            time.sleep(3)

    except Exception as e:
        print(f"크롤링 중 에러 발생: {e}")
    finally:
        driver.quit()
        print("\n✅ 크롤링 테스트 작업이 종료되었습니다.")

if __name__ == "__main__":
    crawl_kcomwel_rules()