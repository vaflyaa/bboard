from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.core.signing import BadSignature
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy

from .models import AdvUser
from .forms import ChangeUserInfoForm, RegisterUserForm
from .utilities import signer

def index(request):
    return render(request, 'main/index.html')

# 
def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))

@login_required
def profile(request):
    return render(request, 'main/profile.html')


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'main/user_is_activated.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


class BBLoginView(LoginView):
    template_name = 'main/login.html'


class BBLogout(LoginRequiredMixin ,LogoutView):
    template_name = 'main/logout.html'

# SuccessMessageMixin - для вывода всплывающих сообщений в случае успеха
class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'main/change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Данные пользователя изменены'

    # Достаем user_id,  метод наследуется от View, выполняет инициализацию
    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)
    
    # По этому user_id находим запись о user. Метод наследуется от SingleObjectMixin
    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль пользователя успешно изменен'


class BBPasswordResetView(PasswordResetView):
    template_name = 'main/password_reset_form.html'
    subject_template_name = 'email/reset_subject.txt'
    email_template_name = 'email/reset_email.txt'
    success_url = reverse_lazy('main:password_reset_done')


class BBPasswordResetDoneView(TemplateView):
    template_name = 'main/password_reset_done.html'


class BBPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = 'main/confirm_password_reset.html'
    success_url = reverse_lazy('main:login')
    success_message = 'Пароль пользователя был успешно изменен'


class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # перед удалением, делаем выход и создаем всплывающие сообщение
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)