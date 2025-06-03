# API 키 불러오기 위한 작업
from dotenv import dotenv_values
import os

env = dotenv_values()
api_key = env.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError(
        "Google API key is missing. Set GOOGLE_API_KEY in your environment or .env file."
    )

# LLM 모델 셋업
from langchain.chat_models import init_chat_model

model = init_chat_model(
    model="gemini-2.0-flash",
    model_provider="google_genai",
    api_key=api_key,
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
