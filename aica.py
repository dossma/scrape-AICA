from urllib.request import urlopen
from bs4 import BeautifulSoup as soup
import time

# ---------------Parameter----------------------------
filename = "aica.csv"
headers = "Company name,Address,Contact details,Contact name 1,Role Cn 1,Contact name 2,Role Cn 2,URL \n"
pause = 8  # Pause nach dem Scrapen jeder Seite in s
loopfile = r'linklist.txt'
# -------------------------------------------------------
f = open(filename, "a", encoding='utf-8', errors='replace')
f.write(headers)

with open(loopfile, encoding='utf-8', errors='replace') as linkfile:
    for url in linkfile:
        print("get:", url)
        try:
            uClient = urlopen(url)
            page_html = uClient.read()
            uClient.close()
            soup_card = soup(page_html, "html5lib")
            containers = soup_card.findAll("div", {"class": "col-md-4"})
            containers = containers[2:4]  # Nur letzen Einträge relevant
        except Exception as e:
            print("url", url, "nicht aufrufbar", e)
        try:  # Firmenname
            firmenname = soup_card.findAll("h1")[0].text.strip()
            firmenname = firmenname.replace(",", ";")
        except Exception as e:
            firmenname = "?"
            print("Ausnahme: company name")
            print(e)

        cnlist = []
        p1 = containers[0].find_all("p")

        try:  # Kontaktinfo, bis zu zwei Personen lang
            for el in p1:
                if el.strong:
                    ap = el.strong.text
                    cnlist.append(ap)
            cn1 = cnlist[0]
            if len(cnlist) > 1:  # wenn zweiter Eintrag existiert
                cn2 = cnlist[-1]
            else:
                cn2 = "?"
        except Exception as e:
            print("Ausnahme: contact names")
            cn1, cn2 = "?", "?"
            print(e)

        rollen = []
        contblock = []
        address = []
        try:
            for el in p1:
                if el.em:
                    rolle = el.em.text
                    rollen.append(rolle)

                    el.strong.clear()
                    el.em.clear()  # Tag-Inhalte löschen um danach auf den Inhalt hinter dem span zugreifen zu können
                    el.br.clear()

                    telfaxemail = el.get_text().strip()
                    telfaxemail = telfaxemail.replace("Website: ", "")  # Telefon, Fax, Webseite in Komma-String
                    telfaxemail = telfaxemail.replace("\t", "")  # Telefon, Fax, Webseite in Komma-String
                    telfaxemail = telfaxemail.replace(" ", "")  # Telefon, Fax, Webseite in Komma-String
                    telfaxemail = telfaxemail.replace("|", "\n")  # Telefon, Fax, Webseite in Komma-String

                    contblock.append(telfaxemail)  # Kontaktdaten

            # Listen in Strings konvertieren
            contblock = "\n".join(contblock)
            contblock = f'"{contblock}"'

            role1 = rollen[0].replace(",", ";")
            if len(rollen) > 1:
                role2 = rollen[-1].replace(",", ";")
            else:
                role2 = "?"

        except Exception as e:
            print("Ausnahme: contblock, rollen")
            telfaxemail, contblock, role1, role2 = "?", "?", "?", "?"
            print(e)
        # Adresse
        try:
            p2 = containers[1].find_all("p")
            website = containers[1].find_all(href=True)[0].text  #
            addrtext = p2[0].get_text()
            addrtext = addrtext.replace("\t", "")
            addrtext = addrtext.replace(", ", "\n")
            adresse = f'"{addrtext}"'
        except Exception as e:
            website = "?"
            adresse = "?"
            print("Ausnahme: website, adresse")
            print(e)

        f.write(firmenname + ","
                + adresse + ","
                + contblock + ","
                + cn1 + ","
                + role1 + ","
                + cn2 + ","
                + role2 + ","
                + website
                + "\n")

        print("wait", pause, "seconds...\n")
        time.sleep(pause)

f.close()

print("Finished")
