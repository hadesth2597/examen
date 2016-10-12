# -*- coding: utf-8 -*-

import webapp2
import os
import jinja2
import random
#import urllib
from google.appengine.ext import ndb
import logging
from webapp2_extras import sessions
#from datetime import date
	
NUMDIGITS = 3
MAXGUESS = 10

JINJA_ENVIRONMENT = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')),
	extensions=['jinja2.ext.autoescape'],
	autoescape=True)

def render_str(template, **params):
	t = JINJA_ENVIRONMENT.get_template(template)
	return t.render(params)

class Handler(webapp2.RequestHandler):
	def dispatch(self):
		#Get a session store for this request
		self.session_store = sessions.get_store(request=self.request)

		try:
			#Dispatch the request
			webapp2.RequestHandler.dispatch(self)
		finally:
			#Save all sessions
			self.session_store.save_sessions(self.response)

	@webapp2.cached_property
	def session(self):
		#Returns a session using the default cookie key
		return self.session_store.get_session()		

 	def render(self,template, **kw):
 		 self.response.out.write(render_str(template, **kw))

 	def write(self, *a, **kw):
 		self.response.out.write(*a, **kw)

class MainPage(Handler):
	def get(self):
		self.render("index.html")

class Registro(Handler):
    def get(self):
        self.render("register.html")

class Usuario1(ndb.Model):
	nombre = ndb.StringProperty()
	email = ndb.StringProperty()
	password = ndb.StringProperty()
	lost = ndb.IntegerProperty()
	win = ndb.IntegerProperty()
	

class Usuario(Handler):
	def post(self):
		Nombre=self.request.get('txtNombre')
		Email=self.request.get('txtEmail')
		Pass=self.request.get('txtContrasena')
		consulta = Usuario1.query(ndb.AND(Usuario1.nombre==Nombre, Usuario1.password==Pass)).get()
		if consulta is not None:
			msg = ('Error, el usuario ya existe.')
			logging.info('Consulta is not none')
			self.render("register.html", error=msg)
		else:
			##global key
			##global key2
			objeto=Usuario1()
			objeto.nombre=Nombre
			objeto.email=Email
			objeto.password=Pass
			objeto.lost = 0
			objeto.win = 0
			objeto.put()
			self.render("index.html")

class Logueado(Handler):
	def get(self):
		user = self.session.get('user')
		win = self.session.get('win')
		lost = self.session.get('lost')
		trys = self.session.get('try')
		logging.info('Checkin index user value =' + str(user))
		diccionario = {}
		diccionario["nombre"] = user
		diccionario["win"] = win
		diccionario["lost"] = lost
		diccionario["try"] = trys
		self.render("user_index.html", diccionario=diccionario)

	def post(self):

			
			def getSecretNum(numDigits):
    				# Returns a string that is numDigits long, made up of unique random digits.
				numbers = list(range(10))
				random.shuffle(numbers)
				secretNum = ''
				for i in range(numDigits):
					secretNum += str(numbers[i])
				return secretNum

			def getClues(guess, secretNum):
				# Returns a string with the pico, fermi, bagels clues to the user.
				if guess == secretNum:
					return 'You got it!'

				clue = []

				for i in range(len(guess)):
					if guess[i] == secretNum[i]:
						clue.append('Fermi')
					elif guess[i] in secretNum:
						clue.append('Pico')
				if len(clue) == 0:
					return 'Bagels'

				clue.sort()
				return ' '.join(clue)

			def isOnlyDigits(num):
				# Returns True if num is a string made up only of digits. Otherwise returns False.
				if num == '':
					return False

				for i in num:
					if i not in '0 1 2 3 4 5 6 7 8 9'.split():
						return False

				return True
				
			secretNum = getSecretNum(NUMDIGITS)
			#print('I have thought up a number. You have %s guesses to get it.' % (MAXGUESS))
			#print('Guess #%s: ' % (numGuesses))
			user = self.session.get('user')
			win = self.session.get('win')
			lost = self.session.get('lost')
			trys = self.session.get('try')
			logging.info('Checkin index user value =' + str(user))
			diccionario = {}
			diccionario["nombre"] = user
			guess = self.request.get('numero')
			clue = getClues(guess, secretNum)
			if guess != secretNum:
				if trys == 10:
					Query=Usuario1.query(ndb.AND(Usuario1.nombre==self.session.get('user'))).get()
					self.session['lost'] = lost+1;
					lost = self.session.get('lost')
					Query.lost = lost 
					Query.put()
					mensaje2 = "Superaste los 10 intentos la respuesta era:"
					self.session['try'] = 1
					diccionario["lost"] = Query.lost
					diccionario["try"] = 1
					self.render("user_index.html", mensaje = clue, mensaje2 = mensaje2, secret = secretNum, diccionario = diccionario)
				else:
					self.session['try'] = trys+1;
					Query=Usuario1.query(ndb.AND(Usuario1.nombre==self.session.get('user'))).get()
					diccionario["lost"] = Query.lost
					trys = self.session.get('try')
					diccionario["try"] = trys
					self.render("user_index.html", mensaje = clue, diccionario = diccionario)
			if guess == secretNum:
				#print('excelente')
				self.session['win'] = win+1;
				Query=Usuario1.query(ndb.AND(Usuario1.nombre==self.session.get('user'))).get()
				ganadas = self.session.get('win')
				Query.win = ganadas
				Query.put()
				diccionario["win"] = win
				self.render("user_index.html", mensaje = clue, diccionario = diccionario)
			#if numGuesses > MAXGUESS:
    				#print('You ran out of guesses. The answer was %s.' % (secretNum))
				#self.render("user_index.html", mensaje = "se acabaron los intentos prro>:V", diccionario = diccionario)

	

class Logout(Handler):
	def get(self):
		#asd = int(self.session.get('lost'))
		#key = key2
		#key2.lost = asd
		#key2.put()

		global turns
		global secret
		global missed
		global string 
		global copiastring

		
		if self.session.get('user'):
			msg	= 'You are login out..'
			del self.session['user']
			turns = 6
			secret = ""
			missed = 0
			string = ""
			copiastring = ""
			self.redirect("/")
      

class Login(Handler):
	def post(self):
		Usuario=self.request.get('username')
		Pass=self.request.get('password')
		logging.info('Checking user='+ str(Usuario) + 'Pass='+ str(Pass))
		msg=''
		if Pass == '' or Usuario == '':
			msg = 'Datos incorrectos, intenta de nuevo.'
			self.render("index.html", error=msg)
		else:
			consulta=Usuario1.query(ndb.AND(Usuario1.nombre==Usuario, Usuario1.password==Pass)).get()
			logging.info('consulta: ' + str(consulta))
			if consulta is not None:
				logging.info('POST consulta=' + str(consulta))
				self.session['user'] = consulta.nombre
				self.session['win'] = consulta.win
				self.session['lost'] = consulta.lost
				self.session['try'] = 1
				user = consulta.nombre
				logging.info('User %s just logged in' % user)
				self.redirect('/user_index')
			else:
				msg = 'Datos incorrectos, intenta de nuevo.'
				self.render('index.html', error=msg)

config = {}
config['webapp2_extras.sessions'] = {
	'secret_key': 'some-secret-key',
}

app = webapp2.WSGIApplication([('/', MainPage),
								('/registro', Registro),
								('/guardar', Usuario),
								('/login', Login),
								('/user_index', Logueado),
								('/logout',Logout)], debug=True, config=config)

			
			