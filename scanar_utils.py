import re

from google_news_feed import GoogleNewsFeed
from gnews import GNews

from datetime import datetime,date
import base64
import pandas as pd
from tqdm import tqdm
import csv
from newspaper import Article
from newspaper import Config
import time
import streamlit as st

def alternative_fulltext(link):

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'

    config = Config()
    config.browser_user_agent = user_agent
    article = Article(link, config=config)
    article.download()
    article.html
    article.parse()
    return article.text

def get_fulltext(link,article_scraper):

    article = article_scraper.get_full_article(link)
    try:
        return article.text
    except:
        pass

    try:
        return alternative_fulltext(link)
    except:
        #print("Error with URL: {}".format(link))
        return "Please see link for full text"

def all_fulltexts(df, link_field="link", output_field="fulltext"):
    article_scraper = GNews()
    text_column=[]
    for l in tqdm(list(df[link_field])):
        text_column.append(get_fulltext(l,article_scraper))
    df[output_field]=text_column
    return df

#print(get_fulltext('https://accounts.google.com/ServiceLogin?hl=en-US&continue=https://news.google.com/rss/articles/CBMiemh0dHBzOi8vd3d3Lm1hcmt0ZWNocG9zdC5jb20vMjAyNC8wMy8zMS9tb2R1bGFyLW9wZW4tc291cmNlcy1tb2pvLXRoZS1wcm9ncmFtbWluZy1sYW5ndWFnZS10aGF0LXR1cm5zLXB5dGhvbi1pbnRvLWEtYmVhc3Qv0gF-aHR0cHM6Ly93d3cubWFya3RlY2hwb3N0LmNvbS8yMDI0LzAzLzMxL21vZHVsYXItb3Blbi1zb3VyY2VzLW1vam8tdGhlLXByb2dyYW1taW5nLWxhbmd1YWdlLXRoYXQtdHVybnMtcHl0aG9uLWludG8tYS1iZWFzdC8_YW1w?oc%3D5&gae=cb-', article_scraper))
def postprocess_link(l):
    if not l.startswith("http"):
        l=re.sub(r".+?(?=http)", "", l)
    if l.endswith("$"):
        l=l[:-1]
    return l

def decode_url(google_url):
    try:
        base64_url = google_url.split("https://news.google.com/rss/articles/")[1].split("?")[0]
    except:
        return google_url
    # print(type(base64_url))
    missing_padding = len(base64_url) % 4
    if missing_padding:
        base64_url="{}{}".format(base64_url,b'='* (4 - missing_padding))

    try:
        actual_url=base64.b64decode(base64_url)[4:].decode('utf-8', "backslashreplace").split('\\')[0]
    except:
        #print("Error with {}".format(base64_url))
        actual_url=google_url

    return postprocess_link(actual_url)

def get_feed(myquery, starter):
    """

    :param myquery:
    :param starter: the start date, as chosen by the user in the app
    :return:
    """
    gnf = GoogleNewsFeed(resolve_internal_links=True)

    dat = date(starter.year, starter.month, starter.day)
    results = gnf.query(myquery, after=dat)
   # print("retrieved results for query "+ myquery)
    return results

def feed_to_df(res):

    rows=[]
    for news_item in res:

        row={}
        row["link_original"]=news_item.link
        row["link"] = decode_url(news_item.link)
        row["description"] = news_item.description
        row["title"] = news_item.title
        row["pubDate"] = news_item.pubDate
        row["source"] = news_item.source

        rows.append(row)
    df=pd.DataFrame(rows)

    return df

def csv_truncate(df, truncate='fulltext'):
    new_trunced = []
    for l in list(df[truncate]):
        new_trunced.append(l[:30000])
    df[truncate] = new_trunced
    return df



def test_query():

    myfeed=get_feed("Python programming")
    mydf=feed_to_df(myfeed)
    mydf.to_csv("output/test.csv",encoding="utf-8-sig", index=False)
    df=pd.read_csv("output/test.csv", encoding="utf-8-sig").fillna("")
    df=all_fulltexts(df)
    df=csv_truncate(df)
    df.to_csv("output/test.csv",encoding="utf-8-sig", index=False, quoting=csv.QUOTE_ALL)

def get_results(df, results, max_results,q):


    article_scraper = GNews()

    total_res = len(df.index)


    retrieved = 0

    ignored = 0
    ignored_tides = []
    if "[Yes]" in st.session_state.fulltexts:
        pr_text = "Scraping articles for your query: {}".format(q)
        art_bar = st.progress(0, text=pr_text)

    for i, row in tqdm(df.iterrows()):

        ti = row["title"].strip()
        li = row["link"].strip()
        des = ti  # there is no description with this method
        # print(ti)

        ti_des = '{} {}'.format(ti, des)



        if len(df.index)>0:

            key = "{} {}".format(ti, li)
            existing = results.get(key, False)  # does the article already exist in previos results?
            thisrank = int((i + 10) / 10)  # simulating paging: to rank relevance, all refernce on a specific page are assumed to be equally relevant, they are less relevant than the articles from the previous page, and more relevant then the articles from the next page

            if existing == False:  # the article is not yet present in the results

                if "[Yes]" in st.session_state.fulltexts:
                    fulltxt = get_fulltext(li, article_scraper)
                else:
                    fulltxt="Not retrieved"

                results[key] = {
                    'title': ti,
                    'description': des,
                    'media': row["source"].strip(),
                    "decision": " ",
                    'link': li,
                    'date': str(row["pubDate"]).strip(),
                    "fulltext": fulltxt[:30000],
                    # we truncate to the first 30k characters because excel has a hard 32k limit and sometimes the counting of whitespaces differes
                    'min_page': thisrank,
                    'appearances': 1,
                    'queries':[q]
                }
            else:  # this article has already been retrieved! So we just check if here it has a better rank, and increment its appearances. Having appeared before is a good thing, so we need tomake sure that the article gets bumped up later in the search results
                rank = results[key][
                    'min_page']  # if this is part of a boolean search then we record the minimum page; the idea is that more relevant search results appear earlier
                if rank > thisrank:  # if the old page is larger than the new page, then we want to add the new page as the best (ie 'min_page' that the article ever appeared at)
                    results[key]['min_page'] = thisrank
                results[key]['appearances'] += 1  # also, if part of a bool search with multiple terms, the more often an article appears in different searches, the more valuable it might be
                results[key]['queries'].append(q)
            retrieved += 1
            if "[Yes]" in st.session_state.fulltexts:
                my_max=min([max_results, len(df.index)])#sometimes we retrieve less than the max value of articles, so then we need to adjust the pbar
                art_bar.progress((i + 1) / my_max, text=pr_text)
            if retrieved == max_results:  # end looping if we reached max_results
                break
    searchdoc={"query": q, "overall_hits":len(df.index),	"number_retrieved":retrieved,	"max_allowed_results":max_results,	"total_aggregated_and_deduplicated":len(results.keys())}

    #print(results)
    return results,searchdoc


def scanar_retrieval():

    max_results=st.session_state.num_ret
    results = {}  # across multiple queries, here we will save the results
    mysearches={}
    progress_text = "Retrieving your queries..."

    my_bar = st.progress(0, text=progress_text)

    for i, query in enumerate(st.session_state.queries):
        time.sleep(3)
        myfeed = get_feed(query, starter=st.session_state.dates)
        df=feed_to_df(myfeed)
        results, searchd=get_results(df, results, max_results, query)
        mysearches[i]=searchd
        my_bar.progress((i + 1) / len(st.session_state.queries), text=progress_text)


    st.session_state.all_res=pd.DataFrame([v for v in results.values()])
    st.session_state.all_res = st.session_state.all_res.sort_values(by=['min_page', 'appearances'],ascending=[True, False])  # the ranking algorithm
    st.session_state.all_searchdoc = pd.DataFrame([v for v in mysearches.values()])



