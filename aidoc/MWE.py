import streamlit as st
from tqdm import tqdm
from random import sample
import numpy as np
from sentence_transformers import util, SentenceTransformer

class mwe_neural():
    def __init__(self):
        self.model_name = 'sentence-transformers/allenai-specter'
        self.model = SentenceTransformer(self.model_name)

    def embed(self, ):

        if st.session_state.refcol != None:
            try:
                dat = st.session_state.mydf[st.session_state.refcol]
                print("!!!!!!!!!Creating embeddings")
                self.emb_source = self.model.encode(list(dat))  # get our data column
            except:
                self.emb_source = [np.array(e) for e in st.session_state.mydf[st.session_state.refcol]]

                print("!!!!!!!!!Attempting to use existing embedding, model is not initialised.")

    def calc_matrix(self, ):

        self.cos_sim = util.pytorch_cos_sim(self.emb_source, self.emb_source)  # .diagonal().tolist()#all similarities

    def calculate_similarity(self, pos_idx=None):
        """
        pos_idx: list with lindex calues of positively-labelled rows

        returns: list of length of the df used for screening, with float values between 0 and 1 corresponding to cosine similarity (1=similar).

        Example:
        pos_idx=[0,2,4]


        """

        if pos_idx == None:
            pos_idx = []
            for i, row in st.session_state.mydf.iterrows():
                if row[st.session_state.goldcol] == st.session_state.goldvar:
                    pos_idx.append(i)
        if len(pos_idx) > 10:
            pos_idx = sample(pos_idx, 10)
        print(pos_idx)
        print("----calcsim-----")
        print(st.session_state.goldvar)

        all_sims = []

        for i in tqdm(self.cos_sim):  # for each input and its pairwise similarities
            avg_for_record = []  # list to store all pairwwise similarities of this field with the positively labelled fields
            for ind in pos_idx:  # for each positive labelled record
                avg_for_record.append(i[ind].item())  # add the cosine similarity
                # print(i[ind])
            try:
                all_sims.append(sum(avg_for_record) / len(
                    avg_for_record))  # average similarity is used for now, but could use median etc
            except:
                all_sims.append(0)
            # print(sum(avg_for_record)/len(avg_for_record))
            # print("-----")
        # print(all_sims)
        return all_sims