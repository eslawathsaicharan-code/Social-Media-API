
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas, oauth2
from app.database import get_db


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


# GET ALL POSTS + VOTE COUNTS
@router.get("/")
def get_posts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""
):
    posts = db.query(
        models.Post,
        func.count(models.Vote.post_id).label("votes")
    ).outerjoin(
        models.Vote,
        models.Vote.post_id == models.Post.id
    ).group_by(
        models.Post.id
    ).filter(
        models.Post.title.contains(search)
    ).limit(
        limit
    ).offset(
        skip
    ).all()

    return [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "published": post.published,
            "created_at": post.created_at,
            "owner_id": post.owner_id,
            "votes": votes
        }
        for post, votes in posts
    ]


# CREATE POST
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.PostOut
)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    new_post = models.Post(
        owner_id=current_user.id,
        **post.model_dump()
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {
        "id": new_post.id,
        "title": new_post.title,
        "content": new_post.content,
        "published": new_post.published,
        "created_at": new_post.created_at,
        "owner_id": new_post.owner_id,
        "votes": 0
    }


# GET ONE POST
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    result = db.query(
        models.Post,
        func.count(models.Vote.post_id).label("votes")
    ).outerjoin(
        models.Vote,
        models.Vote.post_id == models.Post.id
    ).group_by(
        models.Post.id
    ).filter(
        models.Post.id == id
    ).first()

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    post, votes = result

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "published": post.published,
        "created_at": post.created_at,
        "owner_id": post.owner_id,
        "votes": votes
    }


# DELETE POST
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    post_query = db.query(models.Post).filter(
        models.Post.id == id
    )

    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    return None


# UPDATE POST
@router.put("/{id}", response_model=schemas.PostOut)
def update_post(
    id: int,
    post: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    post_query = db.query(models.Post).filter(
        models.Post.id == id
    )

    existing_post = post_query.first()

    if existing_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if existing_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )

    post_query.update(
        post.model_dump(exclude_unset=True),
        synchronize_session=False
    )

    db.commit()

    updated_post = post_query.first()

    return {
        "id": updated_post.id,
        "title": updated_post.title,
        "content": updated_post.content,
        "published": updated_post.published,
        "created_at": updated_post.created_at,
        "owner_id": updated_post.owner_id,
        "votes": db.query(func.count(models.Vote.post_id)).filter(
            models.Vote.post_id == updated_post.id
        ).scalar()
    }
