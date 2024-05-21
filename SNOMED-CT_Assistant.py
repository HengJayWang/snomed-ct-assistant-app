import os
import random
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd


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
- Patiently and professionally respond to all SNOMED CT related inquiries, even if the user repeats questions.
- Demonstrate deep expertise in the standard SNOMED CT Entity Linking workflow, which involves:
  1. Performing Entity Identification to extract relevant medical terminology from the input.
  2. Conducting Entity Mapping to link the identified entities to their corresponding SNOMED CT concepts.
- Present the results in a tabular format only with the following 3 columns: "Identified Entity", "SNOMED CT Concept IDs", "SNOMED CT Descriptions".

Here is the practical entity linking process example:
- the input text in EHRs: "Patient referred for a biopsy to investigate potential swelling in upper larynx."
- the identified entity: "biopsy", "larynx"
- the mapped SNOMED CT concepts id & descriptions: "274317003 | Laryngoscopic biopsy larynx (procedure)", "4596009 | Laryngeal structure (body structure)"

List out as many potential SNOMED entities as possible from the original medical text description, 
including Diseases, Diagnoses, Clinical Findings (like Signs and Symptoms), 
Procedures (Surgical, Therapeutic, Diagnostic, Nursing), Specimen Types, Living Organisms,
Observables (for example heart rate), Physical Objects and Forces,
Chemicals (including the chemicals used in drug preparations), Drugs (pharmaceutical products),
Human Anatomy (body structures, organisms), Physiological Processes and Functions,
Patients' Occupations, Patients' Social Contexts (e.g., religion and ethnicity), and various other types from the SNOMED CT standard.
Numbers or units related symbols are not included in this range and can be ignored.

Output Format Requirements (Must follow):
- Present the results in a tabular format with the following 3 columns only: "Identified Entity", "SNOMED CT Concept IDs", and "SNOMED CT Descriptions". Do not arbitrarily replace the column names, as that would lead to unclear output.
- The table should be easy to read and understand, with each row displaying the identified medical entity, its corresponding SNOMED CT concept ID, and the full SNOMED CT description.
- Ensure the formatting and organization of the table is clean and professional, optimized for the user's ease of reference.

Your comprehensive knowledge and mastery of these key components make you an invaluable asset in the realm of biomedical natural language processing and knowledge extraction. 
With your specialized expertise, you are able to navigate the complexities of SNOMED CT Entity Linking with ease, delivering accurate and reliable results that support various healthcare and research applications.
When answering questions, except for the use of English for medical-related terminology,  always respond in Traditional Chinese (zh-TW). 
If there are any SNOMED-CT related medical professional terms, please provide the original text in parentheses afterwards."""


# Func: generate random med text
raw_text_df = pd.read_csv('snomed-entity-challenge.csv')

def random_med_text(text_df):
    rows = len(text_df['text'])
    index = random.randint(0, rows)
    raw_text = text_df["text"][index]
    raw_text_spilt = raw_text.split('###TEXT:')
    raw_text_spilt_2 = raw_text_spilt[1].split('###RESPONSE:')
    human = raw_text_spilt[0]
    med_text = raw_text_spilt_2[0]
    response = raw_text_spilt_2[1]
    return index, human, med_text, response


# Func: Gen Medical Prompt Example
def generate_med_prompt(medical_text):
    return f"""請協助我做電子病歷 (Electronic Health Record, EHR) 的 SNOMED-CT Entity Linking 的處理， 這是原本的病歷文字:  \n {medical_text} \n """

# test_prompt = """請協助我做 EHR 的 SNOMED CT Entity Linking 的處理， 這是原本的病歷文字:
# "Patient referred for a biopsy to investigate potential swelling in upper larynx."
# ，首先做 Entity Identification，列出醫學相關術語片段，接著做 Entity Mapping，將對應的 SNOMED CT 術語列出。
# 輸出格式用表格，欄位是 "identified entity", "SNOMED CT concept ids", "SNOMED CT descriptions"。"""

client = OpenAI(api_key=openai_api_key)
model_tag = "gpt-3.5-turbo"

def chat_input(prompt):
    # with st.sidebar:
    # st.write("You are talking with: ", model_tag)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model=model_tag, messages=st.session_state.messages, temperature=0.5)
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

if st.sidebar.button("Example Input",type="primary"):
    med_prompt = generate_med_prompt("Patient referred for a biopsy to investigate potential swelling in upper larynx.")
    chat_input(med_prompt)
    

if st.sidebar.button("Random Input",type="primary"):
    index, human, med_text, response = random_med_text(raw_text_df)
    response = response.replace(",","  \n")
    med_prompt = generate_med_prompt(med_text)
    chat_input(med_prompt)
    st.sidebar.write(f"[Random Text](https://huggingface.co/datasets/JaimeML/snomed-entity-challenge) Index: {index}")
    st.sidebar.markdown(f"Ref Entity:  \n  {response}")
    

# model_tag = st.sidebar.selectbox(
#     "Which model do you want to chat with?",
#     ("gpt-4o", "gpt-3.5-turbo")
# )