 

import datetime

from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.models import Author



def index(request):
	"""View function for home page of site."""
	num_books = Book.objects.all().count()
	num_instances = BookInstance.objects.all().count()
	num_instances_available = BookInstance.objects.filter(status__exact='a').count()
	num_authors = Author.objects.count()
	num_visits = request.session.get('num_visits', 0)
	request.session['num_visits'] = num_visits + 1
	
	context = {
	    'num_books' : num_books,
	    'num_instances' : num_instances,
	    'num_instances_available' : num_instances_available,
	    'num_authors' : num_authors,
	    'num_visits' : num_visits,
	}

	return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
	"""class-based generic list view(ListView)"""
	model = Book
	paginate_by = 2

class BookDetailView(generic.DetailView):
    model = Book
    paginate_by = 2

class AuthorListView(generic.ListView):
	"""class-based generic list view(ListView)"""
	model = Author
	paginate_by = 2

class AuthorDetailView(generic.DetailView):
    model = Author
    paginate_by = 2

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
	"""View function for renewing a specific BookInstance by librarian."""
	book_instance = get_object_or_404(BookInstance, pk=pk)

	if request.method == 'POST':
		#binding
		form = RenewBookForm(request.POST)

		if form.is_valid():
			book_instance.due_back = form.cleaned_data['renewal_date']
			book_instance.save()

			return HttpResponseRedirect(reverse('books'))

	else:
		proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
		form = RenewBookForm(initial={'renewal_date' : proposed_renewal_date})

	context = {
		'form' : form,
		'book_instance' : book_instance,
	}

	return render(request, 'catalog/book_renew_librarian.html', context)



#@permission_required('catalog.can_mark_returned')
class AuthorCreate(LoginRequiredMixin,CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': datetime.date.today() + datetime.timedelta(weeks=4170)}

class AuthorUpdate(LoginRequiredMixin,UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(LoginRequiredMixin,DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(LoginRequiredMixin,CreateView):
    model = Book
    fields = '__all__'

class BookUpdate(LoginRequiredMixin,UpdateView):
    model = Book
    fields = '__all__'

class BookDelete(LoginRequiredMixin,DeleteView):
    model = Book
    success_url = reverse_lazy('book-detail')

class AllLoanedBooksListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_allborrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')



'''
from django.forms import ModelForm

from catalog.models import BookInstance

class RenewBookModelForm(ModelForm): 
    def clean_due_back(self):
       data = self.cleaned_data['due_back']
       
       # Check if a date is not in the past.
       if data < datetime.date.today():
           raise ValidationError(_('Invalid date - renewal in past'))

       # Check if a date is in the allowed range (+4 weeks from today).
       if data > datetime.date.today() + datetime.timedelta(weeks=4):
           raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

       # Remember to always return the cleaned data.
       return data

    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': _('Renewal date')}
        help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).')}
'''

'''
https://medium.com/@leydsonvieira/utilizando-slug-baseado-em-uuid-nas-urls-do-django-f99abe44c424

Utilizando Slug baseado em UUID nas url’s do Django
Muitas vezes, desenvolvedores sentem-se desconfortáveis e inseguros ao exibir o id dos registros no momento das ações nas páginas da aplicação. Sempre há um espertinho que se dá conta do significado do número na url e tenta digitar outros id’s para acessar dados de outros registros. Certamente, isso não vai funcionar se o ambiente estiver bem configurado e seguro. Os dados não serão retornados se o registro acessado for diferente do que está com a sessão ativa. Porém, isso pode causar exceptions inesperadas e problemas na aplicação e deve ser evitado.
Slug
Estes são campos especiais para utilização em url’s. Slugs são, frequentemente, baseados em outros campos da classe.
Quando um campo texto ou uma string é transformada em um slug, os caracteres maiúsculos são convertidos para minúsculos, letras acentuadas perdem os acentos e os espaços são transformados em hifens. Por exemplo:
“Nome do usuário” => “nome-do-usuario”
Com isso, é muito comum em blogs, por exemplo, ser possível visualizar um slug do nome do post na url.

No Django, um campo do tipo slug é criado na model desta maneira:

class Usuario(models.Model):
    """
       Classe com campo slug.
    """
    id = models.AutoField(
        primary_key=True
    )

    slug = models.SlugField(
            max_length=150,
            unique=True,
            default='page-slug'
    )

Universally Unique Identifier
Os UUIDs são números utilizados para identificação de qualquer coisa no mundo da computação. Com o tamanho de 128 bits, é praticamente impossível que exista uma duplicidade entre dois UUIDs.
Esses números são formados por 16 octetos que são representados por 32 dígitos hexadecimais minúsculos apresentados em 5 grupos separados por hifens no formato:
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
123e4567-e89b-12d3-a456-426655440000
Atribuindo um UUID ao campo slug da sua model
Para utilizar UUID no Python, é necessário fazer o import do módulo uuid:
import uuid
De acordo com a documentação oficial:
21.20. uuid - UUID objects according to RFC 4122 - Python 3.6.1rc1 documentation

Create a UUID from either a string of 32 hexadecimal digits, a string of 16 bytes as the bytes argument, a string of 16…
docs.python.org	
Após importar o módulo, sobrescreva o método ‘save()’ da sua classe para atribuir um UUID aleatório ao campo ‘slug’ da instância:

def save(self, **kwargs):
    ''
    Sobrescreve o método save da classe alterando o slug da instância e atribuindo um UUID (Universal Unique Identifier).
    ''
    if not self.id:
        self.slug = uuid.uuid4()
    super().save(**kwargs)

uuid4 é uma função que gera um uuid aleatoriamente. Existem outras que podem ser utilizadas também dentro do módulo.
Note no código acima que uma condição foi escrita de forma que o UUID só seja atribuído ao campo slug, se o campo id do objeto não existir. Essa é a grande sacada! O UUID só será gerado na criação do usuário. Caso haja um update (que também utiliza o método save() para gravar os dados no banco) o identificador gerado na criação é preservado, assim evitando problemas de duplicidade.
URL
Agora basta ajustar suas URLs para, ao invés da primary key do registro, enviar o slug no grupo nomeado da expressão regular.

from django.conf.urls import url
from usuario import views

urlpatterns = [
    url(r'^cadastro/$',views.UsuarioCreateView.as_view(), name='cadastro' ),

    url(r'^editar/(?P<slug>[-\w\W\d]+)/$',views.UsuarioUpdateView.as_view(), name='editar_cadastro'),

    url(r'^senha/(?P<slug>[-\w\W\d]+)/$',views.PasswordChangeView.as_view(), name='senha'),

    url(r'^excluir/(?P<slug>[-\w\W\d]+)/$',views.UsuarioDeleteView.as_view(), name='excluir_cadastro')
]

Também alterar os links dos templates para acessarem essas urls usando como parâmetro o slug e não o id do registro:

href="{% url 'usuario:editar_cadastro' user.slug %}"

Acho essa, uma forma muito interessante de navegar pela sua aplicação de forma segura e limpa.
'''


