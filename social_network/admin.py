from django.contrib import admin

from social_network.models import Like, Comment, HashTag, Post

admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(HashTag)
admin.site.register(Post)
