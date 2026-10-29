import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

# 1. 환경변수 및 경로 설정
load_dotenv()
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'db', 'vector_data.json')

# 2. 웹 페이지 기본 설정
st.set_page_config(page_title="근로복지공단 규정 챗봇", page_icon="🤖")
st.title("🤖 근로복지공단 규정 AI 챗봇")
st.caption("수집된 최신 규정(민원 처리, 체불청산, 가족수당)을 바탕으로 답변합니다.")

# 3. AI 및 지식창고 불러오기 (캐싱으로 속도 최적화)
@st.cache_resource
def load_ai_system():
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    vectorstore = InMemoryVectorStore.load(DB_PATH, embeddings)
    llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0)
    return vectorstore, llm

try:
    vectorstore, llm = load_ai_system()
    
    # 채팅 기록 보관함 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 이전 채팅 내용 화면에 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자가 질문을 입력하면 작동하는 부분
    if user_input := st.chat_input("규정에 대해 무엇이든 질문해 보세요!"):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # AI가 DB를 직접 검색해서 답변하는 부분
        with st.chat_message("assistant"):
            with st.spinner("관련 규정을 꼼꼼히 찾고 있습니다..."):
                docs = vectorstore.similarity_search(user_input, k=3)
                context = "\n\n".join([doc.page_content for doc in docs])
                
                prompt = f"""당신은 근로복지공단 규정 안내 전문가입니다. 반드시 아래 제공된 [문맥]을 바탕으로 질문에 친절하고 정확하게 답변하세요. [문맥]에 없는 내용은 지어내지 말고 '제공된 규정에서는 해당 내용을 찾을 수 없습니다'라고 답변하세요.

[문맥]:
{context}

[질문]:
{user_input}"""
                
                response = llm.invoke(prompt)
                
                # 💡 AI 응답을 깔끔한 텍스트 문자열로 안전하게 추출
                raw_content = response.content
                if isinstance(raw_content, list):
                    answer = "".join([item.get('text', '') if isinstance(item, dict) else str(item) for item in raw_content])
                else:
                    answer = str(raw_content)
                    
                st.markdown(answer)
                
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
except Exception as e:
    st.error(f"시스템 오류가 발생했습니다. 에러 내용: {e}")