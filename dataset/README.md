### Traffic sign annotations
*\* = included in GTSDB*
##### Zakazy
- 01 = zákaz vjezdu *
- 02 = zákaz vjezdu (jeden směr) *
- 03 = zákaz předjíždění *
- 04 = zákaz vjezdu motorových vozidel
- 05 = zákaz odbočení vpravo
- 06 = zákaz odbočení vlevo
- 07 = zákaz stání
- 08 = zákaz zastavení

##### Prikazy
- 09 = přikázaný směr rovně *
- 10 = přikázaný směr vpravo *
- 11 = přikázaný směr vlevo *
- 12 = kruhový objezd *
- 13 = přechod pro chodce

##### Prednost
- 14 = hlavní silnice *
- 15 = křižovatka s vedlejší  komunikací *
- 16 = stůj, dej přednost *
- 17 = dej přednost v jízdě *

##### Rychlosti
- 18 = omezení rychlosti - 30 *
- 19 = omezení rychlosti - 50 *
- 20 = omezení rychlosti - 70 *


### Datasets used
1. German Traffic Sign Detection Benchmark(GTSDB) - [Kaggle](https://www.kaggle.com/datasets/safabouguezzi/german-traffic-sign-detection-benchmark-gtsdb)
2. BelgiumTS - [website](https://btsd.ethz.ch/shareddata/)

### Data mining
#### Online dashcam video sources:
- Liberecká perla - [youtube](https://www.youtube.com/@LibereckaPerla)
- autoskolareal - [youtube](https://www.youtube.com/@autoskolareal)


### Annotation format
The annotation format used is adapted from the GTSDB dataset. It is identical to `Microsoft VoTT CSV` formats.

Header of annotation csv file is as follows: `filename;xmin;ymin;xmax;ymax;class_id`


### Author
- Jan Štaffa (janstaffa.cz)