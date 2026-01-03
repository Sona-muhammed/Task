from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator


class Student(models.Model):
    """
    Model representing a student in the system.
    """
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    roll_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z0-9]+[A-Za-z0-9\-]*[A-Za-z0-9]+$',
                message="Roll number must contain alphanumeric characters and hyphens only."
            )
        ]
    )
    CLASS_CHOICES = [
        ('FY', 'First Year'),
        ('SY', 'Second Year'),
        ('TY', 'Third Year'),
        ('FYJC', 'First Year Junior College'),
        ('SYJC', 'Second Year Junior College'),
    ]
    class_batch = models.CharField(max_length=10, choices=CLASS_CHOICES)
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.roll_number})"
    
    class Meta:
        ordering = ['roll_number']


class Subject(models.Model):
    """
    Model representing a subject for which students can have marks.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class ProgressSheet(models.Model):
    """
    Model representing a student's progress sheet with exam results.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progress_sheets')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='progress_sheets')
    
    EXAM_TYPE_CHOICES = [
        ('quarterly', 'Quarterly'),
        ('midterm', 'Midterm'),
        ('model', 'Model'),
        ('end_term', 'End Term'),
    ]
    
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES)
    exam_date = models.DateField()
    marks_obtained = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    max_marks = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(1)]
    )
    percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
        null=True
    )
    grade = models.CharField(max_length=3, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calculate percentage if marks are provided
        if self.max_marks and self.marks_obtained is not None:
            self.percentage = (self.marks_obtained / self.max_marks) * 100
            # Calculate grade based on percentage
            if self.percentage >= 90:
                self.grade = 'A+'
            elif self.percentage >= 80:
                self.grade = 'A'
            elif self.percentage >= 70:
                self.grade = 'B+'
            elif self.percentage >= 60:
                self.grade = 'B'
            elif self.percentage >= 50:
                self.grade = 'C'
            elif self.percentage >= 40:
                self.grade = 'D'
            else:
                self.grade = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name} - {self.get_exam_type_display()}"

    class Meta:
        unique_together = ('student', 'subject', 'exam_type', 'exam_date')
        ordering = ['student', 'subject', 'exam_date', 'exam_type']


class ExamResult(models.Model):
    """
    Model to store calculated results like total marks and average for a student across all subjects in an exam type.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_results')
    
    EXAM_TYPE_CHOICES = [
        ('quarterly', 'Quarterly'),
        ('midterm', 'Midterm'),
        ('model', 'Model'),
        ('end_term', 'End Term'),
    ]
    
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES)
    total_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    max_possible_marks = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    average_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
        null=True
    )
    exam_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.get_exam_type_display()} - {self.average_percentage}%"

    class Meta:
        unique_together = ('student', 'exam_type', 'exam_date')
        ordering = ['student', 'exam_date', 'exam_type']