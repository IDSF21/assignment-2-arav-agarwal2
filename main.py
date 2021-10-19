import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import matplotlib.pyplot as plt
import plotly.express as px
import graphviz as  gz
from streamlit_agraph import agraph, TripleStore, Config
from enum import Enum

# Function Definitions


def updatePaper(lookatme, store):
    for paper in lookatme:
        r3 = querydata(paper[0], forward=False)
        for elem in r3:
            if elem["isInfluential"]:
                store.add_triple(elem["citedPaper"]["title"], "Cited by", paper[1])



def getBasicPaperData(paperid, verbose=True):
    @st.cache
    def get_data():
        response = requests.get("https://api.semanticscholar.org/graph/v1/paper/"+paperid+"/?fields=url,title,abstract,venue,year,fieldsOfStudy,authors")
        output = json.loads(response.text)
        return output
    output = get_data()
    #output
    if verbose:
        st.subheader(output["title"])
        st.text(", ".join(elem["name"] for elem in output["authors"]))
        st.text(output["venue"] + " " + str(output["year"]))
        output["abstract"]
        output["url"]
    return output["title"]
    
def returnBasicPaperData(paperid, verbose=True):
    @st.cache
    def get_data():
        response = requests.get("https://api.semanticscholar.org/graph/v1/paper/"+paperid+"/?fields=title,url,venue,year,referenceCount,citationCount")
        output = json.loads(response.text)
        return output
    return get_data()


@st.cache
def querydata(paperid, forward=True, maxpages=5):
    if forward:
        response = requests.get("https://api.semanticscholar.org/graph/v1/paper/"+paperid+"/citations?fields=title,citationCount,isInfluential,venue,year,influentialCitationCount")
    else:
        response = requests.get("https://api.semanticscholar.org/graph/v1/paper/"+paperid+"/references?fields=title,citationCount,isInfluential,venue,year,influentialCitationCount")
    response = json.loads(response.text)
    total = response["data"]
    counter = 1
    while "next" in response.keys():
        if forward:
            response = requests.get("https://api.semanticscholar.org/graph/v1/paper/"+paperid+"/citations?fields=title,citationCount,isInfluential,venue,year,influentialCitationCount&offset="+str(response["next"]))
        else:
            response = requests.get("https://api.semanticscholar.org/graph/v1/paper/"+paperid+"/references?fields=title,citationCount,isInfluential,venue,year,influentialCitationCount&offset="+str(response["next"]))
        response = json.loads(response.text)
        total = total + response["data"]
        counter += 1
        if counter > maxpages:
            break
    return total     


def display_graph(current_title):
    graph = gz.Digraph()

    store = TripleStore()
    store.add_triple(current_title, "", current_title)
        

    for _, t1, _, t2 in st.session_state['paper_list']:
        store.add_triple(t1, "", t2)


    agraph(list(store.getNodes()), (store.getEdges() ), config = Config(height=500, width=700, nodeHighlightBehavior=True, highlightColor="#F7A7A6", directed=True,
                    collapsible=True))

    st.graphviz_chart(graph)


def init_callback(user_input):
    st.session_state['paper_hist'].append(user_input)
    st.session_state['exploration_state'] = 1

#TODO: Add input validation to the search box, using the /paper/id system.

def add_fd_paper_callback(forward_info, user_input, current_title, choice_forward, move=True):
    for elem in forward_info:
        if elem["citingPaper"]["title"] == choice_forward:
            st.session_state['paper_list'].append((user_input, current_title, elem["citingPaper"]["paperId"], choice_forward))
            st.session_state['paper_list'] = list(set(st.session_state['paper_list']))
            if move:
                st.session_state['paper_hist'].append(elem["citingPaper"]["paperId"])
                
            break

def add_bk_paper_callback(backward_info, user_input, current_title, choice_backward, move=True):
    for elem in backward_info:
        if elem["citedPaper"]["title"] == choice_backward:
            st.session_state['paper_list'].append((elem["citedPaper"]["paperId"], choice_backward, user_input, current_title))
            st.session_state['paper_list'] = list(set(st.session_state['paper_list']))
            if move:
                st.session_state['paper_hist'].append(elem["citedPaper"]["paperId"])
            break


def back_button():
    st.session_state['paper_hist'].pop()
    
def paper_hist():
    out = set()
    for _,a,_,b in st.session_state["paper_list"]:
        out.add(a)
        out.add(b)
    out = "\n".join(sorted(list(out)))
    return out

def id_list():
    out = set()
    for a,_,b,_ in st.session_state["paper_list"]:
        out.add(a)
        out.add(b)
    out = list(out)
    return out
if 'paper_list' not in st.session_state:
    # Tuples of the form (last paper id, last paper name, current paper id, current paper name)
    st.session_state['paper_list'] = []
    
if 'paper_hist' not in st.session_state:
    st.session_state['paper_hist'] = []
    

if 'exploration_state' not in st.session_state:
    st.session_state['exploration_state'] = 0
  
st.title('Paper Explorer')  

if st.session_state['exploration_state'] == 0:
    st.header("Welcome to the Paper Explorer! ")
    st.write("Start by going to Semantic Scholar, and looking for the initial seed paper you wish to look at.")
    st.write("Get the Semantic Scholar ID for this paper, and place it here.")
    user_input = st.text_input("Paper Id", "6a9fa4c579bfd4fe4b1b06f384b946c5c28e1c47")
    st.write("Selected Paper:")
    current_title = getBasicPaperData(user_input)
    use_this_paper = st.button("Choose this paper!", on_click=init_callback, args=(user_input,))
    
        
        
else:
    user_input = st.session_state['paper_hist'][-1]
    current_title = getBasicPaperData(user_input, verbose=False)
    forward_info = querydata(user_input)
    backward_info = querydata(user_input, forward=False)
    display_graph(current_title)

    forward_titles = sorted([elem["citingPaper"]["title"] for elem in forward_info if len(elem["citingPaper"]["title"]) > 5])
    backward_titles = sorted([elem["citedPaper"]["title"] for elem in backward_info if len(elem["citedPaper"]["title"]) > 5])
    

    st.header('Paper Information')
    with st.expander("Basic Information"):
        getBasicPaperData(paperid=user_input)
    with st.expander("Most Influential Papers Citing Current Paper"):
        cleaned = [elem for elem in forward_info if elem["isInfluential"] and elem["citingPaper"]["influentialCitationCount"] != None and elem["citingPaper"]["influentialCitationCount"] >= 0]
        cleaned.sort(key=lambda elem: elem["citingPaper"]["influentialCitationCount"], reverse=True)
        cleaned.sort(key=lambda elem: elem["citingPaper"]["citationCount"], reverse=True)
        paper_names = st.container()
        plist = min(10, len(cleaned))
        for elem in range(plist):
            paper_names.text(cleaned[elem]["citingPaper"]["title"],)
    
    with st.expander("Paper Stats"):
        citations = [elem["citingPaper"]["citationCount"] for elem in forward_info if elem["citingPaper"]["citationCount"] != None]
        if citations != []:
            st.markdown("**The most cited paper that cites this paper is:**")
            [elem for elem in forward_info if  elem['citingPaper']['citationCount'] != None  and elem['citingPaper']['citationCount'] == max(citations)][0]['citingPaper']['title']
        
        citations = [elem["citingPaper"]["citationCount"] for elem in forward_info if elem["citingPaper"]["citationCount"] != None]
        if citations != []:
            fig = px.histogram(citations, title="Citation Count on Papers that Cite This Paper")
            st.plotly_chart(fig)
        
        citations = [elem["citedPaper"]["citationCount"] for elem in backward_info if elem["citedPaper"]["citationCount"] != None]
        if citations != []:
            st.markdown("**The most cited paper that this paper cites is:**")
            [elem for elem in backward_info if  elem['citedPaper']['citationCount'] != None  and elem['citedPaper']['citationCount'] == max(citations)][0]['citedPaper']['title']
        
        citations = [elem["citedPaper"]["citationCount"] for elem in backward_info if elem["citedPaper"]["citationCount"] != None]
        if citations != []:
            fig = px.histogram(citations, title="Citation Count on the Papers that this Paper Cites")
            st.plotly_chart(fig)
    
    
        citations = [elem["citedPaper"]["year"] for elem in backward_info if elem["citedPaper"]["year"] != None] +  [elem["citingPaper"]["year"] for elem in forward_info if elem["citingPaper"]["year"] != None] 
        if citations != []:
            fig = px.histogram(citations, title="Years Published on Papers Cited and Citing the Paper")
            st.plotly_chart(fig)
    
    st.header('Navigation')
    with st.form(key="tf2"):
        choice_forward = st.selectbox("Papers Citing This Paper", forward_titles)
        select_forward = st.form_submit_button("Add this paper to reading list", on_click=add_fd_paper_callback, args=(forward_info, user_input, current_title, choice_forward, False))
        select_forward = st.form_submit_button("Go to this paper", on_click=add_fd_paper_callback, args=(forward_info, user_input, current_title, choice_forward, True))
    
    with st.form(key="tf3"):
        choice_backward = st.selectbox("Current Paper Citations", backward_titles)
        select_backward = st.form_submit_button("Add this paper to reading list", on_click=add_bk_paper_callback, args=(backward_info, user_input, current_title, choice_backward, False))
        select_backward = st.form_submit_button("Go to this paper", on_click=add_bk_paper_callback, args=(backward_info, user_input, current_title, choice_backward, True))
    if len(st.session_state["paper_hist"]) > 1:
        st.button("Go back to the last paper.", on_click=back_button)
       
    st.header('Reading List Stats')
    with st.expander('Expand'):
         paper_id_list = id_list()
         out_l = []
         for id in paper_id_list:
             if id != None:
                data = returnBasicPaperData(id)
                out_l.append(data)
         
         years = [elem["year"] for elem in out_l]
         fig = px.histogram(years, title="Year Published for Papers on Reading List")
         st.plotly_chart(fig)
         
         years = [elem["citationCount"] for elem in out_l]
         fig = px.histogram(years, title="# of Citations for Papers on Reading List")
         st.plotly_chart(fig)
             
    read_hist_str = paper_hist()
    st.download_button("Download your reading list!", data=read_hist_str, file_name='ReadingList.txt')
        


