from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.core.mail import send_mail

from .forms import EmailPostForm, CommentForm
from .models import Post


# def post_list(request):
#     post_list = Post.published.all()
#     paginator = Paginator(post_list, 3, orphans=2)
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.page(page_number)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)
#     except PageNotAnInteger:
#         posts = paginator.page(1)
#
#     return render(request, 'blog/post/list.html', {'posts': posts})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    template_name = 'blog/post/list.html'
    paginate_by = 3
    paginate_orphans = 2


def post_detail(request, post, year, month, day):
    post = get_object_or_404(Post,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day,
                             status=Post.Status.PUBLISHED)
    comments = post.comments.filter(active=True)
    form = CommentForm()

    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'form': form})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.POST:
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # print(post.get_absolute_url())  - /blog/2024/1/16/benjamin-franklin-s-inventions/
            post_url = request.build_absolute_uri(post.get_absolute_url())
            # request.build_absolute_uri(post.get_absolute_url())  - http://127.0.0.1:8000/blog/2024/1/16/benjamin-franklin-s-inventions/
            subject = f'{cd["name"]} recommends you read {post.title}'
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}'s comments: {cd['comments']}"
            send_mail(subject, message, 'alykovyaroslav@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})

