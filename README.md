# 🚀 LangChain PRO-Mode Demo with Google Gemini 2.0 Flash

[![Google AI Studio](https://img.shields.io/badge/Google%20AI%20Studio-Gemini%202.0%20Flash-blueviolet)](https://ai.google.dev/)
[![LangChain](https://img.shields.io/badge/LangChain-Framework-brightgreen)](https://python.langchain.com/)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)

> LangChain과 Google의 **Gemini 2.0 Flash** 모델을 활용하여,  
> 여러 단계를 거쳐 최적의 결과물을 생성하는 "PRO-Mode" 예시입니다.  
> 번역 → 초기 응답 → 개선 → 재번역의 순차적인 과정을 통해,  
> LLM이 가장 적합한 답변을 단계적으로 만들어냅니다.

## ✨ 소개 (Introduction)

- **PRO-Mode란?**
    - 단순한 단일 호출이 아닌, 여러 차례의 재귀적(Recurrent) 호출을 통해 응답을 점진적으로 개선(Refine)하는 방식입니다.
    - 이 프로젝트에서는 Time Tracking, 사용자 입력의 자연스러운 번역/재번역, 응답 결과의 반복적 개선 기법 등을 시연합니다.

- **사용된 기술 스택**
    1.  **LangChain**: LLM 호출 및 체인 구성을 위한 파이썬 라이브러리
    2.  **Google Generative AI**: Gemini 2.0 Flash 모델 API (파이썬 wrapper: `langchain-google-genai`)
    3.  **Python-dotenv**: `.env` 파일에서 API 키를 안전하게 로드
    4.  **Miniconda** (또는 Anaconda): 파이썬 가상 환경 관리

## 🌟 주요 기능 (Features)

1.  **언어 자동 번역**
    -   사용자 프롬프트를 LLM 친화적인 언어(영어)로 번역
    -   최종 결과물을 다시 사용자 모국어로 재번역

2.  **다단계 프로세스**
    -   **번역 페이즈** → **최초 응답 페이즈** → **개선 페이즈**(반복) → **사용자 언어 응답 페이즈**
    -   최대 5~10회 혹은 그 이상의 재귀 개선 요청 가능

3.  **시간 추적 (Thinking 표시)**
    -   `Thread`와 `Event`를 활용하여 모델이 생각하는 시간을 실시간으로 터미널에 표기
    -   사용자에게 마치 대형 추론형 모델이 오랜 시간 동안 생각하는 듯한 인터랙션 제공

## 🛠️ 설치 및 준비 (Installation)

아래 예시 환경은 Python 3.12 기준입니다.  다른 버전이어도 `langchain` 호환성만 맞다면 대부분 정상 작동합니다.

1.  **Miniconda/Anaconda 설치**
    -   [Anaconda.com/download](https://www.anaconda.com/download/)에서 직접 설치
    -   혹은 기존에 `conda`가 설치되어 있다면 이 단계 생략

2.  **가상 환경 생성 및 활성화**

    ```bash
    conda create --name my_pro python=3.12 pip
    conda activate my_pro
    ```

3.  **필수 라이브러리 설치**

    ```bash
    pip install python-dotenv
    pip install langchain
    # Gemini API 사용 시
    pip install "langchain-google-genai"
    # 추가로 OpenAI/Anthropic/등을 사용한다면
    pip install "langchain-openai"
    pip install "langchain-anthropic"
    ```

4.  **`.env` 파일 설정**
    -   루트 디렉토리에 `.env` 파일 생성 후 아래와 같이 API 키를 입력

        ```
        GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
        ```

    -   Google Cloud Generative AI (Gemini) 키가 없는 경우, [AI Studio](https://makersuite.google.com/app/apikey) 등을 통해 발급받으세요.

## 🚀 사용 방법 (Usage)

1.  이 레포를 클론 혹은 코드를 복사 후, `main.py` (파일명 자유) 생성
2.  아래 예시 코드를 붙여넣고 `.env`가 준비된 상태에서 실행

    ```python
    # main.py

    # API 키 불러오기 위한 작업
    from dotenv import dotenv_values

    env = dotenv_values()

    # LLM 모델 셋업
    from langchain.chat_models import init_chat_model

    model = init_chat_model(
        model="gemini-2.0-flash",
        model_provider="google_genai",
        api_key=env["GOOGLE_API_KEY"],
    )


    # 시간 측정 위한 작업
    from time import time, sleep
    import sys
    from threading import Thread, Event

    stop_time = Event()


    def show_time():
        start = time()
        while not stop_time.is_set():
            sys.stdout.write(f"\rThinking... {time() - start:.2f}s")
            sys.stdout.flush()
            sleep(0.1)


    # 번역 프롬프트
    def prompt_translate(prompt, target_language):
        return f"""
        Accurately translate the following text into natural {target_language}.
        ```
        {prompt}
        ```
        Output only the perfectly translated text.
        """


    # 모델 언어
    llm_language = "American English"
    # 사용자 언어
    user_language = "Korean"

    # 사용자 입력
    request = input("User: ")

    # 시간 측정 스레드 시작
    Thread(target=show_time, daemon=True).start()

    # 1. 번역 페이즈
    response = model.invoke(prompt_translate(request, llm_language)).content
    print(f'\nHmm.. The user said, "{response}"')

    # 2. 최초 응답 페이즈
    response = model.invoke(request).content

    # 3. 개선 페이즈
    for i in range(5):
        response = model.invoke(
            f"""
            request:
            ```
            {request}
            ```
            response:
            ```
            {response}
            ```
            Refine the response to perfectly match the request.
            Output only the plaintext response.
            Ask nothing; independently make all choices and output only the final result.
            Do not explain any refinements.
            """
        ).content

    # 4. 사용자 언어 응답 페이즈
    print(f"\nRespond in the user's native language. '{user_language}'")
    response = model.invoke(prompt_translate(response, user_language)).content
    stop_time.set()

    # 5. 최종 응답 페이즈
    print(f"\nAI: {response}")


    ```

3.  **실행**

    ```bash
    python main.py
    ```

4.  **프로그램 동작**
    -   터미널에 `User:`라고 뜨면, 원하는 질문이나 요청을 입력
    -   모델이 `Thinking…` 상태로 시간 경과를 표시하며 응답 준비
    -   영어 번역 → 초기 응답 생성 → 5회 개선 → 최종적으로 한국어(사용자 언어)로 변환
    -   최종 결과물을 `AI: ...` 형식으로 출력

## ❓ FAQ / 자주 묻는 질문

1.  **오류 발생 시**
    -   `.env` 파일이 정상적으로 로드되는지 확인 (`print(env)` 등으로 디버깅)
    -   `conda` 환경이 적절히 활성화되어 있는지 재확인
    -   패키지 버전 충돌 시 `pip install --upgrade <package_name>`로 업데이트
2.  **추가 모델 사용**
    -   Anthropic Claude, OpenAI GPT 시리즈 등은 각각 API 키를 발급받아야 합니다.
    -   `langchain-openai`, `langchain-anthropic` 등을 추가 설치 후, 비슷한 방식으로 사용 가능합니다.
    -   `main.py`에서 `ChatGoogleGenerativeAI` 부분을 해당 모델에 맞게 수정해야합니다. (예: `ChatOpenAI`, `ChatAnthropic`)
3.  **재귀(Refine) 횟수 조정**
    -   `for i in range(5):` 부분의 숫자를 원하는 만큼 늘리거나 줄일 수 있습니다.
    -   단, 너무 많이 늘리면 API 비용과 시간이 증가하니 주의하세요.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (optional: 라이선스 파일을 추가할 경우).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. (optional: 기여 관련 내용을 추가할 경우)