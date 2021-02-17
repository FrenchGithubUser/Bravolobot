import subprocess
import os
from ppadb.client import Client
import time
import pytesseract
from PIL import Image
import numpy as np
from random import uniform, randint
import configparser
log = configparser.ConfigParser()

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

def print_log(message):
	#permet d'avoir l'heure à laquelle les message ont été print
	#et assure les bons retours à la ligne entre les messages
	print(time.strftime("\n[%H:%M:%S] ") + message)

def rd_pause(a,b):
	#crée un temps de pause aléatoire entre a et b
	time.sleep(uniform(a,b))

def connexion_adb():
	print_log("Connexion avec l'émulateur...")
	while True:
		try:
			global device
			client = Client(host='127.0.0.1', port=5037)
			devices = client.devices()
			device = devices[0]
			print_log(f"Connexion établie avec {device} ")
			break
		except:
			time.sleep(5)
			
def screenshot():
	try:
		image = device.screencap()
		with open("screen.raw", "wb") as f:  #mettre en png pour la rotation et debug
			f.write(image)
	except:
		screenshot()

def launch_app():
	try:
		device.shell("monkey -p com.marketluck.bravoloto -c android.intent.category.LAUNCHER 1")
	except:
		time.sleep(1)
		launch_app()

def restart_app():
	#ralance bravolot et vérifie qu'il est ouvert
	device.shell("am force-stop com.marketluck.bravoloto")
	launch_app()
	verif_app_ouverte()

def verif_app_ouverte():
	while True:
		screenshot()
		try:
			file = Image.open("screen.raw").rotate(270, expand=True).crop((110, 1045, 596, 1149))
			txt_img = pytesseract.image_to_string(file, lang="fra")
			if "JOUER" in txt_img:
				print_log("Bravoloto démarré avec succès !")
				break
		except:
			pass
		time.sleep(8)

def rd_coord(coord_tuple):
	#permet de randomiser les coordonnées du clic mais CLIQUE AUSSI SUR LE POINT CHOISI
	(x1,y1,x2,y2) = coord_tuple
	return "input tap "+str(randint(x1,x2))+" "+str(randint(y1,y2))

def check_dayly_reward(): 
	color = get_color(674,216)[:3]
	if color == (255,25,8):
		print_log("Récompense quotidienne disponible !")

	else:
		print_log("Récompense quotidienne déjà récupérée")

def get_color(x,y):
  return Image.open("screen.raw").getpixel((x,y))

def increment_log(gridtype, elapsed_time):
	log[gridtype]['nb grille'] = str(int(log[gridtype]['nb grille'])+1)
	log[gridtype]['temps'] = str(int(log[gridtype]['temps'])+int(elapsed_time))
	write_log()

def write_log():
	with open('log.ini','w') as file:
		log.write(file)

def check_grilles_sup():
	global nb_grilles_a_jouer
	screenshot()
	scr = Image.open("screen.raw").rotate(270, expand=True) 
	if int(nb_grilles_a_jouer) <= 75:
		if int(pytesseract.image_to_string(scr.crop((92,235,200,262)))) >= 1000:
			print_log("Il est rentable d'acheter des grilles supplémentaires, c'est parti !")
			#achat de 25 grilles jackpot
			device.shell(rd_coord((30,41,81,75)))
			time.sleep(1.5)
			device.shell(rd_coord((7,309,178,342)))
			time.sleep(8)
			device.shell(rd_coord((113,434,237,559)))
			time.sleep(1.5)
			device.shell(rd_coord((97,674,328,931)))
			time.sleep(1.5)
			device.shell(rd_coord((140,925,559,983)))
			print_log("Vous voilà avec 25 grilles en plus !")
			time.sleep(4)
			device.shell(rd_coord((232,867,476,911)))
			time.sleep(4)
			restart_app()
		else:
			print_log("Vous avez moins de 75 grilles dispo mais moins de 1000 pièces... On fera le plein la prochaine fois ! ")
	else:
		print_log("Vous avez plus de 75 grilles dispo ! Pas besoin d'en acheter !")

def launch_MEmu():
	try:
		subprocess.Popen("C:/Program Files (x86)/Microvirt/MEmu/MEmu.exe")  # Changer le chemin d'accès si besoin
		print_log("Démarrage de MEmu...")
	except subprocess.CalledProcessError as error:
		print(str(error))

def main_loop():
	last_event = 0
	elapsed_loops = 0
	played_grids = 0
	etat_jouer = 0
	etat_valider = 0
	etat_nouvelle = 0
	app_arrete=0
	last_time = time.time()
	global gridtype

	launch_app()

	while True:

		rd_pause(1,3)
		screenshot()
		#associe le screenshot à une variable (rotation nécessaire ou non en fonction des configs)
		scr = Image.open("screen.raw").rotate(270, expand=True) 

		if "Obtenez" in pytesseract.image_to_string(scr.crop(coord_fin)):
			break

		if "Obtenez" in pytesseract.image_to_string(scr.crop((178,565,343,607))):
			break

		elif "maximum" in pytesseract.image_to_string(scr.crop((150, 584, 324, 618))):
			break

		elif "soumettre" in pytesseract.image_to_string(scr.crop((146,565,326,595))):
			break

		elif "JOUER" in pytesseract.image_to_string(scr.crop(coord_play)):
			#clique sur "JOUER"
			device.shell(rd_coord(coord_play))
			etat_jouer+=1
			if etat_jouer>=2:
				device.shell(rd_coord(coord_pop10))
				etat_jouer=0

		elif "parraine" in pytesseract.image_to_string(scr.crop((coord_parraine))):
			device.shell(rd_coord((586,425,615,456))) #clique sur la croix
			time.sleep(3)

		elif "Erreur" in pytesseract.image_to_string(scr.crop((coord_erreur))):
			restart_app()

		elif "Ok" in pytesseract.image_to_string(scr.crop((321,736,393,782))):
			device.shell(rd_coord((321,736,393,782)))  #ferme le pop-up

		elif "VALIDER" in pytesseract.image_to_string(scr.crop(coord_validate)):
			#clique sur "ALEATOIRE"
			device.shell(rd_coord(coord_rand))
			rd_pause(1,3)
			#clique sur "VALIDER"
			device.shell(rd_coord(coord_validate))
			time.sleep(4)
			#ferme la pub
			launch_app()
			time.sleep(5)
			etat_valider+=1
			elapsed_loops = 0
			etat_nouvelle=0
			etat_jouer=0
			if etat_valider >=2:
				device.shell("input keyevent 4")
				etat_valider=0
			elapsed_time = time.time() - last_time
			last_time = time.time()
			increment_log(gridtype, elapsed_time)

		elif "NOUVELLE" in pytesseract.image_to_string(scr.crop((coord_newgrid))):
			#clique sur "nouvelle grille"
			device.shell(rd_coord(coord_newgrid))
			etat_nouvelle+=1
			etat_valider=0
			if etat_nouvelle >=2:
				if gridtype == 'Super':
					device.shell(rd_coord(coord_pop10))
				else:
					device.shell("input keyevent 4")
					etat_nouvelle=0

		else:
			launch_app()
			elapsed_loops+=1
			#print("Aucun motif détecté") #debug
			if elapsed_loops>=2:
				elapsed_loops=0
				device.shell("input keyevent 4")
				app_arrete+=1
				if app_arrete==2:
					app_arrete=0
					device.shell(rd_coord((623,676,650,690)))
				if gridtype == 'Mega':
					device.shell(rd_coord(coord_pop10))

def boucles_par_type():
	#joue les grilles, type par type

	#Cree le fichier de log si il n'existe pas deja
	try:
		with open("log.ini","r") as nb:
			print_log("Voici les grilles déjà jouées au paravant : \n")
			print(nb.read())
	except:
		log['Jackpot'] = {'nb grille': 0, 'temps': 0}
		log['Super'] = {'nb grille': 0, 'temps': 0}
		log['Mega'] = {'nb grille': 0, 'temps': 0}
		with open("log.ini","w") as file:
			log.write(file)

	print_log("Jouons les grilles disponibles...")

	global gridtype, coord_newgrid, coord_super, coord_mega
	#check_grilles_sup()

	log.read('log.ini')
	#Jackpot
	gridtype = 'Jackpot'
	coord_newgrid = (118,365,606,414)
	main_loop()
	print_log("Toutes les grilles jackpot sont remplies ! Passage au Super jackpot...")

	#Super Jackpot
	gridtype = 'Super'
	coord_super = (250,126,462,178)
	restart_app()
	device.shell(rd_coord(coord_super))
	time.sleep(0.5)
	coord_newgrid = (112,462,610,520)
	main_loop()
	print_log("Toutes les grilles Super jackpot sont remplies ! Passage au Mega jackpot...")

	#Mega jackpot
	gridtype = 'Mega'
	coord_mega = (509,136,700,170)
	restart_app()
	device.shell(rd_coord(coord_mega))
	time.sleep(0.5)
	coord_newgrid = (112,462,610,520)
	main_loop()

	print_log("Plus de grilles à jouer pour cette session.")

def time_to_next_money_time(argument):
	#calcule le temps (en s) qu'il faut attendre avant le prochain money time (3min de marge le temps de lancer MEmu et bravoloto)
	hour = int(time.strftime("%H"))
	minute = int(time.strftime("%M"))
	h=0
	m=0
	if hour<9:
		h=9
		m=42
	elif hour==9:
		if minute<45:
			h=9
			m=42
		else:
			h=12
			m=42
	elif hour<12:
		h=12
		m=42
	elif hour==12:
		if minute<45:
			h=12
			m=42
		else:
			h=20
			m=12
	elif hour<20:
		h=20
		m=12
	elif hour==20:
		if minute<15:
			h=20
			m=12
		else:
			h=1e20
			m=1e20

	to_wait = (h-hour)*3600+(m-minute)*60

	if hour>20:
		h=23-hour+9
		m=60-minute+42
		to_wait=h*3600+m*60
	
	if argument == 1:
		pass
	else:
		heures=to_wait//3600
		to_wait-=heures*3600
		minutes=to_wait//60
		to_wait = f"{heures}h{minutes}min"
	return to_wait

def money_time():
	coord_continuer=(250,1042,465,1089)
	coord_gains=(269,224,449,284)
	coord_fleche=(308,961,408,1064)
	print_log("Money Time !!")
	launch_MEmu()
	connexion_adb()
	launch_app()
	verif_app_ouverte()

	day = time.strftime('%A')
	number = time.strftime('%d')
	month = time.strftime('%B')

	while True:
		time.sleep(2)
		screenshot()
		scr = Image.open("screen.raw").rotate(270, expand=True) 
		if "Continuer" in pytesseract.image_to_string(scr.crop(coord_continuer)):
			screenshot()
			os.rename("screen.raw",f"./money_time/gain_{day}_{number}_{month}.png")
			device.shell(rd_coord(coord_continuer))
		elif "Vy By" in pytesseract.image_to_string(scr.crop(coord_gains)):  #somehow tesseract trouve ça quand bravoloto affiche les gains obtenus
			time.sleep(12)
			device.shell(rd_coord(coord_fleche))
			time.sleep(45)
			break
		time.sleep(10)

	screenshot()
	os.rename("screen.raw",f"./money_time/gain_money_time_{day}_{number}_{month}.png")
	print_log("Money time terminé !")
	restart_app()
	time.sleep(10)   #attend le temps que les grilles se reset

def check_grilles_jouées():
	#vérifie si toutes les grilles sont jouées ou non
	global gridtype
	global nb_grilles_a_jouer
	launch_app()
	time.sleep(2)
	screenshot()
	scr = Image.open("screen.raw").rotate(270, expand=True) 
	grilles_ = pytesseract.image_to_string(scr.crop((380,232,498,264)))
	nb_grilles_a_jouer = ""

	if "/" in grilles_:
		
		for i in grilles_[::-1] :
			if i == "/":
				break
			else:
				nb_grilles_a_jouer += i
		nb_grilles_a_jouer = nb_grilles_a_jouer[::-1]

		nb_grilles_jouees = ""
		for i in grilles_:
			if i == "/":
				break
			else:
				nb_grilles_jouees += i

		if nb_grilles_a_jouer==nb_grilles_jouees:
			verification="oui"
		elif nb_grilles_jouees==100:
			verification="oui"
		else:
			verification="non"

		print_log(f"Vous avez {nb_grilles_a_jouer} grilles disponibles et vous en avez joué {nb_grilles_jouees}.")

	else:
		print_log(f"Vous avez {grilles_} grilles {gridtype} disponibles.")
		verification="non"

	return verification

coord_play = (262,1074,455,1131)
coord_rand = (231,1032,486,1081)
coord_validate = (263,1158,460,1207)
coord_back = (45,45,55,55)
coord_gift = (661,202,694,239)
coord_pop10 = (293,737,398,782)
coord_fin = (217,528,348,563)
coord_parraine = (205,742,319,776)
coord_erreur = (165,496,278,529)

#Partie du code qui s'exécute

print("\n================================================================================================================\n"
"=      ==================================  =========  ======================================  ==========      ==\n"
"=  ===  =================================  =========  =====================================   =========   ==   =\n"
"=  ====  ================================  =========  =============  =======================  =========  ====  =\n"
"=  ===  ===  =   ====   ===  =  ===   ===  ===   ===  ======   ===    =======  =  ==========  =========  ====  =\n"
"=      ====    =  ==  =  ==  =  ==     ==  ==     ==    ===     ===  ========  =  ==========  =========  ====  =\n"
"=  ===  ===  ==========  ===   ===  =  ==  ==  =  ==  =  ==  =  ===  =========   ===========  =========  ====  =\n"
"=  ====  ==  ========    ===   ===  =  ==  ==  =  ==  =  ==  =  ===  =========   ===========  =========  ====  =\n"
"=  ===  ===  =======  =  ==== ====  =  ==  ==  =  ==  =  ==  =  ===  ========== ============  =====  ==   ==   =\n"
"=      ====  ========    ==== =====   ===  ===   ===    ====   ====   ========= ==========      ===  ===      ==\n"
"================================================================================================================")

launch_MEmu()
connexion_adb()
launch_app()
verif_app_ouverte()



while True:
	if check_grilles_jouées()=="oui":
		print_log("Toutes les grilles sont jouées, MEmu se relancera au moment du prochain money time")
		os.system("taskkill /f /im MEmu.exe")
		print_log(f"Le prochain money time est dans {time_to_next_money_time(2)}")
		time.sleep(time_to_next_money_time(1))  #attend d'être 5min avant le money time pour ouvrir MEmu et bravoloto
		money_time()
		check_grilles_jouées()
		check_grilles_sup()
		boucles_par_type()
	else:
		check_grilles_sup()
		boucles_par_type()
		print_log("Toutes les grilles sont jouées, MEmu se relancera au moment du prochain money time")
		os.system("taskkill /f /im MEmu.exe")
		print_log(f"Le prochain money time est dans {time_to_next_money_time(2)}")
		time.sleep(time_to_next_money_time(1))  #attend d'être 3min avant le money time pour ouvrir MEmu et bravoloto
		money_time()
		check_grilles_jouées()
		check_grilles_sup()
		boucles_par_type()

print_log("Journée terminée, à demain !")
os.system("taskkill /f /im MEmu.exe")
