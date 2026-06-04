from dataclasses import fields
import re

from django import forms
from .models import *


class TicketForm(forms.Form):
    SUBJECT_CHOICES = (
        ('پیشنهاد', 'پیشنهاد'),
        ('انتقاد', 'انتقاد'),
        ('گزارش', 'گزارش'),
    )

    name = forms.CharField(max_length=30, required=True,
                           label='نام و نام خانوادگی')
    email = forms.EmailField(required=False, label='ایمیل')
    phone = forms.CharField(max_length=11, required=True, label='تلفن همراه')
    title = forms.CharField(max_length=50, required=True, label='عنوان')
    description = forms.CharField(widget=forms.Textarea,
                                  required=True, label='جزئیات')
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES, label='موضوع')

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone:
            if phone.isnumeric() and len(phone) == 11 and phone.startswith('09'):
                return phone
            else:
                raise forms.ValidationError("شماره تلفن درست نیس!")
        else:
            raise forms.ValidationError("شماره تلفن را وارد کنید")

    def clean_title(self):
        title = self.cleaned_data['title']
        if title:
            if len(title) > 50:
                raise forms.ValidationError('لطفا عنوان را کوتاه وارد کنبد')
            if not all(tl.isalnum() or tl.isspace() for tl in title):
                raise forms.ValidationError(
                    'از وارد کاراکتر های خاص خودداری کنید')
            else:
                return title
        else:
            raise forms.ValidationError('لطفا عنوان را وارد کنید!')

    def clean_name(self):
        name = self.cleaned_data['name']
        if name:
            if len(name) <= 2:
                raise forms.ValidationError('نام کوتاه است')
            if not all(na.isalpha() or na.isspace() for na in name):
                raise forms.ValidationError(
                    'از وارد کردن عدد و کاراکتر های خاص خودداری نمایید!')
            if len(name) > 30:
                raise forms.ValidationError('نام طولانی است!')
            else:
                return name
        else:
            raise forms.ValidationError('نام خود را وارد کنید!')

    def clean_description(self):
        description = self.cleaned_data['description']
        if description:
            if len(description) <= 10:
                raise forms.ValidationError("جزئیات کوتاه است")
            else:
                return description
        else:
            raise forms.ValidationError("جزئیات نباید خالی باشد!")


class CommentForm(forms.ModelForm):
    def clean_name(self):
        name = self.cleaned_data['name']
        if name:
            if len(name) <= 2:
                raise forms.ValidationError('نام کوتاه است')
            if not all(na.isalpha() or na.isspace() for na in name):
                raise forms.ValidationError(
                    'از وارد کردن عدد و کاراکتر های خاص خودداری نمایید!')
            if len(name) > 30:
                raise forms.ValidationError('نام طولانی است!')
            else:
                return name
        else:
            raise forms.ValidationError('نام خود را وارد کنید!')

    def clean_message(self):
        message = self.cleaned_data['message']
        if message:
            if len(message) <= 5:
                raise forms.ValidationError("دیدگاه شما کوتاه است")
            else:
                return message
        else:
            raise forms.ValidationError("متن نباید خالی باشد!")

    class Meta:
        model = Comment
        fields = ('name', 'message')


class SearchForm(forms.Form):
    query = forms.CharField(label="جست و جو")


ImageFormSet = forms.inlineformset_factory(
    Post, Image,
    fields=('image_file', 'title', 'description'),
    extra=2, max_num=2
)


class AddPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'description', 'reading_time', 'category')


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, required=True)
    password = forms.CharField(
        max_length=20, required=True, widget=forms.PasswordInput)


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        max_length=20, widget=forms.PasswordInput, label="گذرواژه")
    password_confirm = forms.CharField(
        max_length=20, widget=forms.PasswordInput, label="تایید گذرواژه")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_password_confirm(self):
        cd = self.cleaned_data
        if cd['password_confirm'] != cd['password']:
            raise forms.ValidationError(
                "گذرواژه ها یکی نیستند لطفا دوباره وارد کنید گذرواژه را.")

        return cd['password_confirm']


class EditUserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class EditAccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['birth_day_date', 'job', 'bio', 'photo']
