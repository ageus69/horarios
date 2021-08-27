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

def recombina(horario1, horario2):
    
    # Saco una materia al azar de un horario y la meto en el otro y viceversa
    horario = Horario()
    
    print('horario1',len(horario1.clases))
    print('horario2',len(horario2.clases))
    
    if(len(horario1.clases) == 0 or len(horario2.clases) == 0):
        return horario
    
    for i in range(len(materias)):    
        index1 = random.randint(0, 1)
        if index1 == 0:
            horario.clases.append(horario1.clases[i])
        else:
            horario.clases.append(horario2.clases[i])
    
    return horario
    
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
        self.materiaName = ''
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
        print('Materia_%s_nrc_%s_cupos_%d%s' % (self.materiaName, self.nrc, self.cupos, self.diasToString()))
        
    def showChromosoma(self):
        print('Materia_%s_nrc_%s_cupos_%d%s' % (materias.index(self.materia), self.nrc, self.cupos, self.diasToStringChromosoma()))
    
class Horario():
    def __init__(self):
        self.disponible = np.full((6,15), -1)
        self.fitness = 0
        self.clases = []
        self.clases_sinColition = []
          
    def __hash__(self):
        # necessary for instances to behave sanely in dicts and sets.
        return hash((self.disponible, self.fitness, self.clases, self.clases_sinColition))
        
    def clear(self):
        self.disponible = np.full((6,15), -1)
        self.fitness = 0
        self.clases = []
        self.clases_sinColition = []
        
    def colisionClases(self, clase1, clase2):
        matriz_auxiliar = np.full((6,15), -1)
        for dia in clase1.dias:
            for x in range(dia.horaI, dia.horaF):
                matriz_auxiliar[dia.dia][x] = 0     
                
        for dia in clase2.dias:
            for x in range(dia.horaI, dia.horaF):
                if (matriz_auxiliar[dia.dia][x] == 0):
                    return 1 # Colision
        return 0 # No colision
        
    def quitarClase(self, indice):
        # Quitar de la matriz
        for dia in self.clases[indice].dias:
            for x in range(dia.horaI, dia.horaF):
                self.disponible[dia.dia][x] = -1
        
        return self.clases.pop(indice)
        
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
        self.disponible = self.disponible = np.full((6,15), -1)
        self.clases_sinColition = []
        clases_con_colision = {}
        
        # Por cada clase verificar si no hay colisiones, si si hay, no se agregan a la matriz
        # self.disponible y se aumenta el fitness por algun valor alto. Si no hay colision
        # entonces agregamos a la matriz, pero para eso hay que inicializarla de nuevo
        for i in range(0, len(self.clases)-1):
            for j in range (i+1, len(self.clases)):
                
                if (self.colisionClases(self.clases[i], self.clases[j])):
                    # No agregar a self.disponible
                    # Aumentar al fitnes 100
                    clases_con_colision[self.clases[i].nrc] = 1
                    clases_con_colision[self.clases[j].nrc] = 1
                    self.fitness += 100
                    
        for clase in self.clases:
            try:
                clases_con_colision[clase.nrc]   
            except:
                self.clases_sinColition.append(clase)
                for dia in clase.dias:
                    for x in range(dia.horaI, dia.horaF):
                        self.disponible[dia.dia][x] = materias.index(clase.materia)

        self.fitness += (len(materias) - len(self.clases)) * 200
        for c in clases_con_colision:
            self.fitness += 200

        # Variable que mide que tan alejadas estan las materias entre si
        for i in range(0, len(self.clases_sinColition)-1):
            for j in range (i+1, len(self.clases_sinColition)):
                a = abs(self.clases_sinColition[j].dias[0].horaI - self.clases_sinColition[i].dias[0].horaI)
                if (a > 2):
                    self.fitness += a
                    
        # Variable de cuantas horas hueco tiene (depende directamente de la variable de hasta arriba)
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
        print(' |07|08|09|10|11|12|13|14|15|16|17|18|19|20|21')
        for i in range(6):
            string = str(diasMap[i]) + '|'
            for j in range(15):
                if(self.disponible[i][j] == -1):
                    string += '  |'
                else:
                    string += str(self.disponible[i][j]) + ' |'
            print(string)
        print('Fitness:', self.fitness)


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
        clase.materiaName = curso('td')[2].text 
        clase.nrc = curso('td')[0].text                                                        
        clase.cupos = int(curso('td')[5].text)
        
        clases.append(clase)
            
    return clases

# Get all clases of each materia in html and convert them into objects
cursos = convertToObjects(getCourses(materias)) 

generaciones = 10
padres = 400
hijos = 300
 
x = [Horario() for _ in range(padres + hijos)]
for h in x:
    h.updateFitness()

# Inicializacion de los padres
for i in range(padres):  
    horario = Horario()
    for _ in range(len(materias)):
        while len(horario.clases) < 4:
            flag = True
            random_curso = random.choice(cursos)
            if len(horario.clases) == 0:
                horario.clases.append(random_curso)
                continue
            for m in horario.clases:
                if (random_curso.materia == m.materia):
                    flag = False
                    break  
            if(flag):
                horario.clases.append(random_curso)  
    horario.updateFitness()
    x[i] = horario



result = [i for i in sorted(enumerate(x), key=lambda x: x[1].fitness)]
I = []
x = []
for tup in result:
    I.append(tup[0])
    x.append(tup[1])
    


#I = [i[0] for i in sorted(range(len(x)), key=lambda k: k.fitness)]
#x.sort(key=lambda xd: xd.fitness, reverse=False)

# Algoritmo genetico
for i in range(generaciones):
    print('generacion:', i)
    for j in range(hijos):
        random1 = random.randint(0, padres-1)
        random2 = random1 
        while random1 == random2:
            random2 = random.randint(0, padres-1)
        
        # Recombinacion
        x[padres + j] = recombina(x[I[random1]], x[I[random2]])
        
        # Mutacion
        
        # Update fitness
        x[padres + j].updateFitness()
        
    result = [i for i in sorted(enumerate(x), key=lambda x: x[1].fitness)]
    I = []
    x = []
    for tup in result:
        I.append(tup[0])
        x.append(tup[1])
        
x = x[::-1]        
for h in x:
    h.show()


