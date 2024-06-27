import pandas as pd
from tqdm import tqdm
from scanar_utils import get_fulltext
from gnews import GNews
import time

path=r"C:\Users\c1049033\PycharmProjects\ncl_medx\data\MRC_full.csv"

def get_link(inp, linktype="gtr"):
    try:
        if linktype=="gtr":
            return "https://gtr.ukri.org/projects?ref="+inp.split("ref=")[1]
    except:
        print("Error with type {} link: {}".format(linktype, inp))

def scrape_csv(path, linkcol):
    article_scraper = GNews()
    df=pd.read_csv(path).fillna("")
    txts=[]
    for i, row in tqdm(df.iterrows()):
        if i%20==0:
            time.sleep(2)
        lnk=get_link(row[linkcol])
        txts.append(get_fulltext(lnk,article_scraper)[:25000])
        if i%50 ==0:
            txtdf=pd.DataFrame()
            txtdf["backup"]=txts
            txtdf.to_csv(r"C:\Users\c1049033\PycharmProjects\ncl_medx\data\backup.csv")
    df["Fulltext"]=txts
    df.to_csv(r"C:\Users\c1049033\PycharmProjects\ncl_medx\data\mrc_scraped.csv", index=False)
def postprocess_text(path, textcol):
    prepped=[]
    df=pd.read_csv(path).fillna("")
    for i, row in df.iterrows():
        ft=row[textcol].strip()
        statements=["Abstracts are not currently available in GtR for all funded research. This is normally because the abstract was not required at the time of proposal submission, but may be because it included sensitive information such as personal details."]
        for s in statements:
            ft=ft.replace(s, "").strip()
        if ft.startswith("Abstract\n\nFunding\n\ndetails"):
            #print(ft)
            ft=ft.replace("Abstract\n\nFunding\n\ndetails","").strip()
        ft=ft.replace("\n\n", "\n")
        prepped.append(ft)
    df[textcol]=prepped
    df.to_csv(path)

#scrape_csv(path, "GTRProjectUrl")
postprocess_text(r"C:\Users\c1049033\PycharmProjects\ncl_medx\data\mrc_scraped.csv", "Fulltext")

