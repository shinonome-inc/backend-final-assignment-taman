from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View

from .forms import TweetForm
from .models import Like, Tweet

User = get_user_model()


class HomeView(LoginRequiredMixin, ListView):
    template_name = "tweets/home.html"
    model = Tweet
    queryset = model.objects.select_related("user").prefetch_related("likes").order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        likes = Like.objects.select_related("target").filter(user=self.request.user).values_list("target", flat=True)
        context["user_like_list"] = likes
        return context


class TweetCreateView(LoginRequiredMixin, CreateView):
    template_name = "tweets/create.html"
    success_url = reverse_lazy("tweets:home")
    form_class = TweetForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TweetDetailView(LoginRequiredMixin, DetailView):
    template_name = "tweets/detail.html"
    model = Tweet
    queryset = model.objects.select_related("user")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_liked"] = Like.objects.filter(user=self.request.user, target_id=self.kwargs["pk"]).exists()
        context["liked_count"] = Like.objects.filter(target_id=self.kwargs["pk"]).count()
        return context


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "tweets/delete.html"
    model = Tweet
    queryset = model.objects.select_related("user")
    success_url = reverse_lazy("tweets:home")

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def test_func(self):
        self.object = self.get_object()
        return self.request.user == self.object.user


class LikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        tweet = get_object_or_404(Tweet, pk=kwargs["pk"])
        Like.objects.get_or_create(target=tweet, user=user)
        likes_count = Like.objects.filter(target=tweet).count()
        context = {"liked_count": likes_count}
        return JsonResponse(context)


class UnlikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        tweet = get_object_or_404(Tweet, pk=kwargs["pk"])
        like = Like.objects.filter(target=tweet, user=user)

        if like.exists():
            like.delete()

        likes_count = Like.objects.prefetch_related("target").filter(target=tweet).count()
        context = {"liked_count": likes_count}
        return JsonResponse(context)
