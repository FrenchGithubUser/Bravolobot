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

#path pour le binaire tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

def rd_pause(a,b):
	time.sleep(uniform(a,b))

def connexion_adb():
	try:
		global device
		client = Client(host='127.0.0.1', port=5037)
		devices = client.devices()
		device = devices[0]
		print(f"\nConnexion établie avec {device} ")
	except:
		time.sleep(5)
		connexion_adb()


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
	device.shell("am force-stop com.marketluck.bravoloto")
	launch_app()
	verif_app_ouverte()

def verif_app_ouverte():
	while True:
		screenshot()
		try:
			file = Image.open("screen.raw").rotate(270, expand=True).crop((110, 1045, 596, 1149))
			txt_img = pytesseract.image_to_string(file, lang="fra")
			with open("check_app_ouverte.txt", "w") as check:
				#écrit ce qu'il y a dans le screen dans un fichier "check_app_ouverte.txt"
				check.write(txt_img)
			if "JOUER" in open("check_app_ouverte.txt").read():
				break
		except:
			verif_app_ouverte()
		time.sleep(8)


#permet de randomiser les coordonnées du clic mais CLIQUE AUSSI SUR LE POINT CHOISI
def rd_coord(coord_tuple):
	(x1,y1,x2,y2) = coord_tuple
	return "input tap "+str(randint(x1,x2))+" "+str(randint(y1,y2))

def check_dayly_reward():
	color = get_color(674,216)[:3]
	if color == (255,25,8):
		print("Récompense quotidienne disponible !")

	else:
		print("\nRécompense quotidienne déjà récupérée")

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
	scr = Image.open("screen.raw").rotate(270, expand=True)
	grilles_sur_grilles = pytesseract.image_to_string(scr.crop((378,232,488,264)))[::-1]
	nb_grilles_a_jouer = ""
	for i in grilles_sur_grilles :
		if i == "/":
			break
		else:
			nb_grilles_a_jouer += i
	nb_grilles_a_jouer = nb_grilles_a_jouer[::-1]
	print(f"\nVous avez {nb_grilles_a_jouer} grilles dispo à jouer") #debug
	if int(nb_grilles_a_jouer) <= 75:
		if int(pytesseract.image_to_string(scr.crop((92,235,200,262)))) >= 1000:
			print("\nIl est rentable d'acheter des grilles supplémentaires, c'est parti !")
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
			print("Vous voilà avec 25 grilles en plus !")
			time.sleep(4)
			device.shell(rd_coord((232,867,476,911)))
			time.sleep(4)
			restart_app()
		else:
			print("\nVous avez moins de 75 grilles dispo mais moins de 1000 pièces...\nOn fera le plein la prochaine fois ! ")
	else:
		print("\nVous avez plus de 75 grilles dispo ! Pas besoin d'en acheter !") #debug


def main_loop():
	last_event = 0
	elapsed_loops = 0
	played_grids = 0
	etat_jouer = 0
	etat_valider = 0
	etat_nouvelle = 0
	last_time = time.time()
	while True:
		rd_pause(1,3)
		screenshot()
		#associe le screenshot à une variable (rotation nécessaire ou non en fonction des configs)
		scr = Image.open("screen.raw").rotate(270, expand=True)

		if "Obtenez" in pytesseract.image_to_string(scr.crop(coord_fin)):
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
				if gridtype == 'Mega':
					device.shell(rd_coord(coord_pop10))


coord_play = (262,1074,455,1131)
coord_rand = (231,1032,486,1081)
coord_validate = (263,1158,460,1207)
coord_back = (45,45,55,55)
coord_gift = (661,202,694,239)
coord_pop10 = (293,737,398,782)
coord_fin = (217,528,348,563)


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



# Démarrage de MEmu
try:
	subprocess.Popen("C:/Program Files (x86)/Microvirt/MEmu/MEmu.exe")  # Changer le chemin d'accès si besoin
	print("\nDémarrage de MEmu...")
except subprocess.CalledProcessError as error:
	print(str(error))
print("\nConnexion avec l'émulateur...")
connexion_adb()
launch_app()
print("\nDémarrage de Bravoloto...\n")

#Cree le fichier de log si il n'existe pas deja
try:
	with open("log.ini","r") as nb:
		print("Voici les grilles déjà jouées au paravant : \n")
		print(nb.read())
except:
	log['Jackpot'] = {'nb grille': 0, 'temps': 0}
	log['Super'] = {'nb grille': 0, 'temps': 0}
	log['Mega'] = {'nb grille': 0, 'temps': 0}
	with open("log.ini","w") as file:
		log.write(file)

verif_app_ouverte()
print("Bravoloto démarré avec succès !") # debug

check_dayly_reward()

#check_grilles_sup()

log.read('log.ini')
#Jackpot
gridtype = 'Jackpot'
nb_grille_jouees = 0
coord_newgrid = (118,365,606,414)
main_loop()
print("\nToutes les grilles jackpot sont remplies !\nPassage au Super jackpot...")

#Super Jackpot
gridtype = 'Super'
coord_super = (250,126,462,178)
restart_app()
device.shell(rd_coord(coord_super))
time.sleep(0.5)
coord_newgrid = (112,462,610,520)
main_loop()
print("\nToutes les grilles Super jackpot sont remplies !\nPassage au Mega jackpot...")

#Mega jackpot
gridtype = 'Mega'
coord_mega = (509,136,700,170)
restart_app()
device.shell(rd_coord(coord_mega))
time.sleep(0.5)
coord_newgrid = (112,462,610,520)
main_loop()

print("\nPlus de grilles à jouer, fin de l'éxecution\n")
os.system("taskkill /f /im MEmu.exe")
