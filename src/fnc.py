from selenium import webdriver
import signal
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import getpass
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import PIL
import PIL.Image
import PIL.ImageFont
import PIL.ImageOps
import PIL.ImageDraw
from datetime import datetime, timedelta
import re
import time
import os

credDir = "C:/Users/snajera/Documents/chaves/"
dataDir = "C:/Users/snajera/Documents/ProgramData/AccountFraudCheck/"
homeDir = "C:/Users/snajera/OneDrive/PythonProjects/PersonalFinanceDesktop/AccountFraudCheck/data/"
phantomDirExe = r'C:\phantomjs-2.1.1-windows\phantomjs-2.1.1-windows\bin\phantomjs.exe'
minCheckAmnt = 50

def mail(to, subject, text, attach=None):
	msg = MIMEMultipart()
	msg['From'] = gmail_user
	msg['To'] = ", ".join(to)
	msg['Subject'] = subject
	msg.attach(MIMEText(text))
	part = MIMEBase('application', 'octet-stream')
	part.set_payload(open(attach, 'rb').read())
	Encoders.encode_base64(part)
	part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attach))
	msg.attach(part)
	mailServer = smtplib.SMTP("smtp.gmail.com", 587)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(gmail_user, gmail_pwd)
	mailServer.sendmail(gmail_user, to, msg.as_string())
	mailServer.close()

def text_image(text_path, font_path=None):
	"""Convert text file to a grayscale image with black characters on a white background.

	arguments:
	text_path - the content of this file will be converted to an image
	font_path - path to a font file (for example impact.ttf)
	"""
	grayscale = 'L'
	# parse the file into lines
	with open(text_path) as text_file:  # can throw FileNotFoundError
		lines = tuple(l.rstrip() for l in text_file.readlines())

	# choose a font (you can see more detail in my library on github)
	large_font = 20  # get better resolution with larger size
	font_path = font_path or 'cour.ttf'  # Courier New. works in windows. linux may need more explicit path
	try:
		font = PIL.ImageFont.truetype(font_path, size=large_font)
	except IOError:
		font = PIL.ImageFont.load_default()
		print('Could not use chosen font. Using default.')

	# make the background image based on the combination of font and lines
	pt2px = lambda pt: int(round(pt * 96.0 / 72))  # convert points to pixels
	max_width_line = max(lines, key=lambda s: font.getsize(s)[0])
	# max height is adjusted down because it's too large visually for spacing
	test_string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	max_height = pt2px(font.getsize(test_string)[1])
	max_width = pt2px(font.getsize(max_width_line)[0])
	height = max_height * len(lines)  # perfect or a little oversized
	width = int(round(max_width + 40))  # a little oversized
	image = PIL.Image.new(grayscale, (width, height), color=0)
	draw = PIL.ImageDraw.Draw(image)

	# draw each line of text
	vertical_position = 5
	horizontal_position = 5
	line_spacing = int(round(max_height * 0.8))  # reduced spacing seems better
	for line in lines:
		draw.text((horizontal_position, vertical_position),
				  line, fill=255, font=font)
		vertical_position += line_spacing
	# crop the text
	c_box = PIL.ImageOps.invert(image).getbbox()
	image = image.crop(c_box)
	return image

def check_exists_by_id(ids):
	try:
		browser.find_element_by_id(ids)
	except NoSuchElementException:
		return False
	return True

from datetime import datetime
with open(homeDir + "lastRunTime.txt", 'r') as f:
	lastRun = f.readline()

lastRunDate = datetime.strptime(lastRun, "%m/%d/%Y")
days = datetime.today().date() - lastRunDate.date()

url = 'https://www.ccculv.org/'
browser = webdriver.PhantomJS(executable_path=phantomDirExe)
browser.get(url)	#Open Browser

with open(credDir + 'bnkCred.txt', 'r') as f:
	usr = f.readline()
	pwd = f.readline()

usr_element = browser.find_element_by_name('UserName')
usr_element.send_keys(usr)
pwd_element = browser.find_element_by_name('Password')
pwd_element.send_keys(pwd)
pwd_element.submit()

with open(credDir + 'qCred.txt', 'r') as f:
	a1 = f.readline()
	a2 = f.readline()
	a3 = f.readline()
	a4 = f.readline()
	a5 = f.readline()

if check_exists_by_id('Answer'):
	sec_q_element = browser.find_element_by_id('Text')
	sec_q = sec_q_element.get_attribute('value')
	if sec_q == 'What is your favorite animal?':
		sec_a_element = browser.find_element_by_id('Answer')
		sec_a_element.send_keys(a1)
		sec_a_element.submit()
	elif sec_q == 'What is the first musical instrument you learned to play?':
		sec_a_element = browser.find_element_by_id('Answer')
		sec_a_element.send_keys(a2)
		sec_a_element.submit()
	elif sec_q == 'Where does your nearest sibling live?':
		sec_a_element = browser.find_element_by_id('Answer')
		sec_a_element.send_keys(a3)
		sec_a_element.submit()
	elif sec_q == 'Where was your wedding rehearsal dinner held?':
		sec_a_element = browser.find_element_by_id('Answer')
		sec_a_element.send_keys(a4)
		sec_a_element.submit()
	elif sec_q == 'Who is your favorite author?':
		sec_a_element = browser.find_element_by_id('Answer')
		sec_a_element.send_keys(a5)
		sec_a_element.submit()

data = []
for i in range(1,5):
	browser.get('https://online.ccculv.org/banking/Accounts/Details/Index/' + str(i))
	try:
		element = WebDriverWait(browser, 10).until(
			EC.presence_of_element_located((By.CLASS_NAME, "transaction-credit")))
	except:
		html = browser.page_source
		
	html = browser.page_source
	
	soup = BeautifulSoup(html, "html.parser")
	table = soup.find_all('table')[0]
	rows = table.find_all('tr')[1:]
	
	header = table.find_all('tr')[0]
	amountIndex = None
	dateIndex = None
	descIndex = None
	for i in range(len(header.find_all('th'))):
		if 'Amount' == header.find_all('th')[i].text.strip():
			amountIndex = i
			
		if 'Description' == header.find_all('th')[i].text.strip():
			descIndex = i

		if 'Date' == header.find_all('th')[i].text.strip():
			dateIndex = i
	
	if rows[0].text == 'There are no transactions within the selected date range.':
		continue

	for row in rows:
		subdata= []
		
		try:
			if not re.sub('[a-z,$]', '', row.find_all('td')[amountIndex].text.strip()).strip():
				continue
			
			if ('transaction-credit' in str(row.find_all('td')[amountIndex]) ) | \
			(float(re.sub('[a-z,$]', '', row.find_all('td')[amountIndex].text.strip())) < minCheckAmnt):
				continue
			
			if datetime.strptime(row.find_all('td')[dateIndex].text.strip() + ' ' + str((datetime.today()-timedelta(days=int(days.days))).year), "%b %d %Y").date() < \
			datetime.today().date() - timedelta(days=int(days.days)):
				break
			
			subdata.append(row.find_all('td')[dateIndex].text.strip())
			subdata.append(row.find_all('td')[descIndex].text.strip())
			subdata.append(row.find_all('td')[amountIndex].text.strip())
			data.append(subdata)
		except:
			continue

f.close()
if len(data) > 0:
	try:
		os.remove(dataDir + "file.txt")
	except OSError:
		pass

	f = open(dataDir + "file.txt", 'a')
	for t in data:
		f.write('   '.join(str(s) for s in t) + '\n')

	f.close()
	
	image = text_image(dataDir + "file.txt")
	image.save(dataDir + "content.png")
	
	with open(credDir + 'sndCred.txt', 'r') as f:
		gmail_user = f.readline()
		gmail_pwd = f.readline()
		
	with open(dataDir + 'emails.txt', 'r') as f:
		email1 = f.readline()
		email2 = f.readline()
		
	us = [email1, email2]
	mail(us, "Safe Contents", "", attach=dataDir + "content.png")


f = open(homeDir + "lastRunTime.txt", 'w')
f.write(datetime.today().strftime("%m/%d/%Y"))
f.close()
	
browser.service.process.send_signal(signal.SIGTERM)
browser.quit()