from django import forms
from django.contrib.auth.models import User
from .models import Exam, Question, Choice


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=(('student','Student'),('staff','Staff')))


    class Meta:
        model = User
        fields = ['username','email','password']


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class ExamForm(forms.ModelForm):
    start_time = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
    class Meta:
        model = Exam
        fields = ['title','description','start_time','duration_minutes']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text','is_correct']


class DocxUploadForm(forms.Form):
    docx_file = forms.FileField()
    exam = forms.ModelChoiceField(queryset=Exam.objects.all())