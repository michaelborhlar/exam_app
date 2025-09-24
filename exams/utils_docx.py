from docx import Document
import re
from .models import Question, Choice

# Expected docx format:
# 1. Question text
# A. Option A
# B. Option B
# C. Option C
# D. Option D
# Answer: A

def parse_docx_to_exam(docx_file, exam):
    doc = Document(docx_file)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    i = 0
    while i < len(paragraphs):
        p = paragraphs[i]
        if re.match(r'^\d+\.', p):
            qtext = re.sub(r'^\d+\.?\s*', '', p)
            i += 1
            options = []
            while i < len(paragraphs) and re.match(r'^[A-Z]\.', paragraphs[i]):
                opt = re.sub(r'^[A-Z]\.\s*', '', paragraphs[i])
                options.append(opt)
                i += 1
            ans = None
            if i < len(paragraphs) and re.match(r'(?i)^answer[:\s]', paragraphs[i]):
                ans_line = re.sub(r'(?i)^answer[:\s]*', '', paragraphs[i]).strip()
                ans = ans_line.split()[0].strip()
                i += 1
            q = Question.objects.create(exam=exam, text=qtext)
            for idx, opt in enumerate(options):
                is_correct = False
                if ans:
                    letters = re.findall(r'[A-Z]', ans.upper())
                    letter = chr(ord('A') + idx)
                    if letter in letters:
                        is_correct = True
                Choice.objects.create(question=q, text=opt, is_correct=is_correct)
        else:
            i += 1
