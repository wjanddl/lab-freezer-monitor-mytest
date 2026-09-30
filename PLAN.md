# Plan: 이메일 목록 중복 제거 스크립트

## Goal
`dedup.py` — 한 줄에 이메일 하나인 텍스트 파일에서 중복을 제거하고 **원본 파일을 덮어쓴다**.

## Acceptance criteria
1. `python dedup.py emails.txt` 실행 시 `emails.txt`가 중복 제거된 내용으로 바뀐다.
2. 중복 판정: 앞뒤 공백 제거 후 대소문자 무시 (`" A@X.com "` == `"a@x.com"`).
3. 첫 등장 줄을 유지하고(공백은 제거된 형태로), 원래 순서를 보존한다.
4. 빈 줄(공백만 있는 줄 포함)은 제거한다. 이메일 형식 검증은 하지 않는다 — 나머지 줄은 모두 유지.
5. 제거 개수를 stderr에 출력한다 (예: `kept 3, removed 2`).
6. 덮어쓰기는 원자적: 같은 디렉터리의 임시 파일에 쓴 뒤 `os.replace`. 중간 실패 시 원본은 그대로.
7. 인자 누락/파일 없음 → 0이 아닌 종료 코드와 메시지.

## Approach
- 표준 라이브러리만 (`sys`, `os`, `tempfile`, `shutil`). 외부 의존성 없음.
- 교체 순서: 같은 디렉터리에 `tempfile.mkstemp` → 내용 쓰기·닫기 → `shutil.copymode(원본, 임시)` → `os.replace(임시, 원본)`. 어느 단계든 실패하면 임시 파일 삭제 후 오류 전파.
- 입력은 `utf-8-sig`로 읽어 BOM을 흡수, 출력은 `utf-8`, 줄바꿈 `\n`, 마지막 줄 뒤 개행 포함.
- 키: `line.strip().casefold()`; `set`으로 본 키 추적.
- Python 3.6 호환 (이 머신 PATH의 `python`이 3.6.8).

## Non-goals
이메일 유효성 검증, gmail 점/`+태그` 정규화, CSV 파싱, 백업 파일, 원본 줄바꿈 스타일 보존.

## Risks
- 원본 덮어쓰기는 사용자 선택. 원자적 교체로 부분 쓰기 손상만 방지 (되돌리기는 불가).
- 권한 비트는 `shutil.copymode`로 원본 것을 유지 (소유자/ACL은 유지 안 됨 — non-goal).

## Verification
`python test_dedup.py` (assert 기반, 임시 디렉터리 사용) → 종료 코드 0, `OK` 출력. 확인 항목:
- 입력 `"a@x.com\n A@X.com \n\nb@y.com\nnot-an-email\nb@y.com\n"` → 파일 내용 `"a@x.com\nb@y.com\nnot-an-email\n"`
- BOM이 있는 입력도 첫 줄이 올바르게 중복 판정됨.
- 없는 파일 경로 → 종료 코드 != 0.
