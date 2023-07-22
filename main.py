
import sys
from turtle import pos
from fastapi import FastAPI,Response,status,HTTPException,Depends
from fastapi.param_functions import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)


app=FastAPI()



class post(BaseModel):
    title: str
    content: str
    published: bool=True

try:
    conn=psycopg2.connect(host='localhost', database ='fastapi',user='postgres',password='password123',cursor_factory=RealDictCursor) 
    cursor=conn.cursor()
    print('connection sucessful!')
except Exception as error:
    print('connection to database failed')
    print('error',error)
    time.sleep(2)



my_posts=[{"title":"title of post 1","content":"content of post 1","id":1},
          {"title":"favourite food","content":"i like pizza","id":2}]

def find_post(id):
    for p in my_posts:
        if p['id']==id:
            return p 
        
def find_index_post(id):
    for i,p in enumerate(my_posts):
        if p['id']==id:
            return i




@app.get("/")
def root():
    return{"message":"welcome to my api"}

@app.get("/sqlalchemy")
def test_posts(db:Session=Depends(get_db)):

    posts=db.query(models.Post).all()
    return{"status":posts}


@app.get("/posts")
def get_posts(db:Session=Depends(get_db)):
    #cursor.execute("""select * from posts""")
    #posts = cursor.fetchall()
    posts=db.query(models.Post).all()

    return{"data":posts}

@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_posts(post:post,db:Session=Depends(get_db)):
#    cursor.execute(""" insert into posts(title,content,published) 
#                   values(%s,%s,%s) returning *""",
#                   (post.title,post.content,post.published))
#    new_post=cursor.fetchone()
#    conn.commit()
    new_post=models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return{"data":new_post}



@app.get("/posts/{id}")
def get_post(id:int, db:Session=Depends(get_db)):
    post=db.query(models.Post).filter(models.Post.id==id).first()
    

    #cursor.execute("""select * from posts where id = %s""",(str(id),))
    #post=cursor.fetchone()
    #conn.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found ")
        #response.status_code=status.HTTP_404_NOT_FOUND
        #return{"message":f"id: {id} was not found"}
    return{"post_details":post}

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,db:Session=Depends(get_db)):
    #find the index of item to be deleted 
    #cursor.execute(""" delete from posts where id = %s returning *""",(str(id),))
    #deleted_post=cursor.fetchone()
    #conn.commit()
    post=db.query(models.Post).filter(models.Post.id==id)

    if post.first()==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

    


    

@app.put("/posts/{id}")
def update_post(id:int, updated_post:post,db:Session=Depends(get_db)):
#    cursor.execute("""update posts set title = %s, content=%s,published=%s where id=%s returning*""",
#                   (post.title,post.content,post.published,str(id)))
#    updated_post=cursor.fetchone()
#    conn.commit() 
    post_query=db.query(models.Post).filter(models.Post.id==id)
    post=post_query.first()
 
    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    
    post_query.update(updated_post.dict(),synchronize_session=False)
    db.commit()

    return{"data":post_query.first()}

