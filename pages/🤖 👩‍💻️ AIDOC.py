#AIDOC - Artificial Intelligence Document Organizer and Classifier
#SAVETIME: Smart AI Vectors for Efficient Time Optimization during Monitoring and Evaluation
#REORDER: Robust AI Engine for Document Organization and Efficient Reordering

import streamlit as st
import pandas as pd
from utils import my_authenticator
from aidoc.MWE import mwe_neural
from zipfile import ZipFile

def reset_aidoc_session():
    st.session_state.reset_aidoc=True
    st.session_state.goldcol=None
    st.session_state.goldvar = None
    st.session_state.refcol = None
    st.session_state.mydf=None
    st.session_state.indf = None
    st.session_state.neural=None
    st.session_state.initialised=False
    st.session_state.lastcol=""

my_authenticator()

def reorder_me():
    st.session_state.mydf.sort_index(inplace=True)
    if st.session_state.neural==None:
        st.session_state.neural=mwe_neural()
    if st.session_state.lastcol != st.session_state.refcol:
        print("changed goldcol")
        st.session_state.neural.embed()
        st.session_state.neural.calc_matrix()
    all_sims= st.session_state.neural.calculate_similarity()
    st.session_state.mydf["Similarity"]=all_sims
    st.session_state.mydf.sort_values("Similarity", ascending=False, inplace=True)
    st.session_state.lastcol =st.session_state.refcol
    st.session_state.mydf

if st.session_state["authentication_status"]:
    if not "reset_aidoc" in st.session_state:
        reset_aidoc_session()

    st.markdown('''# 🤖 👩‍💻️  :rainbow[AIDOC]: :rainbow[A]rtificial :rainbow[I]ntelligence :rainbow[D]ocument :rainbow[O]rganiser and :rainbow[C]lassifier''')

    st.write('&nbsp;')#empty line
    st.write("## Step 1: Upload a CSV file")

    uploaded_file = st.file_uploader("Upload CSV file containing records to screen, at least 3 relevant references should be labelled already.")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except:


            import ast
            import pickle

            input_zip = ZipFile(uploaded_file)
            #x= {name: input_zip.read(name) for name in input_zip.namelist()}
            x=input_zip.read(input_zip.namelist()[0])

            df = pickle.loads(x)


            #df = pd.read_pickle(x)

        st.write("Successfully uploaded a file with {} records.".format(len(df.index)))
        st.markdown("## Step 2: tell AIDOC about the data you wish to prioritize")
        cols=list(df.columns)
        #st.write("Select the column that contains previous screening results")
        st.session_state.goldcol=st.selectbox("Select the column that contains data of interest",index=None,options=cols,placeholder="Click to view options")
        if st.session_state.goldcol != None:
            st.write("Data are located in column: {}".format(st.session_state.goldcol))
            goldoptions=list(set(df[st.session_state.goldcol]))
            st.session_state.goldvar = st.selectbox("Select the variable that indicates an interesting record in {}".format(st.session_state.goldcol),index=None,options=goldoptions, placeholder="Click to view options")
            print("---mainfunc------")
            print(st.session_state.goldvar)
            if st.session_state.goldvar != None:
                # if "Include AIDOC" not in df.columns:
                #     df["Include AIDOC"] = False
                # if 'Exclude AIDOC' not in df.columns:
                #     df["Exclude AIDOC"] = False
                #df.loc[df[st.session_state.goldcol] == st.session_state.goldvar, "Include AIDOC"] = True
                first_column = df.pop(st.session_state.goldcol)
                df.insert(0, st.session_state.goldcol, first_column)
                # second_column = df.pop("Exclude AIDOC")
                # df.insert(1, "Exclude AIDOC", second_column)


                st.write("The AI will use rows marked with '{}' in column '{}' to re-order references".format(
                    st.session_state.goldcol, st.session_state.goldvar))

                st.session_state.refcol = st.selectbox(
                    "Select the column that contains context that will be processed by the AI, for example the document title", index=None,
                    options=cols, placeholder="Click to view options")

                if st.session_state.refcol != None:
                    st.write("The AI will work on input text from column: {}".format(st.session_state.refcol))







                    popping=[df.pop(c) for c in df if "Unnamed:" in c]

                    if not st.session_state.initialised:
                        st.session_state.mydf =df

                        st.session_state.initialised=True


    if st.session_state.initialised:
        if st.button("Reorder now!"):
            reorder_me()




