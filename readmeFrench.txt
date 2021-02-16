Installer python sur son ordinateur : https://www.python.org/downloads/windows/      (latest python3 release)

Installer les librairies dépendantes : subprocess, ppadb, pytesseract, PIL
pour cela, ouvrir un terminal et taper une par une les commandes suivantes :

pip install subprocess.run
pip install pure-python-adb
pip install pytesseract
pip install pil
pip install configparser

Les librairies sont maintenant installées mais pytesseract est un peu particulier...
Pour cela il faut installer un .exe additionnel : https://osdn.net/frs/g_redir.php?m=kent&f=tesseract-ocr-alt%2Ftesseract-ocr-setup-3.02.02.exe

Vous avez maintenant toutes les librairies fonctionnelles mais le programme utilise la langue française dans Tesseract
il faut donc déplacer un fichier (fra.traineddata) dans le dossier tessdata d'installation de Tesseract
quelque part comme ça : C:\Program Files\Tesseract-OCR\tessdata

Du côté du script c'est tout bon. Il ne vous reste plus qu'à installer un émulateur (j'utilise MEmu et je ne sais pas si le script fonctionne avec d'autres émulateurs)
Téléchargement de MEmu : https://www.memuplay.com/

C'est presque fini ! Une fois MEmu installé il suffit de l'ouvrir, de vous connecter avec un compte Google quelconque
pour installer bravoloto.

Ouvrez bravoloto, jouez quelques grilles histoire d'initialiser l'app et c'est tout bon !

Vous pouvez avoir quelques problèmes avec les chemins d'accès dans le code, il suffit de lire l'erreur et de les changer.
Vous pouvez aussi rencontrer d'autres erreurs, dites-le moi et je vous dirai quoi faire !

Lancer alors le script : ouvrez une invite de commande dans le dossier où se trouver le fichier bravolobot.py
et tapez : python bravolobot.py

Vous pouvez continuer à utiliser votre ordinateur pendant ce temps.

Il arrive cependant que quelques erreurs surviennent, elles seront probablement patchées avec les prochaines maj
(faites moi parvenir vos erreurs svp)

Tips bonus :

vous pouvez programmer des lancements automatique du programme avec le plannificateur de tâches de Windows

vous pouvez régler MEmu à 3fps dans les paramètres>display afin que votre ordi garde le plus de ressources possibles

vous pouvez consulter le log pour suivre le nombre de grilles jouées par le bot

enfin vous pouvez améliorer/optimiser le code pour plus de fluidité

