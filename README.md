# articulate-qqq (aq)

에디터에서 `???`/`!!!` 마커로 AI 사고 확장/답변을 트리거하는 CLI 도구.

## 설치

```bash
cd ~/workspace/service/articulate/articulate-qqq && ./install.sh
```

## 사용법

### 마커

파일 내 텍스트 뒤에 마커를 붙이면 처리됨:

```
어떤 개념 ???     → 3축 정교화 질문 생성
어떤 질문 !!!     → 답변 생성
```

마커는 처리 후 소비됨 (제거됨). 결과는 마커 아래에 들여쓰기로 삽입.

### CLI 명령

```bash
aq run <file>           # 파일의 마커를 한 번 처리
aq watch <file|dir>     # 파일 변경 감시 (폴링)
aq stop                 # 감시 중지
```

### 옵션

```bash
--dry-run              미리보기 (파일 수정 안 함)
--lang ko|en           응답 언어 강제
--prompt "..."         커스텀 지시 추가
--poll-interval N      폴링 간격 (초, 기본 1)
--glob "*.md"          감시 파일 패턴 (기본 *.md)
--timeout N            Claude 타임아웃 (초, 기본 30)
```

## 예시

### 입력 (test.md)

```markdown
# 학습 노트

함수형 프로그래밍 ???

모나드란 무엇인가 !!!
```

### 처리 후

```markdown
# 학습 노트

함수형 프로그래밍
  - [구분] 객체지향 프로그래밍과 어떤 점에서 다른가?
  - [구조] 순수 함수, 불변성, 고차 함수 등 핵심 구성요소는?
  - [관계] 타입 시스템, 카테고리 이론과의 연결은?

모나드란 무엇인가
  - 값을 감싸는 컨테이너로, 순차적 연산을 합성 가능하게 함
  - bind(>>=)로 함수를 체이닝하여 부수효과를 관리
  - Maybe, IO, List 등 다양한 인스턴스가 존재
```

## 요구사항

- Python 3.12+
- Claude CLI (`claude`)
