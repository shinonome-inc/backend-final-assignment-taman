from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from .forms import TweetForm
from .models import Tweet

User = get_user_model()


class HomeView(LoginRequiredMixin, ListView):
    template_name = "tweets/home.html"
    model = Tweet
    queryset = model.objects.select_related("user").order_by("-created_at")


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
