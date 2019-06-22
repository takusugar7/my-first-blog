from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Post, Comment
from .forms import PostForm,  CommentForm, LoginForm
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView, View
from .forms import UserCreateForm
from django.contrib.auth import logout
from django.contrib.messages import constants as messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, LogoutView
)


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'myapp/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=post)

    if request.method == "POST": #入力フォームはPOSTなので
        form = CommentForm(request.POST)
        if form.is_valid(): #もし、formの内容が正しい時は
            comment = form.save(commit=False) #formの内容はまだセーブしません！
            comment.post = post
            comment.author = request.user
            comment.save() #ユーザーを追加したのちにセーブ
    else:
        form = CommentForm()

    print(post)
    return render(request, 'myapp/post_detail.html', {
        'post': post,
        'form': form,
        'comments': comments
    }) #form と comment　を追加

    # return render(request, 'myapp/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'myapp/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'myapp/post_edit.html', {'form': form})


#アカウント作成
class Create_Account(CreateView):
    def post(self, request, *args, **kwargs):
        form = UserCreateForm(data=request.POST)
        if form.is_valid():
            form.save()
            #フォームから'username'を読み取る
            username = form.cleaned_data.get('username')
            #フォームから'password1'を読み取る
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
        return render(request, 'myapp/create.html', {'form': form, })

    def get(self, request, *args, **kwargs):
        form = UserCreateForm(request.POST)
        return render(request, 'myapp/create.html', {'form': form, })


create_account = Create_Account.as_view()


#ログイン機能
class Account_login(View):
    def post(self, request, *arg, **kwargs):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            user = User.objects.get(username=username)
            login(request, user)
            return redirect('/')
        return render(request, 'myapp/login.html', {'form': form, })

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        return render(request, 'myapp/login.html', {'form': form, })

account_login = Account_login.as_view()


class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'myapp/post_list.html'
    

# def logout_request(request):
#     logout(request)
#     messages.info(request, "Logged out,please come back again.")
#     return redirect('myapp/post_list')
