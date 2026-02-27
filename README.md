# articulate-qqq (aq)

에디터에서 `???`/`!!!` 마커로 AI 사고 확장/답변을 트리거하는 CLI 도구.
파일 저장만 하면 AI가 자동으로 개념을 확장하거나 질문에 답변합니다.

## 설치

```bash
# 원라인 설치
curl -fsSL https://raw.githubusercontent.com/kangthink/articulate-qqq/main/install.sh | bash

# 또는 로컬 설치
git clone https://github.com/kangthink/articulate-qqq.git
cd articulate-qqq && ./install.sh
```

### 업데이트

```bash
aq update
```

### 요구사항

- Python 3.12+
- AI CLI 하나 이상 설치:
  - [Claude CLI](https://docs.anthropic.com/en/docs/claude-code) (기본)
  - [Gemini CLI](https://github.com/google-gemini/gemini-cli)
  - [Codex CLI](https://github.com/openai/codex)

## 마커

파일 내 텍스트 뒤에 마커를 붙이면 AI가 처리합니다.

| 마커 | 동작 | 설명 |
|------|------|------|
| `???` | 질문 생성 | 개념을 다양한 각도에서 파고드는 질문 3~5개 |
| `!!!` | 답변 생성 | 간결하고 실용적인 답변 2~5개 불릿 |

- 마커는 처리 후 **소비됨** (제거됨)
- 결과는 마커 위치에 **들여쓰기**로 삽입
- 실패 시 마커가 유지되어 **재시도 가능**

## CLI

```bash
aq run <file>           # 마커를 한 번 처리
aq watch <file|dir>     # 파일 변경 감시 (폴링)
aq stop                 # 감시 중지
aq update               # 최신 버전으로 업데이트
```

### 옵션

```bash
--model claude|gemini|codex   AI 프로바이더 (기본: claude)
--structure                   ??? 마커에 3축 구조화 질문 사용 (기본: 자유형)
--dry-run                     미리보기 (파일 수정 안 함)
--lang ko|en                  응답 언어 강제
--prompt "..."                커스텀 지시 추가
--poll-interval N             폴링 간격 (초, 기본 1)
--glob "*.md"                 감시 파일 패턴 (기본 *.md)
--timeout N                   AI CLI 타임아웃 (초, 기본 120)
```

## 에디터 설정

### Neovim

`~/.config/nvim/lua/config/options.lua`에 추가:

```lua
vim.opt.autoread = true
vim.api.nvim_create_autocmd({ "FocusGained", "BufEnter", "CursorHold" }, {
  command = "checktime",
})
```

터미널에서 `aq watch .` 실행 후, nvim에서 마커를 쓰고 저장하면 결과가 자동 반영됩니다.

### 기타 에디터

`autoread` 또는 파일 변경 자동 감지 기능을 켜면 됩니다.

## 예시

### `???` — 질문 생성 (기본: 자유형)

입력:
```markdown
클로저 ???
```

처리 후:
```markdown
클로저
  - 클로저가 캡처한 외부 변수가 원본과 동일한 메모리를 참조할 때, 의도치 않은 상태 변이가 발생하면 디버깅이 왜 어려워지는가?
  - 루프 안에서 클로저를 생성할 때 흔히 발생하는 "변수 공유 문제"는 설계 결함인가, 오해인가?
  - 클로저를 "가난한 자의 객체"라고 부르는 관점에서, 클래스 기반 private 필드와 어떤 트레이드오프가 있는가?
```

### `???` — 질문 생성 (`--structure`)

입력:
```markdown
클로저 ???
```

처리 후:
```markdown
클로저
  - [구분] 클로저는 일반 함수, 콜백, 람다 표현식과 어떻게 다른가?
  - [구조] 어휘적 환경 캡처, 자유 변수 바인딩, 스코프 체인 유지는 어떤 순서로 작동하는가?
  - [관계] 가비지 컬렉션, 스코프 규칙, 일급 함수 지원에 각각 어떻게 의존하는가?
```

### `!!!` — 답변 생성

입력:
```markdown
모나드란 무엇인가 !!!
```

처리 후:
```markdown
모나드란 무엇인가
  - 값을 감싸는 컨테이너로, unit과 bind 두 연산을 제공하는 구조
  - bind(flatMap)으로 중첩 없이 연산을 플랫하게 체이닝
  - Promise, Optional, Result 등이 대표적 예시
```

### 멀티 프로바이더

```bash
aq run file.md                  # Claude (기본)
aq --model gemini run file.md   # Gemini
aq --model codex run file.md    # Codex
```

## 동작 원리

1. 파일 내 `???`/`!!!` 마커를 정규식으로 스캔
2. 마커 주변 컨텍스트 (헤딩, 전후 텍스트) 추출
3. AI CLI 호출하여 결과 생성
4. **아래→위 순서**로 처리 (라인 번호 보존)
5. 마커 제거 + 결과를 들여쓰기로 삽입
6. 파일 덮어쓰기 → 에디터 autoread 반영
