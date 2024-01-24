from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import numpy as np
import pickle
import requests



app = FastAPI()

new_df= pickle.load(open('pickle/new_df.pkl','rb'))
similarity_scores = pickle.load(open('pickle/similarity_scores.pkl','rb'))

templates = Jinja2Templates(directory='templates')


def fetch_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=27bb03ffeadd16543e243336baf9ac12&language=en-US'.format(movie_id))
    data = response.json()
    poster_path = 'https://image.tmdb.org/t/p/original'+data['poster_path']

    return poster_path

@app.get('/')
def popular(request:Request):
    return templates.TemplateResponse('popular.html',{'request':request ,'name':'popular'})

@app.get('/recommend')
def recommend(request:Request):
    return templates.TemplateResponse(
        'recommend.html',{'request':request,'name':'Recommend'},
        )

@app.post('/recommend_movies')
def recommend_movie(request:Request,user_input:str = Form(...)):
    # movie = request.get('user_input') does not work
    index = np.where(new_df['title']==user_input)
    score = similarity_scores[index][0]
    index_score = list(enumerate(score))
    most_similar = sorted(index_score,key = lambda x:x[1],reverse=True)[1:6]
    
    outer_l = []
    for i in most_similar:
        inner_l = []
        movie_id = new_df.iloc[i[0]].id
        movie_title = new_df.iloc[i[0]].title
        
        inner_l.append(movie_id)
        inner_l.append(movie_title)
        inner_l.append(fetch_poster(movie_id))
        
        outer_l.append(inner_l)

    return templates.TemplateResponse(
        'recommend.html',
        {'request':request,'name':'Recommended Movies','data':outer_l}
        )  