from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from .models import Student, ProgressSheet, Subject


class StudentForm(forms.ModelForm):
    """
    Form for creating and updating student records.
    """
    class Meta:
        model = Student
        fields = ['full_name', 'email', 'roll_number', 'class_batch', 'date_of_birth']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'class_batch': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
        }
    
    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if not full_name or full_name.strip() == '':
            raise ValidationError('Full name is required.')
        return full_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Email is required.')
        return email
    
    def clean_roll_number(self):
        roll_number = self.cleaned_data.get('roll_number')
        if not roll_number or roll_number.strip() == '':
            raise ValidationError('Roll number is required.')
        return roll_number


class SubjectForm(forms.ModelForm):
    """
    Form for creating and updating subjects.
    """
    class Meta:
        model = Subject
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or name.strip() == '':
            raise ValidationError('Subject name is required.')
        return name
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code or code.strip() == '':
            raise ValidationError('Subject code is required.')
        return code


class ProgressSheetForm(forms.ModelForm):
    """
    Form for creating and updating progress sheet records.
    """
    class Meta:
        model = ProgressSheet
        fields = ['student', 'subject', 'exam_type', 'exam_date', 'marks_obtained', 'max_marks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'subject': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'exam_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'exam_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': True}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': True}),
        }
    
    def clean_marks_obtained(self):
        marks_obtained = self.cleaned_data.get('marks_obtained')
        if marks_obtained is None:
            raise ValidationError('Marks obtained is required.')
        if marks_obtained < 0:
            raise ValidationError('Marks obtained cannot be negative.')
        if marks_obtained > 100:
            raise ValidationError('Marks obtained cannot exceed 100.')
        return marks_obtained
    
    def clean_max_marks(self):
        max_marks = self.cleaned_data.get('max_marks')
        if max_marks is None:
            raise ValidationError('Max marks is required.')
        if max_marks <= 0:
            raise ValidationError('Max marks must be greater than 0.')
        if max_marks > 100:
            raise ValidationError('Max marks cannot exceed 100.')
        return max_marks
    
    def clean(self):
        cleaned_data = super().clean()
        marks_obtained = cleaned_data.get('marks_obtained')
        max_marks = cleaned_data.get('max_marks')
        
        if marks_obtained is not None and max_marks is not None:
            if marks_obtained > max_marks:
                raise ValidationError('Marks obtained cannot be greater than max marks.')
        
        return cleaned_data


class BulkProgressSheetForm(forms.Form):
    """
    Form for bulk entry of progress sheets for a student across subjects for a specific exam type.
    """
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control', 'required': True})
    )
    exam_type = forms.ChoiceField(
        choices=ProgressSheet.EXAM_TYPE_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control', 'required': True})
    )
    exam_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamically add fields for each subject
        for subject in Subject.objects.all():
            self.fields[f'marks_{subject.id}'] = forms.DecimalField(
                label=subject.name,
                max_digits=5,
                decimal_places=2,
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                required=False,
                widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'})
            )
            self.fields[f'max_marks_{subject.id}'] = forms.DecimalField(
                label=f'Max Marks for {subject.name}',
                max_digits=5,
                decimal_places=2,
                validators=[MinValueValidator(1), MaxValueValidator(100)],
                initial=100,
                required=False,
                widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '1', 'max': '100'})
            )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate marks and max marks for each subject
        for field_name, value in cleaned_data.items():
            if field_name.startswith('marks_'):
                subject_id = field_name.split('_')[1]  # Extract subject ID from field name
                marks_field = f'marks_{subject_id}'
                max_marks_field = f'max_marks_{subject_id}'
                
                marks = cleaned_data.get(marks_field)
                max_marks = cleaned_data.get(max_marks_field)
                
                if marks is not None and max_marks is not None:
                    if marks > max_marks:
                        raise ValidationError(f'Marks for subject cannot be greater than max marks for that subject.')
                    if marks < 0:
                        raise ValidationError(f'Marks for subject cannot be negative.')
                    if marks > 100:
                        raise ValidationError(f'Marks for subject cannot exceed 100.')
        
        return cleaned_data