# Candy Crush Automatizat in Python

## Descriere
Acesta este un joc Candy Crush simplificat, automatizat in Python.  
Jocul genereaza o tabla de 11x11 cu 4 culori de bomboane si aplica mutari automat pentru a atinge un scor tinta (10000 puncte).  
Rezultatele sunt salvate in fisiere CSV pentru analiza ulterioara.

## Cerinte
- Python 3.8+  
- Biblioteca standard (`random`, `time`, `os`, `csv`, `argparse`)  

## Rulare
Din terminal/command prompt:

```bash
python candy_crush.py --jocuri 100 --delay 0.01
