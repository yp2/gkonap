class ResponseConvert (Response) :
	'''Obiekt odpowiedzi dla pluginów convert
'''
	def __init__(self) :
		self.context = convert # str
		pass
class WorkerConvert (Worker) :
	'''Worker dla pluginów convert'''
	def __init__(self) :
		pass
class Subtitle :
	'''Klasa określająca napisy rozłożone do standardowego formatu - poszczególne linie napisów - obiekt SubLine - znajdują się w atrybucie lines - lista zawierająca ułożne w kolejności poszczególne linie napisów w postacji Subline.'''
	def __init__(self) :
		self.lines = None # list
		pass
	def append (self, subline) :
		""" Metoda do dodawania do atr. lines - kolejnej linii w postaci obiektu SubLine. Działanie jak append typu list.
@subline - obiekt SubLine """
		# returns 
		pass
class SubLine :
	'''Obiekt będący reprezentacją poszczególnych linii napisów w postaci standardowej.
Posiada następujące atrybuty:
start: Decimal - czas pojawienia się napisów
stop: Decimal - czas kiedy napisy przestają być wyświetlane
data: str - właściwe napisy'''
	def __init__(self) :
		self.start = None # Decimal
		self.stop = None # Decimal
		self.data = None # str
		pass
	def set_start (self, time) :
		""" Metoda do ustawiania atr. start na czas w formacie standardowym w postaci obiektu Decimal """
		# returns 
		pass
	def set_stop (self, time) :
		""" Metoda do ustawiania atr. stop na czas w formacie standardowym w postaci obiektu Decimal """
		# returns 
		pass
	def set_data (self, data) :
		""" Metoda do ustawiania atr. data w postraci typu str - linia napisów po przekształceniu na standardowy format. """
		# returns 
		pass
	def get_start (self) :
		""" Metoda pobiera wartość atr. start. """
		# returns Decimal
		pass
	def get_stop (self) :
		""" Metoda pobiera wartość atr. stop. """
		# returns Decimal
		pass
	def get_data (self) :
		""" Metoda pobiera wartość atr. data. """
		# returns str
		pass
class Worker :
	'''Ogólny interface dla robotników wykorzustujących pluginy do wykonywania zadań zleconych przez aplikację
'''
	def __init__(self) :
		pass
class ResponsFactory :
	'''Fabryka obiektów Response na potrzeby różnych elemementów systemu. 
Zwaraca obiekty Response w zależności od kontekstu (części aplikacji).
Przetrzymuje słownik zawierający jako klucz kontekst a wartość referencje do odpowiedniej klasy.
@responses - słownik zwierający kontekst i odpiwednią klase response.
Jeżeli danej odpowiedzi nie ma klasa zwraca ogólny obiekt response'''
	def __init__(self) :
		self.responses = None # dict
		pass
	def get_respons (self, context) :
		""" Metoda zwraca obiekt response w zależności od podanego kontekstu. Jeżeli nie ma takiego kontekstu zwraca ogólną postać odpowiedzi.  """
		# returns Response
		pass
class PluginConvert :
	'''klasa abstrakcyjna -> __metaclass__ = abc.ABCMeta; dla pluginów kowertujących napisy. '''
	def __init__(self) :
		pass
	def set (self, file_lines) :
		""" Metoda do ustawiania danych potrzebnych pluginowi do dekompozycji napisów na standardowy format. Dane to wczytany plik z liniami po readlines

file_lines - wczytany plik w postaci listy linii z open().readlines """
		# returns 
		pass
	def recognize (self) :
		""" Tu trzeba się zastanowić jak to wykonać - czy zawansowana implementacja w metodzie czy też może zwracanie jakieś klasy która to wykona ??? """
		# returns 
		pass
	def get_decompose_subtitle (self) :
		""" Zastanowić się co zwraca może jakiś obiekt który będzie miał dane oraz w razie błędu informacje o błedzie (wyjątek) - jeżeli tak to potrzebny jest zbiór wyjątków 

Zwaraca klase Subtitle zawirającą SubLine'y przekonwertowane do standardowego fotmatu """
		# returns Response (list)
		pass
	def get_compose_subtitle (self) :
		""" Zastanowić się co zwraca może jakiś obiekt który będzie miał dane oraz w razie błędu informacje o błedzie (wyjątek) - jeżeli tak to potrzebny jest zbiór wyjątków 

Funkcja zwaraca listę zawierającą linie po konwersji do zapisuj właściowego pliku w postaci dla open().writelines """
		# returns Response (list)
		pass
	def get_supported_filetypes (self) :
		""" Zwaraca listę obsługiowanych plików przez plugin - lista rozszeżeń czyli ".txt", ".srt" ... """
		# returns Response (list)
		pass
	def set_decompose_subtitle (self, subtitle) :
		""" Metoda przyjumje obiekt Subtitle zawierający SubLine's - napisy rozłożone do formatu standarodwego gotowego do kompozycji. Bez tego kroku nie można przekonwertować właściwych napisów na określony przez plugin typ. """
		# returns 
		pass
class Response :
	'''Obiekt odpowiedzi zwracany przez pluginy. Zwracany jest on w odpowiedzi na zapytania, żadania wykonania pracy. Attr:
success: bool;
exceptions: list - lista wyjątków gdy praca/zadanie nie zostało wykonane nie powiodło się
log: list - lista zawierająca ewentualny zapis pracy poszczególnych metod - nie jest to obowiązkowe
data: typ zależny od pluginu / wykonanego zadania. Dane są obecne gdy praca się powiodła, jeżeli praca nie została wykonana nie ma żadnych danych.'''
	def __init__(self) :
		self.success = None # bool
		self.execeptions = None # list
		self.log = None # list
		self.data = None # data
		pass
	def get_success (self) :
		""" Zwaraca warotść bool powodzenia wykonania pracy """
		# returns bool
		pass
	def get_exceptions (self) :
		""" Zwraca listę wyjątków, dodoanych gdy praca się nie udała """
		# returns list
		pass
	def get_log (self) :
		""" Zwaraca listę zawirającą str logów, nieobowiązkowe """
		# returns list
		pass
	def get_data (self) :
		""" Zawraca dane otrzymane podczas wykonywanej pracy lub brak gdy praca nie została wykonana. """
		# returns data
		pass
	def print_log (self) :
		""" drukuje logi """
		# returns 
		pass
	def print_exceptions (self) :
		""" drukuje wyjątki oraz ich opisy """
		# returns 
		pass
	def set_success (self, state) :
		""" ustawia succes wykonanej pracy """
		# returns 
		pass
	def append_log (self, log_line) :
		""" dodaje pojedyńczy log do attr log """
		# returns 
		pass
	def set_data (self, data) :
		""" ustawia attr data na typ zależny od pluginu oraz pracy """
		# returns 
		pass
	def append_exception (self, exception) :
		""" dodaje do attr exception wyjątek """
		# returns 
		pass
class ResponseSubDownload (Response) :
	'''Obiekt odpowiedzi dla pluginów SubDownload
'''
	def __init__(self) :
		self.context = subdownload # str
		pass
