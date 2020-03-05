from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Group, User, Comment, Follow

from .forms import PostForm, CommentForm

import datetime as dt

from django.contrib.auth import get_user_model

from django.core.paginator import Paginator

from django.views.decorators.cache import cache_page

from django.contrib.auth.decorators import login_required


User = get_user_model()


def author_followed_check(request, username):
    if request.user.is_authenticated:
        followings = Follow.objects.filter(user = request.user)
        author = get_object_or_404(User, username = username)
        following_authors = []
        for following in followings:
            following_authors.append(following.author)
        if author in following_authors:
            return True
        else:
            return False
    else:
        return False



def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, 'index.html', {'page': page, 'paginator': paginator})



def group_posts(request, slug):
    # функция get_object_or_404 позволяет получить объект из базы данных 
    # по заданным критериям или вернуть сообщение об ошибке если объект не найден
    group = get_object_or_404(Group, slug=slug)
    # Метод .filter позволяет ограничить поиск по критериям. Это аналог добавления
    # условия WHERE group_id = {group_id}
    posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    count = posts.count
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "posts": posts, 'page': page, 'paginator': paginator, 'count' : count})

@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST or None, files =request.FILES or None)
        if form.is_valid():
            Post.objects.create(
                author = request.user,
                text = form.cleaned_data['text'],
                group = form.cleaned_data['group'],
                image = form.cleaned_data['image'],
                )
            return redirect("index")
    form = PostForm()
    return render(request, "new_post.html", {"form": form})

@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return redirect("post", username=request.user.username, post_id=post_id)
    # добавим в form свойство files
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("post", username=request.user.username, post_id=post_id)
    return render(request, "post_edit.html", {"form": form, "post": post},)

def post_view(request, username, post_id):
    author = get_object_or_404(User, username = username)
    profile = User.objects.get(username=username)
    post = Post.objects.get(id=post_id)
    posts_count = Post.objects.filter(author=profile).count()
    form = CommentForm()
    items = Comment.objects.filter(post = post)
    count_followers = Follow.objects.filter(author = author).count()
    count_subscriptions = Follow.objects.filter(user = author).count()
    return render(request, 'post.html', {
        'profile': profile,
        'post': post,
        'posts_count' : posts_count,
        'form':form,
        'items':items,
        'followers':count_followers,
        'subscriptions':count_subscriptions,
        } )

def profile(request, username):
    author = get_object_or_404(User, username = username)
    posts = Post.objects.filter(author = author).order_by('-pub_date')
    count = posts.count
    count_followers = Follow.objects.filter(author = author).count()
    count_subscriptions = Follow.objects.filter(user = author).count()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = author_followed_check(request, username)
    # тут тело функции
    return render(request, "profile.html", {
        'author':author,
        'posts' : posts,
        'page': page,
        'paginator': paginator,
        'count' : count,
        'following':following,
        'followers':count_followers,
        'subscriptions':count_subscriptions,
        } )

def page_not_found(request, exception):
        # Переменная exception содержит отладочную информацию, 
        # выводить её в шаблон пользователской страницы 404 мы не станем
        return render(request, "misc/404.html", {"path": request.path}, status=404)

def server_error(request):
        return render(request, "misc/500.html", status=500)

@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = request.user
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                post = post,
                user = user,
                text = form.cleaned_data['text'],
            )
    return redirect('post', username = username, post_id=post_id)

@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user).select_related('author').order_by('-pub_date').all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, 'follow.html', {'page': page, 'paginator': paginator})

@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username = username)
    following_authors = []
    if not author_followed_check(request, username) and request.user != author:
        user = get_object_or_404(User, username = request.user)
        Follow.objects.create(
            user = request.user,
            author = author
        )
    return redirect('profile', username = username)

@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username = username)
    if author_followed_check(request, username):
        Follw_object = Follow.objects.filter(user = request.user).filter(author = author)
        Follw_object.delete()
    return redirect('profile', username = username)