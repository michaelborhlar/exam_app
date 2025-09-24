from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Profile, Exam, Question, Choice, StudentSubmission
from .forms import RegisterForm, LoginForm, ExamForm, DocxUploadForm
from .utils_docx import parse_docx_to_exam

# Registration
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            u = form.save(commit=False)
            u.set_password(form.cleaned_data['password'])
            u.save()
            role = form.cleaned_data['role']
            Profile.objects.create(user=u, role=role)
            login(request, u)
            return redirect('exams:dashboard')
    else:
        form = RegisterForm()
    return render(request, 'exams/register.html', {'form': form})

# Login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('exams:dashboard')
            else:
                messages.error(request, "Invalid credentials")
    else:
        form = LoginForm()
    return render(request, 'exams/login.html', {'form': form})

# Logout
def logout_view(request):
    logout(request)
    return redirect('exams:login')

@login_required
def dashboard(request):
    profile = request.user.profile
    if profile.role == 'staff':
        exams = Exam.objects.filter(created_by=request.user)
        doc_form = DocxUploadForm()
        return render(request, 'exams/staff_dashboard.html', {
            'exams': exams,
            'doc_form': doc_form
        })
    else:
        available = Exam.objects.all()
        submissions = StudentSubmission.objects.filter(student=request.user)
        return render(request, 'exams/student_dashboard.html', {
            'exams': available,
            'submissions': submissions
        })

@login_required
def create_exam(request):
    if request.user.profile.role != 'staff':
        return redirect('exams:dashboard')
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            return redirect('exams:dashboard')
    else:
        form = ExamForm()
    return render(request, 'exams/create_exam.html', {'form': form})

@login_required
def upload_docx(request):
    if request.user.profile.role != 'staff':
        return redirect('exams:dashboard')
    if request.method == 'POST':
        form = DocxUploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['docx_file']
            exam = form.cleaned_data['exam']
            parse_docx_to_exam(f, exam)
            messages.success(request, "Questions uploaded successfully")
            return redirect('exams:dashboard')
    return redirect('exams:dashboard')

@login_required
def exam_detail(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    profile = request.user.profile
    if profile.role == 'staff' and exam.created_by == request.user:
        return render(request, 'exams/exam_detail_staff.html', {'exam': exam})

    # student view
    submission, _ = StudentSubmission.objects.get_or_create(student=request.user, exam=exam)
    if request.method == 'POST':
        answers = {}
        for q in exam.questions.all():
            a = request.POST.get(f'question_{q.id}')
            if a:
                answers[str(q.id)] = int(a)
        submission.answers = answers
        submission.submit()
        return render(request, 'exams/exam_submitted.html', {'score': submission.score})

    time_left = submission.time_left_seconds()
    return render(request, 'exams/exam_detail.html', {
        'exam': exam,
        'submission': submission,
        'time_left': time_left
    })

@login_required
def edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam updated successfully")
            return redirect('exams:dashboard')
    else:
        form = ExamForm(instance=exam)
    return render(request, 'exams/edit_exam.html', {'form': form, 'exam': exam})

@login_required
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    if request.method == 'POST':
        exam.delete()
        messages.success(request, "Exam deleted")
        return redirect('exams:dashboard')
    return render(request, 'exams/delete_exam.html', {'exam': exam})

@login_required
def exam_results(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    # Only staff who created the exam can see results
    if request.user.profile.role != 'staff' or exam.created_by != request.user:
        messages.error(request, "You are not allowed to view results for this exam.")
        return redirect('exams:dashboard')

    submissions = StudentSubmission.objects.filter(exam=exam).select_related("student")

    return render(request, "exams/exam_results.html", {
        "exam": exam,
        "submissions": submissions
    })
