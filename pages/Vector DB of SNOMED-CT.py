from timeit import default_timer as timer

import streamlit as st
import chromadb
import pandas as pd
import numpy as np

# configure sqlite3
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

st.set_page_config(layout="wide")

# App Title
st.title("📚 Semantic Search with Vector Database of SNOMED-CT 💡")
st.caption("🔍 Search any SNOMED-CT relate decription & concept with natural language.")
st.sidebar.title("🔍 Search Setting")
query_number = st.sidebar.slider("Query Numbers", 5, 30, 10)
st.markdown("##### ➡️⌨️ Please input some medical description here, e.g. \"insomnia two nights a week.\", \"COPD\", \"Degenerative Joint Disease\"")
query_text = st.text_input("Input: any medical description snippet","Type-2 Diabetes")

# Chroma DB Client
chroma_client = chromadb.PersistentClient(path="snomed_ct_id_term_500k")
collection = chroma_client.get_or_create_collection(name="snomed_ct_id_term")
start = 1.0
end = 1.1
st.markdown("##### ➡️Chroma DB will return " + str(query_number)  
            + " related instances from " + str(collection.count()) + " collections.")
st.warning("Due to the SQLite [file size limit on GitHub](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage), this testing only query from 500k SNOMED-CT instances.", icon="🚨")


# Func: query chrome_db
def query_chroma_db(query_text, query_number):
    results = collection.query(
        query_texts=[query_text],
        n_results=query_number,
        include=["distances", "metadatas", "documents"]
    )
    return results

# Func: chrome_db_result to df
def get_df_from_chroma_results(results):
    result_dict = {'ids': results['ids'][0], 'concept_ids': [ str(sub['concept_id']) for sub in results['metadatas'][0] ], 'distances': results['distances'][0], 'documents': results['documents'][0]}
    df = pd.DataFrame(result_dict)
    return df

start = timer()
results = query_chroma_db(query_text, query_number)
end = timer()
st.markdown("###### ➡️ Query Time : {: .6f} seconds.".format(end - start))
st.divider()

results_df = get_df_from_chroma_results(results)

#displaying the dataframe as an interactive object
st.markdown("### 📊 Similar Search Results from Chroma Vector DB")
st.dataframe(results_df, 1000, 500)

