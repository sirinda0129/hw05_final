from django.db import models

from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):

    title = models.CharField(max_length = 200)
    slug = models.SlugField(unique = True)
    description = models.TextField(max_length = 500)
    
    def __str__(self):
        return ( '%s' % (self.title) )


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_posts")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_posts", blank=True, null=True)
    # поле для картинки
    image = models.ImageField(upload_to='posts/', blank=True, null=True)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comment')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_author')
    text = models.TextField()
    created = models.DateTimeField("Дата создания", auto_now_add=True, db_index=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name='follower')
    author = models.ForeignKey(User, on_delete = models.CASCADE, related_name='following')