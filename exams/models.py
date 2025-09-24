from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    ROLE_CHOICES = (('staff', 'Staff'), ('student', 'Student'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)


    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Exam(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=10)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_exams')


    def end_time(self):
        if self.start_time:
            return self.start_time + timezone.timedelta(minutes=self.duration_minutes)
        return None

    def is_active(self):
        """Check if the exam is currently running (start <= now <= end)."""
        now = timezone.now()
        return self.start_time and self.start_time <= now <= self.end_time()

    def time_left_seconds(self):
        """Return exact number of seconds left, never negative."""
        if not self.end_time():
            return 0
        left = (self.end_time() - timezone.now()).total_seconds()
        return max(0, int(left))


    def __str__(self):
        return self.title


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()


    def __str__(self):
        return self.text[:50]


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=1000)
    is_correct = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.text[:40]} ({'correct' if self.is_correct else 'wrong'})"


class StudentSubmission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
# store answers as JSON string: {question_id: choice_id}
    answers = models.JSONField(default=dict)
    score = models.FloatField(null=True, blank=True)


    


    def submit(self):
# calculate score
        total = 0
        correct = 0
        for qid, cid in self.answers.items():
            try:
                choice = Choice.objects.get(id=cid)
                total += 1
                if choice.is_correct:
                    correct += 1
            except Choice.DoesNotExist:
                continue
        self.score = (correct / total * 100) if total else 0
        self.submitted_at = timezone.now()
        self.save()


    def time_left_seconds(self):
        if self.exam.start_time:
            end = self.exam.start_time + timezone.timedelta(minutes=self.exam.duration_minutes)
        return max(int((end - timezone.now()).total_seconds()), 0)
# fallback: if started_at + duration
        end = self.started_at + timezone.timedelta(minutes=self.exam.duration_minutes)
        return max(int((end - timezone.now()).total_seconds()), 0)


    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"