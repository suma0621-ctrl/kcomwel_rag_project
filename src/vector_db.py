import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

from document_parser import load_and_split_documents

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, 'db')
os.makedirs(DB_DIR, exist_ok=True) 

def create_vector_db():
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ [오류] .env 파일에 GOOGLE_API_KEY가 입력되지 않았습니다.")
        return

    print("🧠 Gemini 최신 통합 임베딩 모델(gemini-embedding-001)을 준비 중입니다...")
    # 💡 단종된 구형 모델 대신, 현재 서비스 중인 최신 통합 모델로 이름 변경!
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001") 

    docs = load_and_split_documents()
    
    if not docs:
        print("❌ 저장된 문서 조각이 없습니다. 데이터를 확인해주세요.")
        return

    print(f"\n📦 총 {len(docs)}개의 조각을 에러 없는 내장 벡터 DB로 변환하여 저장합니다...")
    print("   (구글 서버와 통신하므로 몇 초 정도 걸릴 수 있습니다.)")
    
    vectorstore = InMemoryVectorStore.from_documents(documents=docs, embedding=embeddings)
    
    db_path = os.path.join(DB_DIR, "vector_data.json")
    vectorstore.dump(db_path)
    
    print(f"\n✅ 벡터 데이터베이스가 성공적으로 구축되었습니다!")
    print(f"📁 확인해 보세요: 왼쪽 'db' 폴더 안에 'vector_data.json' 파일이 생성되었습니다.")
    return vectorstore

if __name__ == "__main__":
    create_vector_db()