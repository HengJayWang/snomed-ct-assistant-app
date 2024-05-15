import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# configure sqlite3
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

st.set_page_config(layout="wide")

remote = True

if remote:
    with st.sidebar:
        if 'OPENAI_API_TOKEN' in st.secrets:
            st.success('API key already provided!', icon='✅')
            openai_api_key = st.secrets['OPENAI_API_TOKEN']
else:
    load_dotenv()
    openai_api_key = os.environ.get("OpenAI_API_KEY")

st.title("🏥 SNOMED-CT Assistant")
st.caption("👩‍⚕️ A smart medical assistant with SNOMED-CT knowledge.")

# System prompt
system_prompt = """You are a medical expert with rich experience in SNOMED-CT professional knowledge. 
You are skilled at assisting medical professionals and answering questions in the medical field. You are patient, helpful and professional.
Please refuse to answer inquiries and requests unrelated to the medical field, in order to maintain professionalism in medicine. 
As an experienced professional, you possess deep expertise in the field of SNOMED CT Entity Linking. 
You have a thorough understanding of the relevant workflows and critical aspects involved, encompassing:
- Processing electronic medical records (EHRs), Adept handling of electronic medical record (EMR) data processing
- Entity Identification, Proficient entity recognition capabilities, identifying and extracting relevant medical concepts from unstructured text
- Skilled Entity Mapping, accurately linking identified entities to their corresponding SNOMED CT concepts
- Seamless integration and output of clinical terminology, ensuring the accurate representation and utilization of standardized medical language
Here is the practical entity linking process example:
- the input text in EHRs: "Patient referred for a biopsy to investigate potential swelling in upper larynx."
- the identified entity: "biopsy", "larynx"
- the mapped SNOMED CT concepts id & descriptions: "274317003 | Laryngoscopic biopsy larynx (procedure)", "4596009 | Laryngeal structure (body structure)"
Your comprehensive knowledge and mastery of these key components make you an invaluable asset in the realm of biomedical natural language processing and knowledge extraction. 
With your specialized expertise, you are able to navigate the complexities of SNOMED CT Entity Linking with ease, delivering accurate and reliable results that support various healthcare and research applications.
When answering questions, always respond in traditional Chinese (zh-TW). 
If there are any SNOMED-CT related medical professional terms, please provide the original text in parentheses afterwards."""

# Test Prompt Example
test_prompt = """請協助我做 EHR 的 SNOMED CT Entity Linking 的處理， 這是原本的病歷文字: 
"Patient referred for a biopsy to investigate potential swelling in upper larynx."
，首先做 Entity Identification，列出醫學相關術語片段，接著做 Entity Mapping，將對應的 SNOMED CT 術語列出。
輸出格式用表格，欄位是 "identified entity", "SNOMED CT concept ids", "SNOMED CT descriptions"。"""

client = OpenAI(api_key=openai_api_key)
model_tag = "gpt-3.5-turbo"

def chat_input(prompt):
    # with st.sidebar:
    #     st.write("You are talking with: ", model_tag)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model=model_tag, messages=st.session_state.messages)
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": system_prompt},
                                    {"role": "assistant", "content": "👩‍⚕️ 您好，我是您的專業醫學助理。請問有任何我可以協助你的地方嗎?"}]

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    chat_input(prompt)
    # st.session_state.messages.append({"role": "user", "content": prompt})
    # st.chat_message("user").write(prompt)
    # with st.spinner("Thinking..."):
    #     response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    #     msg = response.choices[0].message.content
    #     st.session_state.messages.append({"role": "assistant", "content": msg})
    #     st.chat_message("assistant").write(msg)

if st.sidebar.button("Example input",type="primary"):
    chat_input(test_prompt)
    
# model_tag = st.sidebar.selectbox(
#     "Which model do you want to chat with?",
#     ("gpt-4o", "gpt-3.5-turbo")
# )