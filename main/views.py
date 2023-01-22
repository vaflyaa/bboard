from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
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
from django.core.paginator import Paginator
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy

from .models import AdvUser, SubRubric, Bb
from .forms import ChangeUserInfoForm, RegisterUserForm, SearchForm, BbForm, AIFormSet
from .utilities import signer

def index(request):
    bbs = Bb.objects.filter(is_active=True) [:10]
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        bbs = Bb.objects.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(bbs, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'bbs': page.object_list, 'form': form, 'page': page}
    return render(request, 'main/index.html', context)

# 
def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))

@login_required
def profile(request):
    bbs = Bb.objects.filter(author=request.user.pk)
    context = {'bbs': bbs}
    return render(request, 'main/profile.html', context)


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


def by_rubric(request, pk):
    rubric = get_object_or_404(SubRubric, pk=pk)
    bbs = Bb.objects.filter(is_active=True, rubric=pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        bbs = Bb.objects.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(bbs, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'rubric': rubric, 'page': page,'bbs': page.object_list, 'form': form}
    return render(request, 'main/by_rubric.html', context)


def detail(request, rubric_pk, pk):
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additionalimage_set.all()
    context = {'bb': bb, 'ais': ais}
    return render(request, 'main/detail.html', context)

@login_required
def profile_bb_detail(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additionalimage_set.all()
    context = {'bb': bb, 'ais': ais}
    return render(request, 'main/profile_bb_detail.html', context)


@login_required
def profile_bb_add(request):
    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES)
        if form.is_valid():
            bb = form.save()
            # Сначала выполняется валидация и сохр. формы, потом передаем ее набору форм, тобы связать иллюстрации с bb
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление добавлено')
                return redirect('main:profile')
    else:
        form = BbForm(initial={'author': request.user.pk})
        formset = AIFormSet()
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_bb_add.html', context)


@login_required
def profile_bb_change(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES, instance=bb)
        if form.is_valid():
            bb = form.save()
            # Сначала выполняется валидация и сохр. формы, потом передаем ее набору форм, тобы связать иллюстрации с bb
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление исправлено')
                return redirect('main:profile')
    else:
        form = BbForm(instance=bb)
        formset = AIFormSet(instance=bb)
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_bb_change.html', context)


@login_required
def profile_bb_delete(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    if request.method == 'POST':
        bb.delete()
        messages.add_message(request, messages.SUCCESS, 'Объявление удалено')
        return redirect('main:profile')
    else:
        context = {'bb': bb}
        return render(request, 'main/profile_bb_delete.html', context)


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