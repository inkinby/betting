import time
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import Request, urlopen
from json import JSONEncoder

# import cgi, cgitb 
# import xml.dom.minidom
# from lxml import etree
# import lxml.html as html


# прикидываемся браузером
headers = {'accept-ranges': 'bytes', 
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}

# ссылка для проверки
base_url = 'https://www.marathonbet.by/su/betting/11?periodGroupAllEvents=24'

all_events = []	
hiscore=[]
number=[]
sobitie=[]
number_title=[]
time_period_print = []


def mb_parse(base_url,headers):

	session = requests.Session()	# открываем сессию с сервером
	request = session.get(base_url, headers=headers )	# запрос по url

	if request.status_code == 200:  # проверяем ответ сервера, если 200 (ОК) выполняем запрос страницы №*
				
		time_period = 12		# События за 2ч = 2, 6ч = 6, 12ч = 12, 24ч = 24, всё вермя = 0 
		time_period_print.append(time_period)	# вынести на верх из функции

		# запрос на 1 и 2 страницы

		url = 'https://www.marathonbet.by/su/betting/11?'	# футбол = 11, хоккей = 537
		params = {'periodGroupAllEvents': time_period,'pageAction': 'default'}	
		request2 = session.get(url=url, params=params)
		request2_json = request2.json()
		request2_json_str = str(request2_json[0])
		request2_json_str_norm = request2_json_str[1:-2]	# обрезаем края у str json ответа 
		all_events.append(request2_json_str_norm)	# добавляем полученую страницу в список

		# запрос на 3 и остальные страницы

		for page_namber in range(3,10):
			url = 'https://www.marathonbet.by/su/betting/11?'
			params = {'periodGroupAllEvents': time_period, 'page': page_namber,'pageAction': 'getPage'}
			request3 = session.get(url=url, params=params)
			request3_json = request3.json()
			request3_json_str = str(request3_json[0])
			request3_json_str_norm = request3_json_str[66:-2]
			all_events.append(request3_json_str_norm)

		all_events_str = str(all_events).strip('[]')	# список всех страниц в строку для супа
		soup = bs(all_events_str,'html.parser')
		divs = soup.find_all('div', attrs={'class': 'category-container'})	# парсим данные div category-container
		number.append(len(divs))	# количество найденых div category-container

		for div0 in divs:
			title = div0.find_all('div', attrs={'class': 'bg coupon-row'})
			number_title.append(len(title))
			for div1 in title:
				title2 = div1.find('tr', attrs={'class': 'sub-row'}).text
				hiscore2 = title2.split()
				hiscore.append(hiscore2)	# все найденые события в список
	else:
		print("ERROR")


mb_parse(base_url,headers)

print('')
print('		Событие и коэффициенты: [1], [X], [2], [1X], [12], [X2]')

# вилка коэффициентов
stavka2_3min=1.170	# значение коэффициента [1] от...
stavka2_3max=1.300	# значение коэффициента [1] ...до
stavka3_2min=8.300	# значение коэффициента [2] от...
stavka3_2max=20.000	# значение коэффициента [2] ...до

stavki_all=[]
index_plus=[]
index_plus_short={}

scores2 = list(map(int, number_title))

# функция check_koeff принимает значения event_name_join (имя события) и event_koeff (коэфф этого события) 
# от функции iterate_str

def check_koeff(event_name_join,event_koeff):
	print(event_name_join,':',event_koeff)
	index_koeff_1=event_koeff[0]
	# пробуем преобразовать значение коэффициента1 во float, если нет то коэф1=0
	try:
		value_index_koeff_1=float(event_koeff[0])
	except ValueError:
		value_index_koeff_1=0
	index_koeff_2=event_koeff[2]
	# пробуем преобразовать значение коэффициента2 во float, если нет то коэф2=0
	try:
		value_index_koeff_2=float(event_koeff[2])
	except ValueError:
		value_index_koeff_2=0

	# фильтруем событая с нужной вилкой коэффициентов, если соответствует, добавляем в словарь
	if stavka2_3min <= value_index_koeff_1 <= stavka2_3max:
			print('первый коэфф норм, проверяем второй коэфф')
			if stavka3_2min <= value_index_koeff_2 <= stavka3_2max:
				print('два коэффа норм, БЕРЁМ СТАВКУ!!!')
				index_plus_short[event_name_join]=event_koeff
			else:
				print('Не соответствует')
	else:
		if stavka2_3min <= value_index_koeff_2 <= stavka2_3max:
			print('второй коэфф норм, проверяем первый коэфф')
			if stavka3_2min <= value_index_koeff_1 <= stavka3_2max:
				print('два коэффа норм, БЕРЁМ СТАВКУ!!!')
				index_plus_short[event_name_join]=event_koeff
			else:
				print('Не соответствует')


number_str=number[0]
# n= количество индексов событий начиная с 0
n=number_str-1


# функция принимает значения (список) и перебирает в нём столбцы
def iterate_str(eventos):
	m=eventos
#   ищем '+' в списке с 0 до b (b=len(eventos))
	b=12
	for v in range(b):
		text = m[v]
		text2 = '+'
		indexs = [i for i, symb in enumerate(text) if symb==text2]
#       если '+' есть, то всё что до первого '+' это имя события, остальные 6 столбцов это [1], [X], [2], [1X], [12], [X2]
		if len(indexs) == 1:
			index_plus.append(v)
			# имя события все ячейки до '+'
			event_name=m[:v]
			# коэффициенты 6 ячеек после '+'
			event_koeff=m[v+1:v+7]
			event_name_join=' '.join(event_name)
			check_koeff(event_name_join,event_koeff)

n=len(hiscore)


# функция перебора списков из hiscore и передачи этих списков в iterate_str
def append_eventos():
	for xx in range(n):
		eventos = hiscore[xx]
		iterate_str(eventos)


append_eventos()
length = len(index_plus_short)

print("")
print('		В БЛИЖАЙШИЕ',time_period_print,'ЧАСОВ НАЙДЕНО СОБЫТИЙ:',sum(scores2), )
print("")
print('		ИЩЕМ СОБЫТИЯ С КОЭФФИЦИЕНТАМИ') 
print('		',stavka2_3min, '...',stavka2_3max, ' - ',stavka3_2min, '...',stavka3_2max)
print("")
print('		НАЙДЕНО ПОДХОДЯЩИХ СОБЫТИЙ:',length)
#выводим все ключи и их значения словаря index_plus_short с новой строки
for keys,values in index_plus_short.items():
    print(keys,' ',values)


#time.sleep(600)
print("")
print('		Нажмите ENTER для выхода')
name = input()
