# pip install langchain llama-index openai chromadb numpy pandas django langchain-community

import os
from langchain.chains import create_retrieval_chain
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub

# os.environ["OPENAI_API_KEY"] = ""

# 1. Load Data
def load_plant_data():
    # Load plant-specific knowledge from a file or database
    loader = TextLoader("plant_health_data.txt")
    documents = loader.load()
    return documents

# 2. Set Up Vector Store
def create_vector_store(documents):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(texts, embeddings)
    return vectorstore

# 3. Build RAG Pipeline
def create_rag_pipeline(): # reference: https://api.python.langchain.com/en/latest/chains/langchain.chains.retrieval.create_retrieval_chain.html
    documents = load_plant_data()
    vectorstore = create_vector_store(documents)
    retriever = vectorstore.as_retriever()
    llm = ChatOpenAI(temperature=0.7, model_name="gpt-4")
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    combine_docs_chain = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)
    rag_pipeline = create_retrieval_chain(retriever=retriever, combine_docs_chain=combine_docs_chain)
    return rag_pipeline

# 4. Query with Sensor Data
def query_with_sensor_data(user_query, sensor_data):
    rag_pipeline = create_rag_pipeline()

    sensor_info = (
        f"Current sensor readings: "
        f"Temperature: {sensor_data.get('temperature', 'N/A')}°C, "
        f"Humidity: {sensor_data.get('humidity', 'N/A')}%, "
        f"Soil Moisture: {sensor_data.get('soil_moisture', 'N/A')}%, "
        f"Light Intensity: {sensor_data.get('light_intensity', 'N/A')}."
    )

    full_query = f"{user_query}\n\n{sensor_info}"

    response = rag_pipeline.invoke({"input": full_query})
    return response

if __name__ == "__main__":
    query = ""
    test_data = {
        "temperature": 22,
        "humidity": 40,
        "soil_moisture": 20,
        "light_intensity": 500
    }
    print(query_with_sensor_data(query, test_data))