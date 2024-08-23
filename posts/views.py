from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostCreateForm, CommentForm
from django.contrib.auth.decorators import login_required
from .models import Post
from django.http import JsonResponse

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostCreateForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            return redirect('posts:feed')  # Redirect to the feed after creating a post
    else:
        form = PostCreateForm()
    return render(request, 'posts/create.html', {'form': form})

def feed(request):
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            post_id = request.POST.get('post_id')
            post = get_object_or_404(Post, id=post_id)
            new_comment.post = post
            new_comment.user = request.user  # Set the user for the comment
            new_comment.save()
            return redirect('posts:feed')  # Redirect to avoid re-posting on page refresh
        else:
            # Print form errors for debugging
            print(comment_form.errors)
    else:
        comment_form = CommentForm()

    posts = Post.objects.all()
    logged_user = request.user
    return render(request, 'posts/feed.html', {'posts': posts, 'logged_user': logged_user, 'comment_form': comment_form})

@login_required
def like_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        if post.liked_by.filter(id=request.user.id).exists():
            post.liked_by.remove(request.user)
        else:
            post.liked_by.add(request.user)
        
        return JsonResponse({'success': True, 'likes_count': post.liked_by.count()})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
