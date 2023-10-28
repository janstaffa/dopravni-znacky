# dopravni-znacky

Cílem práce je vytvořit mobilní aplikaci využívající umělou inteligenci pro identifikaci dopravních značek. Aplikace by měla úspěšně najít značku/značky na snímku, následně zařadit do kategorie (výstražná, zákazová,...) a poté určit konkrétní značku. Cílem je dosáhnout úspěšnosti identifikace konkrétních značek v 65% případů. Celá tato operace by měla probíhat rychlostí okolo 5FPS - bude možné využít aplikaci pro "real time" identifikaci. Vedlejšími cíli může být inteligentní nápověda pro řidiče - zapamatuje si aktuální maximální rychlost, zda je silnice hlavní či vedlejší, jednosměrná, slepá nebo třeba upozorní na zákaz. Název značky také může přečíst.


1. Výstup: Provedení výzkumu a testování funkčnosti konceptu využití neuronové sítě pro rozpoznávání dopravních značek na menší datové sadě (úspěšné rozpoznání typu značky).
2. Výstup: Získání dostatečného množství dat (obrázků všech značek). Začátek vývoje frontendu aplikace.
3. Výstup: Dokončení vývoje neuronové sítě, vytvoření backendu aplikace a webového serveru.
4. Výstup: Dokončení vývoje aplikace, oprava chyb, detaily.
5. Výstup: Vytvoření prezentace.


Ref.: http://www.dopravni-znaceni.eu/

## Které značky dokáže program rozpoznat
<details>
  <summary>Obsah</summary>
  <a href="#a-výstražné">Výstražné</a></br>
  <a href="#b-upravující-přednost">Upravující přednost</a></br>
  <a href="#c-zákazové">Zákazové</a></br>
  <a href="#d-příkazové">Příkazové</a></br>
  <a href="#e-informativní-provozní">Informativní provozní</a>
</details>


### a) Výstražné:	

A01a - Zatáčka vpravo

![A01a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/af561fc6-7c68-407a-9580-2ddcc71faeee)


A01b - Zatáčka vlevo  

![A01b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/383810ce-08a5-4b4d-8729-8459656ad1c7)


A02a - Dvojitá zatáčka, první vpravo 

![A02a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/32fb855a-0849-4b11-be9c-49acd774cdf5)

 
A02b - Dvojitá zatáčka,první vlevo  

![A02b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/608cd3c1-a2d2-461d-945b-92a3d2db74e0)


A03 - Křižovatka

![A03](https://github.com/janstaffa/dopravni-znacky/assets/58565385/a909b851-fb31-4e69-bcb8-11a5582b7e2a)


A04 - Pozor, kruhový objezd

![A04](https://github.com/janstaffa/dopravni-znacky/assets/58565385/77ed37fc-86ee-476b-86a8-3810079aaab4)


A06a - Zúžená vozovka (zobou stran)	

![A06a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/f8d817e7-82c1-4bf0-ba92-24e68ea5c288)


A06b - Zúžená vozovka (zjedné strany)

![A06b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/0241636e-e5da-4ae8-bdbd-0944c95f6676)


A07a - Nerovnost vozovky

![A07a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/af5cc0b0-d846-4657-a549-0efea1995023)


A07b - Pozor, zpomalovací práh

![A07b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/a8dedcdf-78cb-4e60-ba54-f0cb720029d8)


A08 - Nebezpečí smyku	

![A08](https://github.com/janstaffa/dopravni-znacky/assets/58565385/f423386c-b5b3-4a31-bb2b-6aff9c594b88)


A09 - Provoz v obou směrech	

![A09](https://github.com/janstaffa/dopravni-znacky/assets/58565385/6b137e34-7b3f-480b-9fbb-923f730638e9)


A10 - Světelné signály

![A10](https://github.com/janstaffa/dopravni-znacky/assets/58565385/7102e3ef-8520-4914-b58b-bb91703f4098)


A11 - Pozor, přechod prochodce	

![A11](https://github.com/janstaffa/dopravni-znacky/assets/58565385/a16e5d1c-8420-4665-be04-b1ac23997c3f)


A12 - Děti

![A12](https://github.com/janstaffa/dopravni-znacky/assets/58565385/5e3762a7-a040-4735-a4d8-9463459e21e6)


A13 - Zvířata

![A13](https://github.com/janstaffa/dopravni-znacky/assets/58565385/52e3c3d5-3677-4e42-a561-20cae5b2aa89)


A14 - Zvěř

![A14](https://github.com/janstaffa/dopravni-znacky/assets/58565385/d8d1c15c-6308-4951-b39a-d0ebf72ae4c8)


A15 - Práce

![A15](https://github.com/janstaffa/dopravni-znacky/assets/58565385/698d5c0c-ab34-4252-821f-4a8c3db98e83)


A16 - Boční vítr

![A16](https://github.com/janstaffa/dopravni-znacky/assets/58565385/98b92ed5-bc85-4569-a0d2-def952cc0b90)


A19 - Cyklisté		

![A19](https://github.com/janstaffa/dopravni-znacky/assets/58565385/aed0eb6a-a86e-4a1f-8da0-79a95c2e9ab5)


A21 - Pozor, tunel

![A21](https://github.com/janstaffa/dopravni-znacky/assets/58565385/130a1f37-4a39-46b2-945b-5e5cceb4de3d)


A23 - Kolona

![A23](https://github.com/janstaffa/dopravni-znacky/assets/58565385/115c4fc7-0574-44e3-8dc6-5ca31169e20f)


A24 - Náledí

![A24](https://github.com/janstaffa/dopravni-znacky/assets/58565385/bf018e0a-4ece-4b68-9d76-02829c9ac80b)


A25 - Tramvaj

![A25](https://github.com/janstaffa/dopravni-znacky/assets/58565385/e9c44f2f-5188-40c0-a717-bd5bf6fae816)


A27 - Nehoda

![A27](https://github.com/janstaffa/dopravni-znacky/assets/58565385/580e20f6-7e2c-4509-8de5-55fb6819a71e)


A29 - Železniční přejezd se závorami

![A29](https://github.com/janstaffa/dopravni-znacky/assets/58565385/38cc831a-9a56-4b69-9f2c-89f247080077)


A30 - Železniční přejezd bezzávor

![A30](https://github.com/janstaffa/dopravni-znacky/assets/58565385/4f20a891-2087-440a-9fec-054af3aad440)


### b) Upravující přednost:
P01 - Křižovatka s vedlejší pozemní komunikací

![P01](https://github.com/janstaffa/dopravni-znacky/assets/58565385/61f5050f-c2ba-4266-80c5-37575ff7978d)


P02 - Hlavní pozemní komunikace	

![P02](https://github.com/janstaffa/dopravni-znacky/assets/58565385/cb13c061-3c88-4bdb-acaa-01e386458a0e)


P03 - Konec hlavní pozemní komunikace	

![P03](https://github.com/janstaffa/dopravni-znacky/assets/58565385/bad41ce3-6547-4340-945e-169b79129d8a)


P04 - Dej přednost v jízdě		

![P04](https://github.com/janstaffa/dopravni-znacky/assets/58565385/6b1a64f2-0fb0-48fe-b259-77a34b1c5252)


P06 - Stůj, dej přednost v jízdě	

![P06](https://github.com/janstaffa/dopravni-znacky/assets/58565385/3c8469bf-0760-43ce-ab93-ca0c6a7c0db1)


P07 - Přednost protijedoucích vozidel	

![P07](https://github.com/janstaffa/dopravni-znacky/assets/58565385/b051cbfb-1315-452c-88d7-5f61ffbcddfe)


P08 - Přednost před protijedoucími vozidly

![P08](https://github.com/janstaffa/dopravni-znacky/assets/58565385/d7bed138-4237-45bc-8764-d71fa3ce7708)







### c) Zákazové:
B01 - Zákaz vjezdu všech vozidel(v obou směrech)

![B01](https://github.com/janstaffa/dopravni-znacky/assets/58565385/b9c5aa9e-9c77-4568-b4f3-111e42f8e0b3)


B02 - Zákaz vjezdu všech vozidel	

![B02](https://github.com/janstaffa/dopravni-znacky/assets/58565385/81c4540a-65d4-412f-94cf-e8cd9b0098fb)


B03a - Zákaz vjezdu s vyj. motocyklů bez postr. voz.	

![B03a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/c29cacbc-54d1-4259-8ddd-1e046fe60ec4)


B03b - Zákaz vjezdu osobních automobilů

![B03b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/c120321f-1bcd-4feb-80d2-90b86e32207a)


B04 - Zákaz vjezdu nákladních automobilů	

![B04](https://github.com/janstaffa/dopravni-znacky/assets/58565385/f7421171-c864-4196-ba7b-0f63612c90fb)


B05 - Zákaz vjezdu autobusů	

![B05](https://github.com/janstaffa/dopravni-znacky/assets/58565385/50c53e39-8d09-4799-8e48-4303efe52b7b)


B07 - Zákaz vjezdu motocyklů			

![B07](https://github.com/janstaffa/dopravni-znacky/assets/58565385/73e32c0f-e9da-4c63-b408-7c4a0cbb1a36)


B11 - Zákaz vjezdu všech motorových vozidel

![B11](https://github.com/janstaffa/dopravni-znacky/assets/58565385/36d90bea-8945-4604-a107-b91f235d203c)


B18 - Z. v. voz. přep. nebezpečný náklad

![B18](https://github.com/janstaffa/dopravni-znacky/assets/58565385/9d0b7bde-585e-4e43-bf54-beb96ee6b2ba)


B19 - Z. v. voz. přep. náklad, který může znečištit vodu

![B19](https://github.com/janstaffa/dopravni-znacky/assets/58565385/17323419-3658-4006-8c2f-f81312abb726)


B20a - Nejvyšší povolená rychlost	

![B20a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/cad4238f-5a3a-4a27-997f-3fa3b11bc1d5)


B20b - Konec nejvyšší povolené rychlosti	

![B20b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/fd07a4df-f8a3-43df-af48-471661d68a2c)


B21a - Zákaz předjíždění	

![B21a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/ec4d869d-3717-402b-90f6-491317de9afd)


B21b - Konec zákazu předjíždění

![B21b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/fe6f318a-7f63-4eec-9de5-017bc71f6079)


B22a - Zákaz předjíždění pro nákladní automobily

![B22a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/6b3311d8-a63e-460b-b01f-933eacced6eb)


B22b - Konec zák. před. pro nákladní automobily	

![B22b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/c49aa27a-7719-450a-a0bd-dacdedd8ed74)


B23a - Zákaz zvukových výstražných znamení

![B23a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/a91d578d-9148-4b0e-b411-69ea8c8306db)


B23b - Konec zákazu zvuk. výst. znamení

![B23b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/dfa627f7-e9e6-47df-9bdb-ba6c0000449f)


B24a - Zákaz odbočování vpravo	

![B24a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/c219fb82-94ca-4a1a-8879-3c031cb9a51d)


B24b - Zákaz odbočování vlevo	

![B24b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/d51b094b-b361-432c-8d27-76fd14d9d4a3)


B25 - Zákaz otáčení	

![B25](https://github.com/janstaffa/dopravni-znacky/assets/58565385/4e708f3e-68e1-4d46-8d42-91309add4dc9)


B26 - Konec všech zákazů	

![B26](https://github.com/janstaffa/dopravni-znacky/assets/58565385/ce71f7c9-ca3d-4f7c-a9c1-587c5190d130)


B28 - Zákaz zastavení

![B28](https://github.com/janstaffa/dopravni-znacky/assets/58565385/46368a44-5435-40b0-84db-b49d38aff185)


B29 - Zákaz stání	

![B29](https://github.com/janstaffa/dopravni-znacky/assets/58565385/915d0f55-50a4-4a0c-868c-78e3a17f5853)


### d) Příkazové:
C01- Kruhový objezd	

![C01](https://github.com/janstaffa/dopravni-znacky/assets/58565385/72f9b966-a757-4cce-a929-24e29b54a9e2)

C02a - Přikázaný směr jízdy přímo	

![C02a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/a718df18-4cab-4ae9-8d35-9c50d6da8769)

C02b - Přikázaný směr jízdy vpravo	

![C02b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/041267b0-8ddc-4177-9ca7-f60f5bad2bd8)

C02c - Přikázaný směr jízdy vlevo	

![C02c](https://github.com/janstaffa/dopravni-znacky/assets/58565385/595edd48-bb2e-4f14-a336-1d061f76ef84)

C02d - Přikázaný směr jízdy přímo a vpravo	

![C02d](https://github.com/janstaffa/dopravni-znacky/assets/58565385/9064dda2-b6a6-4f10-966d-f1bcb3430048)

C02e - Přikázaný směr jízdy přímo a vlevo	

![C02e](https://github.com/janstaffa/dopravni-znacky/assets/58565385/b2166c78-a825-4d76-a75e-740f7984b3db)

C02f - Přikázaný směr jízdy vlevo a vpravo	

![C02f](https://github.com/janstaffa/dopravni-znacky/assets/58565385/45cb6846-571a-4f2f-b217-eeec9b8ee171)

C03a - Přikázaný směr jízdy zde vpravo		

![C03a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/8b65d85a-d13c-48d7-8f3e-58beb225ef64)

C03b - Přikázaný směr jízdy zde vlevo	

![C03b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/8cf2ad32-dc49-4b13-ac41-2bc290f043b7)

C04a - Přikázaný směr objíždění vpravo	

![C04a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/3e559363-93e2-490d-93cc-187aad314e0c)

C04b - Přikázaný směr objíždění vlevo	

![C04b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/15007e06-32fd-4314-89d3-afb203074e17)

C04c - Přikázaný směr objíždění vpravo a vlevo

![C04c](https://github.com/janstaffa/dopravni-znacky/assets/58565385/e5b7ca3a-0502-43ef-bb14-e2a6d6c92d51)

C06a - Nejnižší dovolená rychlost	

![C06a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/3b970b0b-5752-4d6a-99f6-f5df698baf4f)

C06b - Konec nejnižší dovolené rychlosti

![C06b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/4ab9181b-de2b-4af0-9992-c247958cda6e)

C13a - Rozviť světla	

![C13a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/dc6563ea-a9ef-4a72-a909-c97a98954d2e)

C13b - Rozviť světla - konec

![C13b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/bfd412ba-345f-4d8f-a3f9-622b0d0d36fd)


  
### e) Informativní provozní:
IP02 - Zpomalovací práh	

![IP02](https://github.com/janstaffa/dopravni-znacky/assets/58565385/371735c8-a754-4133-b422-171f0f5926b7)

IP04a - Jednosměrný provoz	

![IP04a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/db485a7f-02f4-4c5b-b14a-9940247c6b06)

IP04b - Jednosměrný provoz	

![IP04b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/936268aa-707c-4b5c-a915-5099992ead2e)

IP05 - Doporučená rychlost	

![IP05](https://github.com/janstaffa/dopravni-znacky/assets/58565385/67e01c79-0992-4501-adba-ec84f3ce6284)

IP06 - Přechod pro chodce

![IP06](https://github.com/janstaffa/dopravni-znacky/assets/58565385/89d04852-fbbc-492a-a6b8-4701ea200646)

IP07 - Přejezd pro cyklisty	

![IP07](https://github.com/janstaffa/dopravni-znacky/assets/58565385/58e2a865-fe7f-4832-a6bd-b31c9b3b4a63)

IP08a - Tunel	

![IP08a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/07289bca-2b8a-4d1e-98e3-f310c450035b)

IP08b - Konec tunelu	

![IP08b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/4a770b93-c58f-4f43-997c-8aa05a60bda9)


IP10a - Slepá pozemní komunikace	

![IP10a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/2861727d-4858-4898-8723-78cb5333c456)

IP10b - Návěst před slepou pozemní komunikací	

![IP10b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/587434b0-1e60-4711-bc35-fbd6a2115e46)

IP11a - Parkoviště	

![IP11a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/0eeae3a2-4d99-4ab7-9790-4fd8de7522a4)

IP14a - Dálnice	

![IP14a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/09a61cf9-19c6-4b1c-92c4-d88e639b9075)

IP14b - Konec dálnice

![IP14b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/45f045d9-787c-411b-8748-cf5f9bc782a4)

IP15a - Silnice pro motorová vozidla	

![IP15a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/37da47f5-8300-4779-b590-f44c2be3c8d2)

IP15b - Konec silnice pro motorová vozidla	

![IP15b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/b0143852-4330-40c6-9ddf-44987a7b6135)

IP26a - Obytná zóna	

![IP26a](https://github.com/janstaffa/dopravni-znacky/assets/58565385/433e623e-a98c-43be-8f11-5ec25d555299)

IP26b - Konec obytné zóny  

![IP26b](https://github.com/janstaffa/dopravni-znacky/assets/58565385/02955f48-21d2-475e-b482-e8008535a169)

