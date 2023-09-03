# Social Media API

API service for managing social media with DRF. 
Implemented possibility of creating users, following/unfollowing other users, 
creating posts, add comments for posts and like/dislike posts.
Also add creating posts by schedule via Celery.

## Installation

Python 3 should be installed. Docker should be installed.

    https://github.com/alim2709/social-media-api.git
    cd social_media_api
    python -m venv venv
    source venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py migrate    
    docker run -d -p 6379:6379 redis
    celery -A social_media_api worker -l info -P gevent
    celery -A social_media_api beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler 
    python manage.py runserver

This project uses environment variables to store sensitive information such as the Django secret key and database credentials.
Create a `.env` file in the root directory of your project and add your environment variables to it. This file should not be committed to the repository.
You can see the example in `.env.sample` file.

## Getting access

    create user via /api/user/register/
    get access token via /api/user/token/

## Features

1. Admin panel.
2. Creating user via email.
3. Managing own profile.
4. Possibility to follow/unfollow other users.
5. Filtering profiles by username.
6. Adding pictures to own Profile.
7. Possibility to like/dislike posts.
8. Adding comments to posts.
9. Added different permissions for different actions.
10. JWT authenticated.
11. Documentation located at /api/doc/swagger/
