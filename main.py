import random
import time
import os
import csv
import argparse

#setari pentru joc
RANDURI = 11
COLOANE = 11
CULORI = [1, 2, 3, 4]  # 1=Rosu, 2=Galben, 3=Verde, 4=Albastru
SCOR_TINTA = 10000
SIMBOL_CULORI = {0: ' ', 1: 'R', 2: 'Y', 3: 'G', 4: 'B'}

class CandyCrush:
    #initiaza tabla si seteaza cu cat scor/numar sa inceapa
    def __init__(self, randuri=RANDURI, coloane=COLOANE, seed=None):
        self.randuri = randuri
        self.coloane = coloane
        self.scor = 0
        self.swapuri = 0
        self.total_cascade = 0
        self.joc_terminat = False
        self.motiv_oprire = ""
        if seed is not None:
            random.seed(seed)
        self.tabla = [[random.choice(CULORI) for _ in range(self.coloane)] for _ in range(self.randuri)]
        self.rezolva_tabla_initiala()

#verifica tabla de formatiuni iar daca are le sterge pentru a incepe fara formatiuni sau mai bine spus fara puncte in plus
    def rezolva_tabla_initiala(self):
        while True:
            formatiuni, _ = self.gaseste_formatiuni()
            if not formatiuni:
                break
            self.elimina(formatiuni)
            self.aplica_gravitate()
            self.reumple_tabla()

    def afiseaza_tabla(self):
        for r in range(self.randuri):
            print(' '.join([SIMBOL_CULORI[self.tabla[r][c]] for c in range(self.coloane)]))
        print('-'* (self.coloane*2-1))

    def gaseste_formatiuni(self):
        celule_potrivite = set()
        puncte = 0
        celule_folosite = set()

#linie de 5
        for r in range(self.randuri):
            for c in range(self.coloane-4):
                val = self.tabla[r][c]
                if val==0: continue
                if all(self.tabla[r][c+i]==val for i in range(5)):
                    linie = {(r, c+i) for i in range(5)}
                    if linie.isdisjoint(celule_folosite):
                        puncte += 50
                        celule_folosite.update(linie)
                        celule_potrivite.update(linie)
        for c in range(self.coloane):
            for r in range(self.randuri-4):
                val = self.tabla[r][c]
                if val==0: continue
                if all(self.tabla[r+i][c]==val for i in range(5)):
                    linie = {(r+i, c) for i in range(5)}
                    if linie.isdisjoint(celule_folosite):
                        puncte += 50
                        celule_folosite.update(linie)
                        celule_potrivite.update(linie)

#Segmente cauta cel putin 3 bombonae identice
        segmente_h = []
        segmente_v = []

#orizontal
        for r in range(self.randuri):
            c=0
            while c<self.coloane:
                val = self.tabla[r][c]
                if val==0 or (r,c) in celule_folosite:
                    c+=1
                    continue
                k=1
                while c+k<self.coloane and self.tabla[r][c+k]==val and (r,c+k) not in celule_folosite:
                    k+=1
                if k>=3:
                    segmente_h.append({'tip':'h','r':r,'c_start':c,'c_end':c+k-1,'lung':k,'val':val,'celule':{(r,c+i) for i in range(k)}})
                c+=k

#vertical
        for c in range(self.coloane):
            r=0
            while r<self.randuri:
                val = self.tabla[r][c]
                if val==0 or (r,c) in celule_folosite:
                    r+=1
                    continue
                k=1
                while r+k<self.randuri and self.tabla[r+k][c]==val and (r+k,c) not in celule_folosite:
                    k+=1
                if k>=3:
                    segmente_v.append({'tip':'v','c':c,'r_start':r,'r_end':r+k-1,'lung':k,'val':val,'celule':{(r+i,c) for i in range(k)}})
                r+=k

#forme L si T
        for h in segmente_h:
            if h['celule'].intersection(celule_folosite): continue
            for v in segmente_v:
                if v['celule'].intersection(celule_folosite): continue
                if h['val']==v['val']:
                    intersect = h['celule'].intersection(v['celule'])
                    if intersect:
                        pt = list(intersect)[0]
                        is_h_mid = h['c_start'] < pt[1] < h['c_end']
                        is_v_mid = v['r_start'] < pt[0] < v['r_end']
                        puncte_forma = 0
                        if is_h_mid or is_v_mid:
                            puncte_forma = 30  # T
                        else:
                            puncte_forma = 20  # L
                        puncte += puncte_forma
                        combinate = h['celule'].union(v['celule'])
                        celule_folosite.update(combinate)
                        celule_potrivite.update(combinate)

#toate segmentele sunt sortate dupa lungime si luate de la cele mai multe bomboane la cele mai putine
#pentru a da un scor cat mai corect
        toate_segmentele = sorted(segmente_h+segmente_v,key=lambda x:x['lung'],reverse=True)
        for seg in toate_segmentele:
            if seg['celule'].isdisjoint(celule_folosite):
                if seg['lung']>=4:
                    puncte += 10
                else:
                    puncte += 5
                celule_folosite.update(seg['celule'])
                celule_potrivite.update(seg['celule'])

        return celule_potrivite, puncte

    def elimina(self, celule):
        for r,c in celule:
            self.tabla[r][c] = 0

#"cad" bomboane pentru a umple spatiile goale
    def aplica_gravitate(self):
        for c in range(self.coloane):
            coloana_noua = [self.tabla[r][c] for r in range(self.randuri) if self.tabla[r][c] != 0]
            padding = self.randuri - len(coloana_noua)
            for r in range(padding):
                self.tabla[r][c] = 0
            for r in range(len(coloana_noua)):
                self.tabla[padding+r][c] = coloana_noua[r]

#tot ce este 0 adica fara bomboane se alege random o culoare (o bomboana)
    def reumple_tabla(self):
        for r in range(self.randuri):
            for c in range(self.coloane):
                if self.tabla[r][c] == 0:
                    self.tabla[r][c] = random.choice(CULORI)

#schimba doua bomboane intre ele
    def incearca_swap(self, r1, c1, r2, c2):
        self.tabla[r1][c1], self.tabla[r2][c2] = self.tabla[r2][c2], self.tabla[r1][c1]
        formatiuni, puncte = self.gaseste_formatiuni()
        if formatiuni:
            self.swapuri += 1
            self.proces_cascade(formatiuni, puncte)
            return True
        else:
            self.tabla[r1][c1], self.tabla[r2][c2] = self.tabla[r2][c2], self.tabla[r1][c1]
            return False
#se ocupa de rularea cascadei dupa un swap valid: elimina bomboanele potrivite, aplica gravitatea, reumple tabla si adauga puncte
    def proces_cascade(self, formatiuni_initiale, puncte_initiale):
        formatiuni = formatiuni_initiale
        puncte = puncte_initiale
        while formatiuni:
            puncte_de_adaugat = puncte_initiale
            if self.scor + puncte_de_adaugat > SCOR_TINTA:
                puncte_de_adaugat = SCOR_TINTA - self.scor
            self.scor += puncte_de_adaugat
            self.elimina(formatiuni)
            self.aplica_gravitate()
            self.reumple_tabla()
            self.total_cascade += 1
            formatiuni, puncte = self.gaseste_formatiuni()
            if self.scor >= SCOR_TINTA:
                self.joc_terminat = True
                self.motiv_oprire = "ATINS_SCOR_TINTA"
                break

#se ocupa de un pas automat de joc fara vizualizare
#verifica toate mutarile posibile, alege cea mai buna mutare
#care creeaza formatiuni, executa swap ul si proceseaza eventualele cascade
    def pas_auto_joc(self):
        if self.scor >= SCOR_TINTA:
            self.joc_terminat = True
            self.motiv_oprire = "ATINS_SCOR_TINTA"
            return False
        potential = []
        for r in range(self.randuri):
            for c in range(self.coloane):
                if c+1 < self.coloane:
                    potential.append((r,c,r,c+1))
                if r+1 < self.randuri:
                    potential.append((r,c,r+1,c))
        valid = []
        for r1, c1, r2, c2 in potential:
            self.tabla[r1][c1], self.tabla[r2][c2] = self.tabla[r2][c2], self.tabla[r1][c1]
            formatiuni, puncte = self.gaseste_formatiuni()
            if formatiuni:
                valid.append({'mutare':(r1,c1,r2,c2), 'puncte': puncte})
            self.tabla[r1][c1], self.tabla[r2][c2] = self.tabla[r2][c2], self.tabla[r1][c1]
        if not valid:
            self.joc_terminat = True
            self.motiv_oprire = "NU_EXISTA_MUTARI"
            return False
        best = max(valid, key=lambda x: x['puncte'])
        r1, c1, r2, c2 = best['mutare']
        self.incearca_swap(r1, c1, r2, c2)
        return True

#functie care curata consola
def clear_console():
    os.system('cls' if os.name=='nt' else 'clear')

#se ocupa de un pas automat de joc cu vizualizare
#afiseaza tabla, scorul, swap-urile si cascadele dupa fiecare mutare
#include un mic delay pentru a urmari vizual procesul
def pas_auto_joc_vizual(joc, delay=0.01):
    if joc.scor >= SCOR_TINTA:
        joc.joc_terminat = True
        joc.motiv_oprire = "ATINS_SCOR_TINTA"
        return False
    potential = []
    for r in range(joc.randuri):
        for c in range(joc.coloane):
            if c+1 < joc.coloane:
                potential.append((r,c,r,c+1))
            if r+1 < joc.randuri:
                potential.append((r,c,r+1,c))
    valid = []
    for r1,c1,r2,c2 in potential:
        joc.tabla[r1][c1], joc.tabla[r2][c2] = joc.tabla[r2][c2], joc.tabla[r1][c1]
        formatiuni, puncte = joc.gaseste_formatiuni()
        if formatiuni:
            valid.append({'mutare': (r1,c1,r2,c2), 'puncte': puncte})
        joc.tabla[r1][c1], joc.tabla[r2][c2] = joc.tabla[r2][c2], joc.tabla[r1][c1]
    if not valid:
        joc.joc_terminat = True
        joc.motiv_oprire = "NU_EXISTA_MUTARI"
        return False
    best = max(valid, key=lambda x: x['puncte'])
    r1,c1,r2,c2 = best['mutare']
    joc.incearca_swap(r1,c1,r2,c2)
    clear_console()
    print(f"Swap: ({r1},{c1}) <-> ({r2},{c2}) | Scor: {joc.scor} | Swap-uri: {joc.swapuri} | Cascade: {joc.total_cascade}")
    joc.afiseaza_tabla()
    time.sleep(delay)
    return True

#functia principala care ruleaza toate jocurile
#creeaza fisiere CSV pentru rezultate, initializeaza fiecare joc
#ruleaza mutarile automate pana la final si salveaza datele despre scor, swap-uri, cascade si motivul opririi
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jocuri", type=int, default=100, help="Numar de jocuri de rulat")
    parser.add_argument("--delay", type=float, default=0.01, help="Delay vizualizare (sec)")
    args = parser.parse_args()

    if not os.path.exists("rezultate"):
        os.makedirs("rezultate")
    csv_file = "results/summary.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id_joc","puncte","swapuri","total_cascade","a_atins_target","motiv_oprire","mutari_pana_la_10000"])

        for id_joc in range(args.jocuri):
            joc = CandyCrush()
            clear_console()
            print(f"Joc {id_joc} initial:")
            joc.afiseaza_tabla()
            time.sleep(0.5)
            mutari_pana_la_target = 0
            while not joc.joc_terminat:
                pas_auto_joc_vizual(joc, delay=args.delay)
                if joc.scor >= SCOR_TINTA:
                    mutari_pana_la_target = joc.swapuri
            writer.writerow([id_joc, joc.scor, joc.swapuri, joc.total_cascade,
                             joc.scor>=SCOR_TINTA, joc.motiv_oprire, mutari_pana_la_target if joc.scor>=SCOR_TINTA else ""])
            time.sleep(0.5)
    print(f"Rezultatele au fost salvate in {csv_file}")

if __name__=="__main__":
    main()
