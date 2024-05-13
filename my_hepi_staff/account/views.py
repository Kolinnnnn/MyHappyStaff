from typing import Any

from django.http import JsonResponse
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy 
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from .models import Account, Employee, Employer, Project, Competence
from .forms import CompetenceEnrollForm, GroupedTableForm, ProjectForm


class DashboardView(TemplateView):
    template_name = 'account/dashboard.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        return render(request, self.template_name, context=context)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data()

        user_id = self.request.user.id
        context['account'] = Account.objects.get(user_id=user_id)

        if context['account'].is_employee:
            context['employee'] = Employee.objects.get(account_id=context['account'].id)
            context['competences_groups'] = self._get_sorted_comptences_groups_and_competences_(context['employee'])

        return context
    
    def _get_sorted_comptences_groups_and_competences_(self, employee: Employee) -> dict[str, Any]:
        competences = employee.competences.all()
        result = {}

        for competence in competences:
            key = competence.competence_group.name

            if key not in result:
                result[key] = []

            result[key].append(competence.name)
        
        return result
    

class EmployeeAboutMeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    fields = ['description']
    template_name = 'account/employee/aboutme_update_form.html'
    

class EmployeeCompetenceView(LoginRequiredMixin, FormView):
    template_name = 'account/employee/competence.html'
    form_class = CompetenceEnrollForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        competences = form.cleaned_data['competence']

        account = Account.objects.get(user_id=self.request.user.pk)
        employee = Employee.objects.get(account_id=account.pk)

        # Clear existing competences
        employee.competences.clear()

        # Add selected competences
        for competence in competences:
            employee.competences.add(competence)

        return super().form_valid(form)
    

class ProjectView(TemplateView):
    template_name = 'account/employer/project/list.html'

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context=context)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data()

        user_id = self.request.user.id
        context['account'] = Account.objects.get(user_id=user_id)

        if context['account'].is_employer:
            employer = Employer.objects.get(account_id=context['account'].pk)
            context['projects'] = Project.objects.filter(employer_id=employer.pk)

        return context
    

class ProjectCreateView(CreateView, LoginRequiredMixin):
    model = Project
    form_class = ProjectForm
    template_name = 'account/employer/project/form.html'

    def form_valid(self, form):
        project = form.save(commit=False)
        project.employer = Employer.objects.get(account_id=self.request.user.account.pk)
        project.save()

        employees = self.request.POST.getlist('employees')  # Pobierz listę wybranych pracowników z formularza
        project.employees.set(employees)  # Przypisz wybranych pracowników do projektu

        return redirect("project-list")
    

class ProjectUpdateView(UpdateView, LoginRequiredMixin):
    model = Project
    form_class = ProjectForm
    template_name = 'account/employer/project/form.html'


class ProjectDeleteView(DeleteView, LoginRequiredMixin):
    model = Project
    success_url = reverse_lazy('project-list')
    template_name = 'account/employer/project/confirm_delete.html'
    context_object_name = 'project'


class EmployerEmployeesView(TemplateView, LoginRequiredMixin):
    template_name = 'account/employer/employee/list.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context=context)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        user_id = self.request.user.id
        context['account'] = Account.objects.get(user_id=user_id)

        if context['account'].is_employer:
            context['employees'] = Employee.objects.all()

        return context


class EmployeeBelbinTest(View):
    template_name = 'account/employee/belbinTest.html'

    questions = [
        {
            'name': 'Część I: Sądzę, że osobiście wnoszę do grupy...',
            'questions': [
                'Wydaje mi się, że szybko dostrzegam i umiem wykorzystać nowe możliwości ',
                'Mogę dobrze pracować z bardzo różnymi ludźmi',
                '"Produkowanie" pomysłów to moja naturalna zdolność',
                'Moja siła tkwi w tym, że potrafię z ludzi "wyciągnąć" to, co mają w sobie najlepszego, aby przyczynili się do osiągnięcia celów i zadań grupowych',
                'Moja główna umiejętność polega na doprowadzaniu spraw do końca i wiąże się z efektywnością',
                'Jestem w stanie przez jakiś czas zaakceptować niepopularność mojej osoby, jeśli prowadzi to do wartościowych wyników',
                'Zwykle wyczuwam, co jest realistyczne i prawdopodobne, jeśli chodzi o osiągniecie sukcesu',
                'Zwykle mogę zaproponować jakieś alternatywne wyjście bez uprzedzeń i niechęci'
            ]
        },
        {
            'name': 'Część II: Jeśli mam jakieś niedociągnięcia w pracy grupowej to dlatego, że...',
            'questions': [
                'Nie mogę się uspokoić, dopóki narada nie jest uporządkowana, kontrolowana i ogólnie dobrze prowadzona',
                'Mam skłonność do bycia wspaniałomyślnym dla tych, których przekonujące pomysły nie zostały odpowiednio przemyślane',
                'Mam skłonność do gadulstwa, gdy grupa rozpracowuje nowe pomysły',
                'Mój chłodny ogląd spraw utrudnia mi przyłączenie się do gotowości i entuzjazmu kolegów',
                'Czasami jestem spostrzegany jako wywierający nadmierny nacisk i autorytatywny wpływ, jeśli coś musi zostać rzeczywiście zrobione',
                'Trudno mi kierować "na pierwszej linii", gdyż czuję się zbyt odpowiedzialny za atmosferę grupową',
                'Mam skłonność do rozmyślania o tym, co w danej chwili wpada mi do głowy, przez co tracę kontakt z tym, co się dzieje',
                'Koledzy widzą mnie jako niepotrzebnie przejmującego się szczegółami i możliwością, że sprawy mogą się źle ułożyć'
            ]
        },
        {
            'name': 'Część III: Gdy jestem wciągnięty razem z innymi w przygotowanie projektu...',
            'questions': [
                'Mam skłonność do wywierania wpływu na ludzi, lecz bez wywierania na nich presji',
                'Moja czujność pozwala zapobiegać wielu pomyłkom i błędom',
                'Jestem gotów kłaść nacisk na działanie, aby upewnić się, że narada nie jest stratą czasu lub, że prowadzi do utracenia z widoku głównego celu',
                'Zwykle można na mnie polegać, że wymyślę coś oryginalnego',
                'Zawsze jestem gotów uczynić dobrą sugestię przedmiotem zainteresowania całej grupy',
                'Zawsze poszukuję ostatnich nowinek, nowych odkryć i wyników badań na określony temat',
                'Mam przekonanie, że moja umiejętność wydawania sądu może pomóc w podjęciu odpowiednich ',
                'Moją specjalnością jest zorganizowanie najbardziej znaczącej części pracy'
            ]
        },
        {
            'name': 'Część IV: Moją charakterystyczną cechą w pracy grupowej jest...',
            'questions': [
                'Rzeczywiście interesuję się bliższym poznaniem moich kolegów',
                'Nie mam oporów przed przeciwstawianiem się zdaniu większości',
                'Zwykle potrafię przyjąć taką linię argumentacji, aby obalić błędny punkt widzenia',
                'Sądzę, że mam szczególny talent do wprowadzania pomysłów w życie, gdy plan ma być zastosowany',
                'Mam skłonność do unikania tego, co oczywiste i do zaskakiwania czymś niespodziewanym',
                'Doprowadzam to, czego się podejmę do perfekcji',
                'Jestem gotów do nawiązywania i wykorzystywania kontaktów pozagrupowych, jeśli jest to potrzebne',
                'Nawet jeśli interesuje mnie wiele aspektów sprawy, nie mam problemów z podjęciem decyzji co do wyboru rozwiązania'
            ]
        },
        {
            'name': 'Część V: Czerpię satysfakcję z pracy, gdyż...',
            'questions': [
                'Cieszy mnie analizowanie sytuacji i rozważanie możliwości wyboru',
                'Interesuje mnie znalezienie praktycznych rozwiązań problemów',
                'Lubię mieć przekonanie, że sprzyjam kształtowaniu dobrych kontaktów międzyludzkich w pracy',
                'Lubię mieć duży wpływ na decyzje',
                'Cieszę się z kontaktów z ludźmi, którzy mają coś nowego do zaoferowania',
                'Jestem w stanie doprowadzić do zgody w ważnych dla pracy sprawach',
                'Wczuwam się w moją część zadania, jeśli pragnę poświęcić zadaniu całą swoją uwagę ',
                'Lubię znaleźć taki obszar, który pobudza moja wyobraźnię'
            ]
        },
        {
            'name': 'Część VI: Jeśli nagle otrzymuję trudne zadanie do wykonania w ograniczonym czasie i wobec nieznanych mi osób...',
            'questions': [
                'Mam ochotę zaszyć się w kącie, aby wymyślić sposób na wyjście z impasu',
                'Byłbym gotów do współpracy z osobą, która wykazała najbardziej pozytywne nastawienie',
                'Znalazłbym sposób na zmniejszenie skali zadania prze ustalenie, co mogłyby zrobić poszczególne jednostki',
                'Moje naturalne wyczucie spraw pilnych pozwoli na postępowanie zgodnie z planem',
                'Z pewnością zachowam spokój i zdolność do trzeźwego osądu',
                'Mimo nacisków zachowam stałość celu',
                'Byłbym przygotowany do przejęcia konstruktywnego kierownictwa, jeśli stwierdziłbym, że grupa nie robi postępu',
                'Zainicjowałbym dyskusję w celu stymulowania nowych pomysłów, rozwiązań'
            ]
        },
        {
            'name': 'Część VII: W odniesieniu do problemów, za które jestem w grupie odpowiedzialny...',
            'questions': [
                'Mam skłonność do ujawniania niezadowolenia wobec tych, którzy moim zdaniem przeszkadzają w osiąganiu postępów',
                'Inni mogą mnie krytykować za to, że jestem analityczny i niedostatecznie opieram się na intuicji',
                'Moje pragnienie, aby praca została starannie wykonana, może wstrzymywać pójście do przodu',
                'Mam skłonność do nudzenia się i oczekuję, że inni będą mnie stymulować i "zapalać"',
                'Trudno mi rozpocząć, jeśli cele nie są dla mnie  jasne',
                'Czasami nie jestem tak efektywny, jak bym chciał, jeśli chodzi o wyjaśnienie złożonych problemów, jakie przede mną stoją',
                'Mam świadomość, że wymagam od innych rzeczy, których sam nie mogę zrobić',
                'Waham się, gdy należałoby przeforsować mój punkt widzenia, gdy mam do czynienia z jawną opozycją'
            ]
        }
    ]

    answers_sum_mapping = [
        {
            'name': 'PO',
            'mapping': [[1, 7], [2, 1], [3, 8], [4, 4], [5, 2], [6, 6], [7, 5]],
            'sum': 0
        },
        {
            'name': 'NL',
            'mapping': [[1, 4], [2, 2], [3, 1], [4, 8], [5, 6], [6, 3], [7, 7]],
            'sum': 0
        },
        {
            'name': 'CZA',
            'mapping': [[1, 6], [2, 5], [3, 3], [4, 2], [5, 4], [6, 7], [7, 1]],
            'sum': 0
        },
        {
            'name': 'SIE',
            'mapping': [[1, 3], [2, 7], [3, 4], [4, 5], [5, 8], [6, 1], [7, 6]],
            'sum': 0
        },
        {
            'name': 'CZK',
            'mapping': [[1, 1], [2, 3], [3, 6], [4, 7], [5, 5], [6, 8], [7, 4]],
            'sum': 0
        },
        {
            'name': 'SĘ',
            'mapping': [[1, 8], [2, 4], [3, 7], [4, 3], [5, 1], [6, 5], [7, 2]],
            'sum': 0
        },
        {
            'name': 'CZG',
            'mapping': [[1, 2], [2, 6], [3, 5], [4, 1], [5, 3], [6, 5], [7, 8]],
            'sum': 0
        },
        {
            'name': 'PER',
            'mapping': [[1, 5], [2, 8], [3, 2], [4, 6], [5, 7], [6, 4], [7, 3]],
            'sum': 0
        }
    ]

    def get(self, request):
        return render(request, self.template_name, {
            'form': GroupedTableForm(grouped_questions=self.questions),
            'account': Account.objects.get(user_id=request.user.id)
        })

    def post(self, request):
        form = GroupedTableForm(request.POST, grouped_questions=self.questions)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            fields_with_values = {}
            for field_name, field_value in cleaned_data.items():
                fields_with_values[field_name] = field_value

            score_ranges = {
            'PO': {'sredni': (9, 13), 'wysoki': (14, 18), 'bardzo wysoki': (19, float('inf'))},
            'NL': {'sredni': (5, 8), 'wysoki': (9, 12), 'bardzo wysoki': (13, float('inf'))},
            'CZA': {'sredni': (10, 14), 'wysoki': (15, 20), 'bardzo wysoki': (21, float('inf'))},
            'SIE': {'sredni': (4, 7), 'wysoki': (8, 11), 'bardzo wysoki': (12, float('inf'))},
            'CZK': {'sredni': (6, 9), 'wysoki': (10, 13), 'bardzo wysoki': (14, float('inf'))},
            'SĘ': {'sredni': (7, 11), 'wysoki': (12, 16), 'bardzo wysoki': (17, float('inf'))},
            'CZG': {'sredni': (5, 10), 'wysoki': (11, 15), 'bardzo wysoki': (16, float('inf'))},
            'PER': {'sredni': (8, 13), 'wysoki': (14, 19), 'bardzo wysoki': (20, float('inf'))},
            }   
            min_score = 0
            roles_above_min_score = []
            roles_with_levels = []

            for item in self.answers_sum_mapping:
                item['sum'] = 0
                for m in item['mapping']:
                    item['sum'] += fields_with_values['group_' + str(m[0]) + '_question_' + str(m[1])]

                role_name = item['name']
                score = item['sum']

                level = ''
                for level_name, range_values in score_ranges[role_name].items():
                    if range_values[0] <= score <= range_values[1]:
                        level = level_name
                        break
                
                if level: 
                    roles_with_levels.append((role_name, level))


            max_sum_name = max(self.answers_sum_mapping, key=lambda x: x['sum'])['name']
            account = Account.objects.get(user_id=self.request.user.pk)
            employee = Employee.objects.get(account_id=account.pk)
            employee.belbin_test_result = ', '.join([f"{role}{'*' if level == 'bardzo wysoki' else '^' if level == 'wysoki' else ''}" for role, level in roles_with_levels])
            employee.save()

            return redirect("dashboard")

        return render(request, self.template_name, {
            'form': form,
            'account': Account.objects.get(user_id=request.user.id)
        })
