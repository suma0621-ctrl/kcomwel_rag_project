import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def load_and_split_documents():
    print("📄 저장된 규정 텍스트를 AI가 읽기 좋게 나누는 작업을 시작합니다...")
    
    documents = []
    
    # 1. data 폴더에 있는 모든 txt 파일을 읽어오기
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            file_path = os.path.join(DATA_DIR, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 파일명을 메타데이터(출처)로 저장 (나중에 AI가 답변할 때 근거로 제시함)
                doc = Document(page_content=content, metadata={"source": filename})
                documents.append(doc)
    
    print(f"✅ 총 {len(documents)}개의 문서를 불러왔습니다.")
    
    # 2. 텍스트 분할기 설정
    # 의미가 끊기지 않게 500자 단위로 자르고, 앞뒤 문맥 유지를 위해 50자씩 겹치게(overlap) 설정
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,       
        chunk_overlap=50,     
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    # 3. 분할 실행
    split_docs = text_splitter.split_documents(documents)
    print(f"✂️ 텍스트 분할 완료: 원본 문서들이 총 {len(split_docs)}개의 조각(Chunk)으로 나뉘었습니다.")
    
    # 테스트용으로 첫 번째 조각 살짝 보여주기
    if split_docs:
        print("\n[미리보기: 첫 번째 조각]")
        print(f"  - 출처: {split_docs[0].metadata['source']}")
        print(f"  - 내용: {split_docs[0].page_content[:150]}...\n")
        
    return split_docs

if __name__ == "__main__":
    load_and_split_documents()