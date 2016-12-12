# Sandbox


### getSpeechesOfPGs(from_year)
Metoda vrne slovar v katerem so ključi id-ji poslanskih skupin, vrednost pa so QuerySet-i govorov.
### getSpeechesOfMembers(from_year)
Metoda vrne slovar v katerem so ključi id-ji poslancev, vrednosti pa so QuerySet-i govorov.
### getSpeechesOfCoal(from_year)
Metoda vrne slovar v katerem je ključ 0, vrednost pa je QuerySet govorov od koalicijskih poslancev.
Slovar je zato, ker metoda counterOfUniqueWords sprejme seznam in nato grupira rezultate glede na ključ.
### getSpeechesOfOppo(from_year)
Metoda vrne slovar v katerem je ključ 0, vrednost pa je QuerySet govorov od opozicijskih poslancev.
Slovar je zato, ker metoda counterOfUniqueWords sprejme seznam in nato grupira rezultate glede na ključ.
### counterOfUniqueWords(speechesQS)
Metoda sprejme slovar v katerem so vrednosti QuerySet-i. Izpis je pravtako slovar z istimi ključi, vrednosti pa so Counterji besed.
### getSurenames()
Metoda vrne seznam priimkov. Pri osebah, ki imajo več priimkov se vrne prvi priimek.

## Uporaba
```
gS = getSpeechesOfPGs(2016)
cP = counterOfUniqueWords(gS)
cP[1].most_common(50) #Top 50 besed poslanske skupine 1

for surename in getSurenames():
    print surename, cP[1][surename]  # print priimka in števeca kolikokrat je priimek izgovorila poslanska skupina 1
```