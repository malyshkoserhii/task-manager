from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from tasks.models import Task, TaskType
from tasks.constants.choices import Priority, TaskStatus


class TaskCreateForm(forms.ModelForm):
    task_type = forms.ModelChoiceField(
        queryset=TaskType.objects.all(),
        required=False,
        empty_label="Select task type",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "status",
            "assignees",
            "deadline",
            "priority",
        ]
        widgets = {
            "deadline": forms.DateTimeInput(
                attrs={
                    "type": "text",
                    "onfocus": "this.type='datetime-local'; "
                    "try { this.showPicker(); } catch(e) {}",
                    "onclick": "try { this.showPicker(); } catch(e) {}",
                    "onblur": "if(!this.value) this.type='text'",
                    "class": "border border-gray-200 rounded-xl "
                    "px-3 py-2 text-sm bg-white "
                    "focus:border-indigo-500 focus:ring-indigo-500 "
                    "cursor-pointer w-full",
                    "placeholder": "Select deadline date and time",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Describe the task...",
                    "class": "form-control",
                }
            ),
            "name": forms.TextInput(
                attrs={"placeholder": "Task name", "class": "form-control"}
            ),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "project": forms.Select(attrs={"class": "form-select"}),
            "assignees": forms.CheckboxSelectMultiple(attrs={"class": "form-select"}),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data["deadline"]
        today = timezone.now()

        if not deadline:
            return deadline

        if deadline < today:
            raise forms.ValidationError("Deadline cannot be less than current time.")
        return deadline


class TaskSearchForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search tasks by name...",
                "class": "w-full pl-10 pr-4 py-2 border border-gray-200 "
                "rounded-xl focus:border-indigo-500 focus:ring-indigo-500 "
                "text-sm bg-white",
            }
        ),
    )
    priority = forms.ChoiceField(
        choices=[("", "All Priorities")] + Priority.choices,
        required=False,
        label="",
        widget=forms.Select(
            attrs={
                "class": "border border-gray-200 rounded-xl px-3 py-2 text-sm "
                "bg-white focus:border-indigo-500 focus:ring-indigo-500 "
                "cursor-pointer"
            }
        ),
    )
    assignee = forms.ModelChoiceField(
        queryset=get_user_model().objects.all(),
        required=False,
        empty_label="All Assignees",
        label="",
        widget=forms.Select(
            attrs={
                "class": "border border-gray-200 rounded-xl px-3 py-2 text-sm bg-white "
                "focus:border-indigo-500 focus:ring-indigo-500 cursor-pointer"
            }
        ),
    )
    status = forms.ChoiceField(
        choices=[("", "All Statuses")] + [(s.value, s.label) for s in TaskStatus],
        required=False,
        label="",
        widget=forms.Select(
            attrs={
                "class": "border border-gray-200 rounded-xl px-3 py-2 text-sm bg-white "
                "focus:border-indigo-500 focus:ring-indigo-500 cursor-pointer"
            }
        ),
    )
    task_type = forms.ModelChoiceField(
        queryset=TaskType.objects.all(),
        required=False,
        empty_label="All Task Types",
        label="",
        widget=forms.Select(
            attrs={
                "class": "border border-gray-200 rounded-xl px-3 py-2 text-sm bg-white "
                "focus:border-indigo-500 focus:ring-indigo-500 cursor-pointer"
            }
        ),
    )
    deadline = forms.ChoiceField(
        choices=[
            ("", "Sort by deadline..."),
            ("deadline_asc", "Closest Deadline First 🗓️"),
            ("deadline_desc", "Furthest Deadline First ⏳"),
        ],
        required=False,
        label="",
        widget=forms.Select(
            attrs={
                "class": "border border-gray-200 rounded-xl px-3 py-2 text-sm bg-white "
                "focus:border-indigo-500 focus:ring-indigo-500 cursor-pointer"
            }
        ),
    )
    created_at = forms.ChoiceField(
        choices=[
            ("", "Sort by created at..."),
            ("created_at_asc", "Oldest First 🗓️"),
            (
                "created_at_desc",
                "Newest First ⏳",
            ),
        ],
        required=False,
        label="",
        widget=forms.Select(
            attrs={
                "class": "border border-gray-200 rounded-xl px-3 py-2 text-sm bg-white "
                "focus:border-indigo-500 focus:ring-indigo-500 cursor-pointer"
            }
        ),
    )
