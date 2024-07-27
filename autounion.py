from playwright.sync_api import sync_playwright
from datetime import datetime
import calendar
import logging
import csv 
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

months_calender=list(calendar.month_name)[1:]

currentDay = datetime.now().day
currentMonth = datetime.now().month
currentYear = datetime.now().year

def enter_date_dep(page, input_date, flag,Time):
	logger.info("**DATE SUBMIT**")
	if flag == 'D':
		page.click('input[id="datefrom"]')
		start = 'start'
	else:
		page.click('input[id="dateto"]')
		start = 'end'
	page.wait_for_timeout(3_000)

	parsed_date = datetime.strptime(input_date, '%Y-%m-%d')

	parsed_date = str(parsed_date).split('-')
	##### year ######
	# dep_year = datetime.strptime(parsed_date[0], '%Y')
	dep_year=parsed_date[0]
	### month name #####
	dep_month=(months_calender[int(parsed_date[1][1:])-1])
	# dep_month = datetime.strptime(parsed_date[1], '%B')
	dep_day = parsed_date[2].split(' ')[0]

	x_year='div[class="ui-datepicker-title"]'
	x_month='div[class="ui-datepicker-title"]'
	x_next_month_click='a[title="Next"]'

	current_year_crawl=page.query_selector(x_year).inner_text().split(' ')[1]
	difference_in_year=int(dep_year)-int(current_year_crawl)
	
	###############################   YEAR & MONTH ---------- SELECT STATEMENT #######################
	if difference_in_year<1:
		if str(current_year_crawl)==str(dep_year):
			for month in range(0,12):
				current_month_crawl1=page.query_selector(x_month).inner_text().split(' ')[0]
				if dep_month==current_month_crawl1:
					break
				page.query_selector(x_next_month_click).click()
			
	else:
		diff=difference_in_year+1
		while diff>0:
			for month in range(0,12):
				page.query_selector(x_next_month_click).click()
				current_month_crawl1=page.query_selector(x_month).inner_text().split(' ')[0]
				if dep_month==current_month_crawl1:
					break
			diff-=1

	###############################  DAY ----------------- SELECT STATEMENT #########################
	
	tb=page.query_selector('table[class="ui-datepicker-calendar"]')
	for td in tb.query_selector_all('td[data-handler="selectDay"]'):
		if str(td.inner_text())==str(dep_day):
			td.click()
			break

	############## Time selection ###########
	if flag=='D':
		tb_click=page.query_selector('select[id="timefrom"]').click()
		page.select_option('select[id="timefrom"]', label=Time)
	else:
		tb_click=page.query_selector('select[id="timeto"]').click()
		page.select_option('select[id="timeto"]', label=Time)


	########## Waiting time #################
	page.wait_for_timeout(2_000)
	logger.info("RETURN DATE SUBMITTED")
		
	print_message = f'--------{input_date} is available.--------'
	logger.info(print_message)


def Main_fun(NAME_LOC,URL,START_DATE,END_DATE,TIME_START,TIME_END):

	START='D'
	END='F'
	with sync_playwright() as p:
		browser=p.chromium.launch(headless=False,slow_mo=50)
		page=browser.new_page()
		page.goto(URL)

		enter=page.query_selector('input[id="pickupstation"]').type(NAME_LOC,delay=200)
		page.wait_for_timeout(1_000)
		click1=page.query_selector('div[class="locationItem"]').click()
		
		date_format = '%Y-%m-%d'
		a = datetime.strptime(START_DATE, date_format)
		b = datetime.strptime(END_DATE, date_format)
		days = (b - a).days
		
		if days>1:
			try:
				enter_date_dep(page, START_DATE, START,TIME_START)
			except:
				print('incorrect start date')
			try:
				enter_date_dep(page, END_DATE, END,TIME_END)
			except:
				print('incorrect end date')

		else:
			print('incorrect date')

		page.wait_for_timeout(1_000)

		page.query_selector('button[type="submit"]').click()
		page.wait_for_timeout(17_000)

		
		Extraction(page)
		# browser.close()

def CSV_WRITER(data):
	filename = "autounion.csv"
	fields = ['START_DEST', 'END_DEST', 'CAR_NAME', 'CAR_IMAGE','PEOPLE_LOGO_COUNT','LUGGAGE_LOGO_COUNT','LOGO','FLEX_DURATION','FLEX_RATE','FLEX_DEATILS','COMFORT_DURATION','COMFORT_RATE','COMFORT_DEATILS'] 
	
	with open(filename, 'w') as csvfile: 
		csvwriter = csv.writer(csvfile) 
		csvwriter.writerow(fields) 
		csvwriter.writerows(data)



def Extraction(page):
	List_details=[]
	start_=page.query_selector('div[class="quickmodify"]').inner_text().split('\n')[0]
	end_=page.query_selector('div[class="quickmodify"]').inner_text().split('\n')[2]
	print('START:::',start_)
	print('END:::',end_)
	list_car=page.query_selector('ul[id="carlist"]')
	for li in list_car.query_selector_all('div[class="car-inner row rate"]'):
		try:
			Car_name=li.query_selector('h3').inner_text()
			Car_image="https://www.autounion.gr/"+str(li.query_selector('img[id="Image1"]').get_attribute('src')).replace('../','')
			peoplelogo=li.query_selector('p[class="specicon peopleIcon"]').inner_text()
			luggagelogo=li.query_selector('p[class="specicon luggageIcon"]').inner_text()
			logo=li.query_selector('p[class="specicon"]').inner_text()
			
			###### FLEX RATE #######
			flex_rate='div[class="exclusivePrice"]'
			Rate_title1=li.query_selector(flex_rate).query_selector('h3').inner_text()
			
			Rate_duration1=li.query_selector(flex_rate).query_selector('span[class="duration"]').inner_text()
			Rate_fare1=li.query_selector(flex_rate).query_selector('span[class="erate"]').inner_text()
			Rate_details1=li.query_selector(flex_rate).query_selector('div[class="e_incl"]').inner_text()

			###### COMFORT RATE ############
			comfort_flex='[class="inclusivePrice"]'
			
			Rate_title2=li.query_selector(comfort_flex).query_selector('h3').inner_text()
			Rate_duration2=li.query_selector(comfort_flex).query_selector('span[class="duration"]').inner_text()
			Rate_fare2=li.query_selector(comfort_flex).query_selector('span[class="irate"]').inner_text()
			Rate_details2=li.query_selector(comfort_flex).query_selector('div[class="i_incl"]').inner_text()
			
			if len(Rate_fare1)>1:
				
				print("car_name::::",Car_name)
				print("car_img::::",Car_image)
				print("peoplelogo::::",peoplelogo)
				print("luggagelogo::::",luggagelogo)
				print("logo::::",logo)
				print('---------------------------------------------------')
				print("Rate_title::::",Rate_title1)
				print("Rate_duration::::",Rate_duration1)
				print("Rate_fare::::",Rate_fare1)
				print("Rate_details::::",Rate_details1)
				print('---------------------------------------------------')
				print("Rate_title2::::",Rate_title2)
				print("Rate_duration2::::",Rate_duration2)
				print("Rate_fare2::::",Rate_fare2)
				print("Rate_details2::::",Rate_details2)

				print('\n')
				print('----------------END-----------------------------------')

				List_details.append((start_,end_,Car_name,Car_image,peoplelogo,luggagelogo,logo,Rate_duration1,Rate_fare1,Rate_details1,Rate_duration2,Rate_fare2,Rate_details2))

		except:
			pass


	CSV_WRITER(List_details)
	page.wait_for_timeout(20_000)
	
	return 'Extraction Completed'


NAME_LOC='eden roc hotel'
URL='https://www.autounion.gr/'
START_DATE='2023-05-17'
END_DATE='2023-09-17'
TIME_START='01:45'
TIME_END='05:45'

AUTO_WEBSITE=Main_fun(NAME_LOC,URL,START_DATE,END_DATE,TIME_START,TIME_END)
