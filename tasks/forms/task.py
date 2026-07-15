from django import forms

from tasks.models import Task


class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "status",
            "assignees",
            "deadline",
            "priority",
            "task_type",
        ]
        widgets = {
            "deadline": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Describe the task...", "class": "form-control"}
            ),
            "name": forms.TextInput(attrs={"placeholder": "Task name", "class": "form-control"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "project": forms.Select(attrs={"class": "form-select"}),
            "task_type": forms.Select(attrs={"class": "form-select"}),
            "assignees": forms.CheckboxSelectMultiple(attrs={"class": "form-select"}),
        }
