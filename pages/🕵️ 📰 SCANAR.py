import streamlit as st
import pandas as pd
from utils import my_authenticator
from io import StringIO
from streamlit.components.v1 import html
from datetime import datetime,date
from scanar_utils import scanar_retrieval

if "querylist" not in st.session_state:
    st.session_state["querylist"]=None

if "all_res" not in st.session_state:
    st.session_state["all_res"]=pd.DataFrame()

if "all_searchdoc" not in st.session_state:
    st.session_state["all_searchdoc"]=pd.DataFrame()

def get_queries():
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    # To read file as string:
    string_data = stringio.read()

    st.markdown("**Here are your queries:**")

    st.session_state.queries = []

    mytext = ""
    for d in string_data.split("\n"):
        qry=d.strip()
        if len(qry)>0:
            mytext = mytext + d + '<br>'
            st.session_state.queries.append(qry)

    html(mytext, height=150, scrolling=True)

def get_parameters():
    st.write("## Step 2: Adjust your search and outputs")

    dt = datetime.now()  # per default, the news will be retrieved from a timeframe srarting 1 year ago.
    st.session_state.dt=dt
    oneyr = dt.replace(year=dt.year - 1)
    twoyr = dt.replace(year=dt.year - 2)

    if dt.month > 6:
        sixmo = dt.replace(month=dt.month - 6)
    else:
        sixmo = dt.replace(year=dt.year - 1)
        left = 6 - sixmo.month
        sixmo = sixmo.replace(month=12 - left)

    dat = date(dt.year, dt.month, dt.day)
    # results = gnf.query(myquery, after=dat)
    st.write('&nbsp;')  # empty line
    st.session_state.timeframe = st.radio(
        "**Retrieve articles published/updated between now and which start date?**",
        ["6 Months ago", ":rainbow[1 year ago]", "2 years ago"], index=1,
        captions=[sixmo.strftime('%d/%m/%Y')+ " to " + dt.strftime('%d/%m/%Y'), oneyr.strftime('%d/%m/%Y')+ " to " + dt.strftime('%d/%m/%Y'), twoyr.strftime('%d/%m/%Y')+ " to " + dt.strftime('%d/%m/%Y')])
    if st.session_state.timeframe == "6 Months ago":
        st.session_state.dates=sixmo
    elif st.session_state.timeframe == "2 years ago":
        st.session_state.dates = twoyr
    else:
        st.session_state.dates = oneyr
    st.write('&nbsp;')  # empty line
    st.session_state.fulltexts = st.radio(
        "**Scrape full text for all articles?**",
        [":rainbow[Yes]", "No"], index=0)
    st.write('&nbsp;')  # empty line
    st.session_state.num_ret = st.slider("**How many articles should be retrieved per query?**", 1, 100, 50)

def ris_converter():
    ############################variables
    atype = 'NEWS'  # they type of reference which is the first bit of metadata in our RIS file for each entry, ususally type is 'JOUR' for journal articles, but here we are choosing news
    date_downloaded = st.session_state.dt.strftime('%d/%m/%Y')  # the day on which the news were retrieved/scraped (for 'last accessed' info that will be part of the citation)
    # path = r'C:\Users\c1049033\PycharmProjects\NewsAPI\data\output_documentation_20240603-103141.csv'  # path to the scraped news csv file
    # fileout = r'C:\Users\c1049033\PycharmProjects\NewsAPI\ris\quantum_citations_{}.ris'.format(
    #     atype)  # the path where to save the new RIS file
    entries = []  # list to store our entries for the RIS file
    #####################################

    ############################################Match data from df with the correct RIS tag and save as list of dicts, where each dict represents one news article and its metadata


    for i, row in st.session_state.all_res.iterrows():  # iterate the news article. Here, each row in the df represents one news article
        pdat = str(row["date"]).split(" ")[0]  # get whole date of publication of this article
        # print(pdat)
        splitdat = pdat.split("-")
        pyr = splitdat[0]  # get year string from date
        pmon = splitdat[1]
        pday = splitdat[2]
        ref = {'TY': atype,
               'id': i,
               'TI': row["title"],  # title of the news article
               "T2": row["media"],  # the newspaper or source publishing this article
               "AU": row["media"].replace(",", " ").replace("  ", " ").strip()+",",  # the newspaper or source publishing this article
               # 'AB': row["description"],#potentially the scraped text could be added as abstract, but I decided to keep it slim for now because the abstract won't appear in the citation.
               "PY": pyr,  # year of publication of the article
               "UR": row["link"],
               # the link to the news article. my news api sometimes appends some crappy appendix to the URL, thus the splitting function.
               "Y2": date_downloaded,  # last accessed info
               "N1": "Last accessed: {}; date article published: {}/{}/{}".format(date_downloaded, pday, pmon, pyr)
               # last accessed info in natural language
               }
        entries.append(ref)

    ####################################################################create RIS output
    # print(entries)
    ris_str = ""  # we will make one large string with all the info and then write that to a file
    for e in entries:  # for each news article
        for key, line in e.items():
            ris_str = ris_str + key + "  - " + str(line) + "\n"  # add metadata as new line
        ris_str = ris_str + "ER  - \n\n"  # finish off the entry with the ER tag
    st.session_state.ris=ris_str
    #####################################################################write to file


def get_news_data():
    st.write("## Step 3: Submit the queries")

    if st.button("Submit queries"):
        scanar_retrieval()

    if len(st.session_state.all_res.index) > 0 and len(st.session_state.all_searchdoc) > 0:
        st.write("## Step 4: View and download results")
        ris_converter()
        fn="scanar_{}_citations_{}.ris".format(len(st.session_state.all_res.index),st.session_state.dt.strftime('%d_%m_%Y'))
        st.download_button('Download RIS for EndNote', st.session_state.ris,file_name=fn)

        st.dataframe(st.session_state.all_res)
        st.dataframe(st.session_state.all_searchdoc)

my_authenticator()
if st.session_state["authentication_status"]:
    st.markdown('''# 🕵️ 📰  :rainbow[SCANAR]: :rainbow[S]earch :rainbow[C]ompanion for :rainbow[A]dvanced :rainbow[N]ews :rainbow[A]rticle :rainbow[R]etrieval''')

    st.write('&nbsp;')#empty line
    st.write("## Step 1: Upload a text file")
    st.write("Note: Each new line in the text file is a new search query. No headers needed.")
    uploaded_file = st.file_uploader("Upload text file")

    if uploaded_file is not None:
        get_queries()
        get_parameters()
        get_news_data()

    #
    st.write('&nbsp;')  # empty line
    st.video("https://youtu.be/5INnu6h8iI0")
    st.markdown("## Description of the methods")
    st.write("As described in the MedTech Horizon Scanning Methods Handbook")
    st.write("News are a routine source for weak signal detection for the different types of scans that the Innovation Observatory undertakes. Google News is a news aggregator service by Google – said to be the world’s largest, covering articles in 35 languages and > 50,000 news sources from > 20,000 publishers [1]. Their sources include general and topic-specific news sites, as well as press releases from industry and universities. Google and Google news are the biggest single driver of traffic to top news sites [2]. Robust news searching using the current Google news interface is precluded. Manually entering search strings on the Google News website, specifying timeframes, and then copy-pasting relevant results is time-consuming. This means only the first few pages of results can be processed and that there is no documentation of the search process and the number of hits. The manual process may also have limited reproducibility, as different people may obtain different results due to varying speed and covering more/less results.")

    st.write("The Innovation Observatory’s custom built SCANAR (Search Companion for Advanced News Article Retrieval) tool has a large potential for time-saving during scans by eliminating the need for manual retrieval of news articles. It also improves reproducibility and transparency of the process by providing a detailed search documentation. The tool’s strengths are that it accepts multiple search queries as input, thus encouraging comprehensive and systematic searching. It downloads full texts of articles, de-duplicates results, and provides an automatic unsupervised ranking that orders articles to the top that were relevant to most input queries. It provides three outputs: ")

    st.write("A spreadsheet with all ranked news articles, including titles, full texts, news source, time of publication. ")

    st.write("A search documentation spreadsheet that indicates how many search results were produced by each query, how many articles were retrieved, and how many duplicate articles appeared between queries.")

    st.write("A bibliographic citation file in RIS (Research Information Systems) format that includes all article metadata ready for import into a reference manager software such as EndNote. This leads to downstream time-savings as it enables colleagues who write up reports to easily cite relevant news articles.  ")
    st.write("[1] https://en.wikipedia.org/wiki/Google_News")
    st.write("[2] https://www.pewresearch.org/wp-content/uploads/sites/8/legacy/nielsen-study-copy.pdf")


