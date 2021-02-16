# Bravolobot

This script has been written to learn more about python, adb and text recognition while having a fun project.

At the date it has been written, it wasn't violating any conditions of use of the Bravoloto app. Don't use it if it now does and please notify me about it.

Originally written to work under Windows, the linux port is still a beta version.

For further informations, read the `readmeFrench.txt` file.

Written with @LucienToiture

## **How it works :**

The script takes a screenshot of the app and uses pytesseract text recognition to find out what section of the app is opened.
It then applys functions depending on the section it is in (read the code for more details).

A major simplification of the code is due to the fact that on Android (at the date I'm writing this), most ads can disappear by relaunching the app, so there is no need to find the sneaky 'close ad' button.

A log of the bot's work is available as you will run the script.
