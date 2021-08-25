import requests
import random
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup


first_url = 'http://consulta.siiau.udg.mx/wco/sspseca.forma_consulta'
target_url = 'http://consulta.siiau.udg.mx/wco/sspseca.consulta_oferta'

_payload = {
    'ciclop':202110,
    'cup':'D',
    'crsep':None, # Clave de la materia
    'majrp':'INCO',
    'materiap':None,
    'horaip':None,
    'horafp':None,
    'horafp':None,
    'aula':None,
    'ordenp':0,
    'mostrarp':2000
}


materias = ['I5893', 'I5894', 'I5892', 'I7022'] # Materias
#materias = ['I5893']

diasMap = ['L', 'M', 'I', 'J', 'V', 'S']

colorMap = ['r', 'b', 'g', 'm', 'y', 'c']

horasDic = {
    '0700' : 0,
    '0755' : 1,
    '0800' : 1,
    '0855' : 2,
    '0900' : 2,
    '0955' : 3,
    '1000' : 3,
    '1055' : 4,
    '1100' : 4,
    '1155' : 5,
    '1200' : 5,
    '1255' : 6,
    '1300' : 6,
    '1355' : 7,
    '1400' : 7,
    '1455' : 8,
    '1500' : 8,
    '1555' : 9,
    '1600' : 9,
    '1655' : 10,
    '1700' : 10,
    '1755' : 11,
    '1800' : 11,
    '1855' : 12,
    '1900' : 12,
    '1955' : 13,
    '2000' : 13,
    '2055' : 14,
    '2100' : 14,
}

horasMap = ['0700','0800','0900','1000','1100',
            '1200','1300','1400','1500','1600',
            '1700','1800','1900','2000','2100'] 

class Dia:  
    def __init__(self, dia=None, horaI=None, horaF=None):
        self.dia = dia
        self.horaI = horaI
        self.horaF = horaF
        
    def toString(self):
        return ('%s_%s-%s' % (diasMap[self.dia], horasMap[self.horaI], horasMap[self.horaF]))
    
    def toStringChromosoma(self):
        return ('%d_%d-%d' % (self.dia, self.horaI, self.horaF))
    

class Clase:
    def __init__(self, nrc=None, cupos=-1, materia=''):
        self.materia = materia
        self.cupos = cupos
        self.nrc = nrc
        self.dias = []                  
    
    def diasToString(self):
        string = ''
        for dia in self.dias:
            string += '_'
            string += dia.toString()
        return string
    
    def diasToStringChromosoma(self):
        string = ''
        for dia in self.dias:
            string += '_'
            string += dia.toStringChromosoma()
        return string
    
    def show(self):
        print('Materia_%s_nrc_%s_cupos_%d%s' % (self.materia, self.nrc, self.cupos, self.diasToString()))
        
    def showChromosoma(self):
        print('Materia_%s_nrc_%s_cupos_%d%s' % (materias.index(self.materia), self.nrc, self.cupos, self.diasToStringChromosoma()))
    
class Horario():
    def __init__(self):
        self.disponible = np.full((6,15), -1)
        self.fitness = 0
        self.clases = []
        
    def clear(self):
        self.disponible = np.full((6,15), -1)
        self.fitness = 0
        self.clases = []
        
    def tryToAppend(self, clase): # Try to append Class
        # See if there is no class with that name clase.materia
        for c in self.clases:
            if (c.materia == clase.materia):
                return -1
        
        # primero checar que no exista colision
        for dia in clase.dias:
            for x in range(dia.horaI, dia.horaF):
                if (self.disponible[dia.dia][x] != -1):
                    return -1
        
        # si se llega a este punto, entonces no hay colisiones
        # entonces agregar a arreglo de clases y agregarlo a la matriz
        self.clases.append(clase)
        for dia in clase.dias:
            for x in range(dia.horaI, dia.horaF):
                self.disponible[dia.dia][x]= materias.index(clase.materia)
        
        return 0
            
    def updateFitness(self):
        self.fitness = 0
        self.fitness += (len(materias) - len(self.clases)) * 20 

        for i in range(6):
            flag = False 
            contador = 0
            for j in range(15):
                if j > 0:
                    if self.disponible[i][j] == -1 and self.disponible[i][j-1] != -1 and flag == False:
                        flag = True
                    if self.disponible[i][j] == -1 and flag:
                        contador += 1
                    if self.disponible[i][j] != -1 and flag:
                        self.fitness += contador
                        contador = 0
                        flag = False
    
    def show(self):
        print(self.disponible)
        print(self.fitness)


def getCourses(materias):
    with requests.session() as s:
        try:     
            cursos = []  
            for materia in materias: 
                
                # Cambiar la clave de la materia
                _payload['crsep'] = materia     
                
                # Ir a la pagina del forma para consultar horarios 
                # consultar materia por materia los cursos que tiene cada materia
                # y por ultimo convertir el plain text to html elements
                s.get(first_url)
                r = s.post(target_url, data=_payload)
                soup = BeautifulSoup(r.content, 'html.parser')
            
                # Obtener todos los cursos de una materia
                cursos += soup.find_all('tr', {'style' : 'background-color:#e5e5e5;'})
                cursos += soup.find_all('tr', {'style' : 'background-color:#FFFFFF;'})                
            
            return cursos
            
        except:
            print('error')
            return cursos

def convertToObjects(cursos_html):
    clases = []
    # Obtener solo los datos que nos interesan
    for curso in cursos_html:        
        clase = Clase()
        
        # Puede haber una fila o dos
        tabla_horas_dias = curso('td')[7].find_all('tr')
        
        if (len(tabla_horas_dias) > 1):
            for tabla in tabla_horas_dias:
                tds = tabla.find_all('td')
                hor = tds[1].text.split('-')
                dia = tds[2].text.replace('.', '').strip()
                
                clase.dias.append(Dia(diasMap.index(dia),
                                      horasDic[hor[0]],
                                      horasDic[hor[1]]))     
                  
        else:
            tds = tabla_horas_dias[0].find_all('td')
            horas = tds[1].text.split('-')
            dias = tds[2].text.replace('.', '').strip().replace(' ', '')
            dias = list(dias)
            
            for dia in dias:
                clase.dias.append(Dia(diasMap.index(dia),
                                      horasDic[horas[0]],
                                      horasDic[horas[1]]))
            
        clase.materia = curso('td')[1].text 
        clase.nrc = curso('td')[0].text                                                        
        clase.cupos = int(curso('td')[5].text)
        
        clases.append(clase)
            
    return clases

# Get all clases of each materia in html and convert them into objects
cursos = convertToObjects(getCourses(materias)) 

# this is for plotting to see distribution of courses
"""
matrices = []
f = plt.Figure()
f, axes = plt.subplots(nrows=len(materias))
for i in range (len(materias)):
    matrices.append(np.full((6,14), 0))
for curso in cursos:
    curso.showChromosoma()
    for dia in curso.dias: 
        for x in range(dia.horaI, dia.horaF+1):
            matrices[materias.index(curso.materia)][dia.dia][x] += curso.cupos
for h in range(len(matrices)):
    for i in range(6):
        for j in range(14):
            axes[h].scatter(j,i,matrices[h][i][j] * 10,c=colorMap[h], marker=("s"), alpha=(0.9))            
plt.show()
"""

# Algoritmo genetico

# 1 - Generar aleatoriamente una poblacion inicial
contador_cupos = 0
for c in cursos:
    contador_cupos += c.cupos
    
particulas = [] # horarios

#Generar n horarios aleatorio
while contador_cupos:
    horario = Horario()
    flag = False
    
    for i in range(len(materias)):
        for _ in range(100):   
            for _ in range(len(materias)):
                random_curso = random.choice(cursos)
                if (random_curso.cupos == 0):
                    continue
                result = horario.tryToAppend(random_curso)
        
            if (len(horario.clases) == 4 - i):   
                for c in horario.clases:
                    c.cupos -= 1
                    contador_cupos -= 1
                
                horario.updateFitness()
                particulas.append(horario)
                print('Contador cupos %d' % contador_cupos)
                flag = True
                break
              
        if flag: break    
   
contador = 0
for h in particulas:
    if (len(h.clases) == 4):
        contador += 1
        h.show()
        print('THIS IS AN HORARIO')
        for c in h.clases:
            c.show()

print(contador)




