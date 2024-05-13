from django import forms

from account.models import Project, Employee
from competence.models import Competence


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class CompetenceEnrollForm(forms.Form):
    competence = forms.ModelMultipleChoiceField(queryset=Competence.objects.all(), 
                                        widget=forms.CheckboxSelectMultiple,
                                        label='')


class AboutMeForm(forms.Form):
    description = forms.Textarea()


class GroupedTableForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.grouped_questions = kwargs.pop('grouped_questions', [])
        super(GroupedTableForm, self).__init__(*args, **kwargs)
        for idx, group in enumerate(self.grouped_questions):
            group_name = group.get('name')
            questions = group.get('questions')
            self.fields[f'group_{idx+1}'] = forms.CharField(label=group_name, widget=forms.HiddenInput(), required=False)
            for q_idx, question in enumerate(questions):
                self.fields[f'group_{idx+1}_question_{q_idx+1}'] = forms.IntegerField(label=question, initial=0)

    def clean(self):
        cleaned_data = super().clean()
        for group_idx, group in enumerate(self.grouped_questions):
            sum_of_group = sum(cleaned_data[f'group_{group_idx + 1}_question_{q_idx + 1}'] for q_idx in range(len(group['questions'])))
            if sum_of_group != 10:
                self.add_error(f'group_{group_idx + 1}', f"The sum of the fields in '{group['name']}' must equal 10.")


class ProjectForm(forms.ModelForm):
    competences = forms.ModelMultipleChoiceField(queryset=Competence.objects.all(), required=True)
    employees = forms.ModelMultipleChoiceField(queryset=Employee.objects.all(), required=True)

    class Meta:
        model = Project
        fields = ['code', 'title', 'description', 'competences', 'employees']

    
    
