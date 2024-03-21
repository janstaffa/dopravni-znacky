# Detekce dopravních značek na mobilních zařízeních pomocí neuronových sítí

Cílem práce je vytvořit mobilní aplikaci využívající umělou inteligenci pro identifikaci dopravních značek. Aplikace by měla úspěšně najít značku/značky na snímku, následně zařadit do kategorie (výstražná, zákazová,...) a poté určit konkrétní značku. Cílem je dosáhnout úspěšnosti identifikace konkrétních značek v 65% případů. Celá tato operace by měla probíhat rychlostí okolo 5FPS - bude možné využít aplikaci pro "real time" identifikaci. Vedlejšími cíli může být inteligentní nápověda pro řidiče - zapamatuje si aktuální maximální rychlost, zda je silnice hlavní či vedlejší, jednosměrná, slepá nebo třeba upozorní na zákaz. Název značky také může přečíst.


1. Výstup: Provedení výzkumu a testování funkčnosti konceptu využití neuronové sítě pro rozpoznávání dopravních značek na menší datové sadě (úspěšné rozpoznání typu značky).
2. Výstup: Získání dostatečného množství dat (obrázků všech značek). Začátek vývoje frontendu aplikace.
3. Výstup: Dokončení vývoje neuronové sítě, vytvoření backendu aplikace a webového serveru.
4. Výstup: Dokončení vývoje aplikace, oprava chyb, detaily.
5. Výstup: Vytvoření prezentace.



## Struktura projektu
- `android_app` - nativní mobilní aplikace pro Android
- `dataset` - kód pro tvorbu datové sady
- `model` - kód pro trénování neuronové sítě
- `prace` - výstup projektu (dokument, prezentace, grafy...)