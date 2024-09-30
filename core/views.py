import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .models import Article, Comment, Like, Dislike, Hunt, Favorite
from .forms import LoginForm, RegistrationForm, CommentForm, ArticleForm
from django.contrib.auth import authenticate, login, logout
from django.views.generic import UpdateView, DeleteView
from django.core.exceptions import ObjectDoesNotExist


def search_view(request):
    query = request.GET.get('q')
    results = Hunt.objects.filter(title__icontains=query) if query else []
    context = {'results': results,
               'query': query
               }
    return render(request, 'core/search_results.html', context)


def home_view(request):
    articles = Article.objects.all()
    context = {
        'articles': articles
    }
    return render(request, 'core/home.html', context)


def category_articles(request, category_id):
    articles = Article.objects.filter(category_id=category_id)
    current_time = datetime.datetime.now().timestamp()
    minutes_update = [round((current_time - article.updated_at.timestamp()) / 60) for article in articles]
    articles = list(map(lambda k, v: (k, v), articles, minutes_update))
    context = {
        'articles': articles
    }
    return render(request, 'core/home.html', context)


def article_detal(request, article_id):
    article = Article.objects.get(pk=article_id)
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.article = article
            form.save()
            try:
                form.likes
            except ObjectDoesNotExist:
                Like.objects.create(comment=form)

            try:
                form.dislikes
            except ObjectDoesNotExist:
                Dislike.objects.create(comment=form)
            return redirect('article_detal', article.pk)
    else:
        form = CommentForm()

    try:
        article.likes
    except Exception as e:
        Like.objects.create(article=article)
    try:
        article.dislikes
    except Exception as e:
        Dislike.objects.create(article=article)

    comments = Comment.objects.filter(article=article)

    total_comments_likes = {comment.pk: comment.likes.user.all().count() for comment in comments}
    total_comments_dislikes = {comment.pk: comment.dislikes.user.all().count() for comment in comments}

    total_likes = article.likes.user.all().count()
    total_dislikes = article.dislikes.user.all().count()
    context = {
        'article': article,
        'form': form,
        'comments': comments,
        'total_likes': total_likes,
        'total_dislikes': total_dislikes,
        'total_comments_likes': total_comments_likes,
        'total_comments_dislikes': total_comments_dislikes

    }
    return render(request, 'core/detal.html', context)


def about_view(request):
    return render(request, 'core/about.html')


def contacts_view(request):
    return render(request, 'core/contacts.html')


def account_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    context = {
        'form': form
    }
    return render(request, 'core/account.html', context)


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('account')
    else:
        form = RegistrationForm()

    context = {
        'form': form
    }
    return render(request, 'core/register.html', context)


def user_logout(request):
    logout(request)
    return redirect('home')


def create_article_view(request):
    if request.method == 'POST':
        form = ArticleForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect('detal', form.pk)
    else:
        form = ArticleForm()

    context = {
        'form': form
    }
    return render(request, 'core/article_form.html', context)


class UpdateArticleView(UpdateView):
    model = Article
    template_name = 'core/article_form.html'
    form_class = ArticleForm
    # success_url = '/'


class DeleteArticleView(DeleteView):
    model = Article
    template_name = 'core/article_delete.html'
    success_url = '/'


def add_vote(request, obj_type, obj_id, action):
    from django.shortcuts import get_object_or_404

    obj = None
    if obj_type == 'article':
        obj = get_object_or_404(Article, pk=obj_id)
    elif obj_type == 'comment':
        obj = get_object_or_404(Comment, pk=obj_id)

    try:
        obj.likes
    except Exception as e:
        if obj.__class__ is Article:
            Like.objects.create(article=obj)
        else:
            Like.objects.create(comment=obj)

    try:
        obj.dislikes
    except Exception as e:
        if obj.__class__ is Article:
            Dislike.objects.create(article=obj)
        else:
            Dislike.objects.create(comment=obj)

    if action == 'add_like':
        if request.user in obj.likes.user.all():
            obj.likes.user.remove(request.user.pk)
        else:
            obj.likes.user.add(request.user.pk)
            obj.dislikes.user.remove(request.user.pk)
    elif action == 'add_dislike':
        if request.user in obj.dislikes.user.all():
            obj.dislikes.user.remove(request.user.pk)
        else:
            obj.dislikes.user.add(request.user.pk)
            obj.likes.user.remove(request.user.pk)
    return redirect(request.environ['HTTP_REFERER'])


def add_to_favorites(request, article_id):
    if request.user.is_authenticated:
        article = get_object_or_404(Article, id=article_id)
        Favorite.objects.get_or_create(user=request.user, article=article)
    return redirect('detal', article_id=article_id)


def remove_from_favorites(request, article_id):
    if request.user.is_authenticated:
        article = get_object_or_404(Article, id=article_id)
        Favorite.objects.filter(user=request.user, article=article).delete()
    return redirect('detal', article_id=article_id)


def favorites_list(request):
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user).select_related('article')
        context={'favorites': favorites}
        return render(request, 'core/favorite.html',context)
    return redirect('account')
