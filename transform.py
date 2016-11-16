# -*- coding: iso-8859-15 -*-

import os
import sys
import codecs
import unidecode
import numpy as np
import editdistance

ART_HEADER = u'¿Cuáles articulaciones están inflamadas o adoloridas? Seleccionar si al menos 1 estaba inflamada o adolorida al inicio'
VACC_HEADER = u'Vacunas (Seleccionar las que Sí tiene)'
AUTOIN_HEADER = u'Otras enfermedades autoinmunes (seleccionar las que Sí tiene)'

medication = [u"Metrotexate",u"Sulfasalazina",u"Cloroquina",u"Prednisolona",u"Leflunomide",
              u"Azatioprina",u"Ácido fólico",u"Ciclofosfamida",u"Ciclosporina",u"Depenicilamida",
              u"Abatacept",u"Adalimumab",u"Etanercept",u"Infliximab",u"Anakinra",u"Rituximab",
              u"Certolizumab",u"Golimumab",u"Tocilizumab",u"Tofazitinib"]

medication = [i.lower() for i in medication]

# medication = enum_list(medication)

ethnicity = [u"Caucásico", u"Afro americano", u"Latino"]
ethnicity = {k:i for i, k in enumerate(ethnicity)}

vaccines = ["Neumococo","Hepatitis B","Influenza","Herpes"]
# vaccines = {k:i for i, k in enumerate(vaccines)}

autoin = [u"Lupus",u"Sjorgen",u"Escleroderma",u"Síndrome antifosfolípido"]
# autoin = {k:i for i, k in enumerate(autoin)}

suspension = [u"Falta de eficacia",u"Toxicidad",u"Administrativa",u"No se ha usado"]
suspension = {k:i for i, k in enumerate(suspension)}

articulations = [u"Metacarpo falángicas", u"Interfalángicas proximales", u"Carpos"]
# articulations = {k:i for i, k in enumerate(articulations)}

use = [u"No", u'Sí', u"No se ha usado"]
use = {k:i for i, k in enumerate(use)}

temporality = [u"Menos de 1 mes", u"De 1 a 3 meses", u"De 4 a 6 meses", 
               u"De 7 a 9 meses", u"De 10 a 12 meses", u"De 13 a 18 meses (Año - Año y medio)", 
               u"De 19 a 24 meses (Año y medio - 2 años", u"De 25 a 30 meses (2 Años - 2 años y medio)", 
               u"De 31 a 36 meses (2 Años y medio a 3 años)", u"Más de 36 meses (Más de 3 años)"]

temporality = {k:i for i, k in enumerate(temporality)}

manifest = {u'Temprana':0, u'Tardía':1}
sex = {u'Masculino':0, u'Femenino':1}
affirmation = {u'Sí':1, u'No':0}
polarity = {u'Positiva':1, u'Negativa':0} 

params = [medication, ethnicity, vaccines, autoin, suspension, 
          articulations, use, temporality, manifest, sex, affirmation, polarity]

units = [u'mg', u'dos', u'tab']
units = {k:i for i, k in enumerate(units)}
posology = [u'd', u's', u'u', u'h']
posology = {k:i for i, k in enumerate(posology)}

with codecs.open('Input_Data.csv', 'rb', 'utf-8') as fp:
    lines = fp.readlines()

lines = map(lambda x: x.strip('\n').split('|'), lines)

header = lines[0]
lines = lines[1:]

M = len(lines)
N = len(lines[0])
C = 5

# X = np.zeros((N, M, C))  

general_info_headers = header[1:13]
# func = [lambda x: int(x)] + [lambda x: d[x] for d in [sex, ethnicity]] + [lambda x: float(x)] + \
#        [lambda x: [articulations[j] for j in x.split(',')]] + [lambda x: affirmation[x]] + \
#        [lambda x: float(x) for _ in range(0, 3)] + [lambda x: [d[j] for j in x.split(',')] for d in [vaccines, autoin]]

# general_info = map(lambda y: map(lambda x: wrap_eval(x[0], x[1]), zip(func, y[1:12])), lines)

x = []
y = []
for line in lines:
    x_inf = []
    gen_info = line[1:13]
    for i, inf in enumerate(gen_info):
        try:
            preproc = False
            if general_info_headers[i] == ART_HEADER:
                d = articulations
                preproc = True
            elif general_info_headers[i] == VACC_HEADER:
                d = vaccines
                preproc = True
            elif general_info_headers[i] == AUTOIN_HEADER:
                d = autoin
                preproc = True
            print preproc
            if preproc:
                V = inf.split(',')
                V = map(lambda x: x.strip(), V)
                if len(V) == 0:
                    x_inf += [0 for _ in d]
                else:
                    for k in d:
                        if k in V:
                            x_inf.append(1)
                        else:
                            x_inf.append(0)
            else:
                found = False
                for param in params:
                    # print param
                    if inf in param:
                        x_inf.append(param[inf])
                        found = True
                        break
                if not found:
                    x_inf.append(float(inf))
        except Exception:
            x_inf.append(-1)
    x_g = []
    y_g = []
    for i in range(0, 3):
        x_t = []
        y_t = []
        inf = line[14+i*275:13+275*(i+1)]
        results = inf[-1]
        inf = inf[:-1]
        for entry in inf:
            try:
                if len(entry) == 0:
                    x_t.append(-1)
                else:
                    found = False
                    for param in params:
                        if entry in param:
                            x_t.append(param[entry])
                            found = True
                            break
                    if not found:
                        x_t.append(float(entry))
            except Exception:
                x_t.append(-1)
        x_g.append(x_inf + x_t)
        treatments = results.split(';')
        treatments = map(lambda x: x.strip().split(' '), treatments)
        treatments = [[j.lower() for j in i] for i in treatments]
        for drug in medication:
            found = False
            for treatment in treatments:
                print drug, treatment[0]
                if editdistance.eval(drug, treatment[0]) <= 6:
                    y_t += [1, float(treatment[1]), units[treatment[2]], 
                            float(treatment[3]), posology[treatment[4]]]
                    found = True
                    break
            if not found:
                y_t += [0] + [-1 for _ in range(0, 4)]
        y_g.append(y_t)
    x.append(x_g)
    y.append(y_g)


X = np.array(x).T
Y = np.array(y).T

np.savez('data', {'inputs':X, 'labels':Y})





