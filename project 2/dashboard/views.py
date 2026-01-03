from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Avg, Count
from django.db.models import Q
from .models import Student, ProgressSheet, Subject, ExamResult
from .forms import StudentForm, ProgressSheetForm, SubjectForm, BulkProgressSheetForm


@login_required
def dashboard(request):
    """
    Dashboard view that requires authentication.
    """
    return render(request, 'dashboard/dashboard.html')


@staff_member_required
def admin_dashboard(request):
    """
    Admin dashboard view that requires staff status.
    """
    from auth_module.models import CustomUser
    
    # You can add admin-specific data here
    user_count = CustomUser.objects.count()
    verified_count = CustomUser.objects.filter(is_verified=True).count()
    unverified_count = CustomUser.objects.filter(is_verified=False).count()
    
    # Get student counts
    student_count = Student.objects.count()
    progress_sheet_count = ProgressSheet.objects.count()
    subject_count = Subject.objects.count()
    
    context = {
        'user_count': user_count,
        'verified_count': verified_count,
        'unverified_count': unverified_count,
        'student_count': student_count,
        'progress_sheet_count': progress_sheet_count,
        'subject_count': subject_count,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def student_list(request):
    """
    View to list all students.
    """
    students = Student.objects.all()
    return render(request, 'dashboard/student_list.html', {'students': students})


@login_required
def add_student(request):
    """
    View to add a new student.
    """
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully.')
            return redirect('dashboard:student_list')
    else:
        form = StudentForm()
    return render(request, 'dashboard/student_form.html', {'form': form, 'title': 'Add Student'})


@login_required
def update_student(request, student_id):
    """
    View to update an existing student.
    """
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully.')
            return redirect('dashboard:student_list')
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'dashboard/student_form.html', {
        'form': form, 
        'title': 'Update Student',
        'student': student
    })


@login_required
def delete_student(request, student_id):
    """
    View to delete a student.
    """
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully.')
        return redirect('dashboard:student_list')
    
    return render(request, 'dashboard/student_confirm_delete.html', {'student': student})


@login_required
def subject_list(request):
    """
    View to list all subjects.
    """
    subjects = Subject.objects.all()
    return render(request, 'dashboard/subject_list.html', {'subjects': subjects})


@login_required
def add_subject(request):
    """
    View to add a new subject.
    """
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added successfully.')
            return redirect('dashboard:subject_list')
    else:
        form = SubjectForm()
    return render(request, 'dashboard/subject_form.html', {'form': form, 'title': 'Add Subject'})


@login_required
def update_subject(request, subject_id):
    """
    View to update an existing subject.
    """
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully.')
            return redirect('dashboard:subject_list')
    else:
        form = SubjectForm(instance=subject)
    
    return render(request, 'dashboard/subject_form.html', {
        'form': form, 
        'title': 'Update Subject',
        'subject': subject
    })


@login_required
def delete_subject(request, subject_id):
    """
    View to delete a subject.
    """
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted successfully.')
        return redirect('dashboard:subject_list')
    
    return render(request, 'dashboard/subject_confirm_delete.html', {'subject': subject})


@login_required
def progress_sheet_list(request, student_id):
    """
    View to list all progress sheets for a specific student.
    """
    student = get_object_or_404(Student, id=student_id)
    progress_sheets = ProgressSheet.objects.filter(student=student).order_by('-exam_date', 'exam_type', 'subject__name')
    
    # Calculate totals and averages per exam type
    exam_summary = {}
    for sheet in progress_sheets:
        exam_type = sheet.exam_type
        if exam_type not in exam_summary:
            exam_summary[exam_type] = {
                'total_marks': 0,
                'max_marks': 0,
                'subjects_count': 0,
                'sheets': []
            }
        
        exam_summary[exam_type]['total_marks'] += float(sheet.marks_obtained)
        exam_summary[exam_type]['max_marks'] += float(sheet.max_marks)
        exam_summary[exam_type]['subjects_count'] += 1
        exam_summary[exam_type]['sheets'].append(sheet)
    
    # Calculate average percentage for each exam type
    for exam_type, data in exam_summary.items():
        if data['max_marks'] > 0:
            data['average_percentage'] = round((data['total_marks'] / data['max_marks']) * 100, 2)
        else:
            data['average_percentage'] = 0
    
    return render(request, 'dashboard/progress_sheet_list.html', {
        'student': student,
        'progress_sheets': progress_sheets,
        'exam_summary': exam_summary
    })


@login_required
def add_progress_sheet(request, student_id):
    """
    View to add a new progress sheet for a student.
    """
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = ProgressSheetForm(request.POST)
        if form.is_valid():
            progress_sheet = form.save(commit=False)
            progress_sheet.student = student
            progress_sheet.save()
            messages.success(request, 'Progress sheet added successfully.')
            return redirect('dashboard:progress_sheet_list', student_id=student.id)
    else:
        form = ProgressSheetForm(initial={'student': student})
    return render(request, 'dashboard/progress_sheet_form.html', {
        'form': form, 
        'title': 'Add Progress Sheet',
        'student': student
    })


@login_required
def update_progress_sheet(request, progress_sheet_id):
    """
    View to update an existing progress sheet.
    """
    progress_sheet = get_object_or_404(ProgressSheet, id=progress_sheet_id)
    
    if request.method == 'POST':
        form = ProgressSheetForm(request.POST, instance=progress_sheet)
        if form.is_valid():
            form.save()
            messages.success(request, 'Progress sheet updated successfully.')
            return redirect('dashboard:progress_sheet_list', student_id=progress_sheet.student.id)
    else:
        form = ProgressSheetForm(instance=progress_sheet)
    
    return render(request, 'dashboard/progress_sheet_form.html', {
        'form': form, 
        'title': 'Update Progress Sheet',
        'progress_sheet': progress_sheet
    })


@login_required
def delete_progress_sheet(request, progress_sheet_id):
    """
    View to delete a progress sheet.
    """
    progress_sheet = get_object_or_404(ProgressSheet, id=progress_sheet_id)
    student_id = progress_sheet.student.id
    
    if request.method == 'POST':
        progress_sheet.delete()
        messages.success(request, 'Progress sheet deleted successfully.')
        return redirect('dashboard:progress_sheet_list', student_id=student_id)
    
    return render(request, 'dashboard/progress_sheet_confirm_delete.html', {
        'progress_sheet': progress_sheet
    })


@login_required
def bulk_progress_sheet_entry(request):
    """
    View for bulk entry of progress sheets for a student across subjects for a specific exam type.
    """
    if request.method == 'POST':
        form = BulkProgressSheetForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            exam_type = form.cleaned_data['exam_type']
            exam_date = form.cleaned_data['exam_date']
            
            # Process each subject's marks
            total_marks = 0
            max_possible_marks = 0
            
            for field_name, value in form.cleaned_data.items():
                if field_name.startswith('marks_'):
                    subject_id = field_name.split('_')[1]  # Extract subject ID from field name
                    marks_field = f'marks_{subject_id}'
                    max_marks_field = f'max_marks_{subject_id}'
                    
                    marks = form.cleaned_data.get(marks_field)
                    max_marks = form.cleaned_data.get(max_marks_field)
                    
                    if marks is not None and max_marks is not None:
                        # Create or update progress sheet
                        ProgressSheet.objects.update_or_create(
                            student=student,
                            subject_id=subject_id,
                            exam_type=exam_type,
                            exam_date=exam_date,
                            defaults={
                                'marks_obtained': marks,
                                'max_marks': max_marks
                            }
                        )
                        
                        total_marks += float(marks)
                        max_possible_marks += float(max_marks)
            
            # Calculate and save exam result summary
            if max_possible_marks > 0:
                average_percentage = round((total_marks / max_possible_marks) * 100, 2)
                
                ExamResult.objects.update_or_create(
                    student=student,
                    exam_type=exam_type,
                    exam_date=exam_date,
                    defaults={
                        'total_marks': total_marks,
                        'max_possible_marks': max_possible_marks,
                        'average_percentage': average_percentage
                    }
                )
            
            messages.success(request, f'Progress sheets added for {student.full_name}.')
            return redirect('dashboard:progress_sheet_list', student_id=student.id)
    else:
        form = BulkProgressSheetForm()
    
    return render(request, 'dashboard/bulk_progress_sheet_form.html', {
        'form': form,
        'title': 'Bulk Progress Sheet Entry'
    })


@login_required
def student_ranking(request):
    """
    View to display student rankings based on exam scores with filtering options.
    """
    exam_type = request.GET.get('exam_type', 'quarterly')
    exam_types = [choice[0] for choice in ProgressSheet.EXAM_TYPE_CHOICES]
    
    # Validate exam_type
    if exam_type not in exam_types:
        exam_type = 'quarterly'
    
    # Get all students with their average scores for the selected exam type
    students_with_scores = []
    
    for student in Student.objects.all():
        # Get all progress sheets for this student and exam type
        sheets = ProgressSheet.objects.filter(
            student=student,
            exam_type=exam_type
        )
        
        if sheets.exists():
            # Calculate total marks and average percentage for this exam type
            total_marks = sum(float(sheet.marks_obtained) for sheet in sheets)
            max_marks = sum(float(sheet.max_marks) for sheet in sheets)
            
            if max_marks > 0:
                average_percentage = round((total_marks / max_marks) * 100, 2)
            else:
                average_percentage = 0
            
            students_with_scores.append({
                'student': student,
                'total_marks': total_marks,
                'max_marks': max_marks,
                'average_percentage': average_percentage,
                'subject_count': len(sheets)
            })
    
    # Sort students by average percentage in descending order (highest first)
    students_with_scores.sort(key=lambda x: x['average_percentage'], reverse=True)
    
    # Add rank to each student
    for i, record in enumerate(students_with_scores, start=1):
        record['rank'] = i
    
    context = {
        'students_with_scores': students_with_scores,
        'selected_exam_type': exam_type,
        'exam_types': exam_types,
    }
    
    return render(request, 'dashboard/student_ranking.html', context)