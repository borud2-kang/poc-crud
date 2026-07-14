import os
import sys

# tests/ 폴더 기준으로 프로젝트 루트(json_poc.py, quick_sort_poc.py, crud_app.py가 있는 곳)를
# import 경로에 추가한다. 별도 패키지 설치 없이 `pytest`만으로 테스트가 돌아가게 하기 위함.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
