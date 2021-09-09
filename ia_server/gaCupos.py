import requests
import random
import copy
import numpy as np
import sys
import json
from bs4 import BeautifulSoup


first_url = 'http://consulta.siiau.udg.mx/wco/sspseca.forma_consulta'
target_url = 'http://consulta.siiau.udg.mx/wco/sspseca.consulta_oferta'

_payload = {
    'ciclop':sys.argv[3],
    'cup':'D',
    'crsep':None, # Clave de la materia
    'majrp':None,
    'materiap':None,
    'horaip':None,
    'horafp':None,
    'horafp':None,
    'aula':None,
    'ordenp':0,
    'mostrarp':2000
}

materias = sys.argv[1].split(',')
generaciones = int(sys.argv[2])

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

def recombinaMutacion(h1, h2, h3):
    cupos = []
    flags = [False for i in range(len(materias))]
    for c in h1.clases:
        cupos.append(c)
    for c in h2.clases:
        cupos.append(c)
    for c in h3.clases:
        cupos.append(c)
        
    random.shuffle(cupos)
    
    h1.clases = []
    h2.clases = []
    h3.clases = []
    
    if(len(cupos) != 0):
        for i in range(len(materias)):
            if flags[materias.index(cupos[len(cupos)-1].materia)] == False:
                flags[materias.index(cupos[len(cupos)-1].materia)] = True
                h1.clases.append(cupos.pop())
                if(len(cupos) == 0):
                    break
            
    if(len(cupos) != 0):
        flags = [False for i in range(len(materias))]         
        for i in range(len(materias)):
            if flags[materias.index(cupos[len(cupos)-1].materia)] == False:
                flags[materias.index(cupos[len(cupos)-1].materia)] = True
                h1.clases.append(cupos.pop())
                if(len(cupos) == 0):
                    break 
                
    if(len(cupos) != 0):
        flags = [False for i in range(len(materias))]
        for i in range(len(materias)):
            if flags[materias.index(cupos[len(cupos)-1].materia)] == False:
                flags[materias.index(cupos[len(cupos)-1].materia)] = True
                h1.clases.append(cupos.pop())
                if(len(cupos) == 0):
                    break
    
    h1.updateFitness()
    h2.updateFitness()
    h3.updateFitness()

def recombina(horario1, horario2):
    
    horarios = []
    
    for i in range(len(horario1.clases)):
        for j in range(len(horario2.clases)):
            if(horario1.clases[i].materia == horario2.clases[j].materia):
                h = copy.deepcopy(horario1)
                h2 = copy.deepcopy(horario2)
                aux = h.clases[i]
                h.clases[i] = horario2.clases[j]
                h2.clases[j] = aux
                h.updateFitness()
                h2.updateFitness()
                horarios.append(h)
                horarios.append(h2)
                
    horarios.sort(key=lambda x: x.fitness, reverse=True)
    
    if(len(horarios) > 0):
        if(horarios[0].fitness > horario1.fitness and horarios[0].fitness > horario2.fitness): 
            h = Horario()
            
            for c in horario1.clases:
                h.clases.append(c)
                
            for c in horario2.clases:
                h.clases.append(c)
            
            for c_ in horarios[0].clases:
                for c in h.clases:
                    if(c.cupo == c_.cupo):
                        h.clases.remove(c)
                        break

            h.updateFitness()
            return horarios[0], h
    return horario1, horario2

def seleccion(horarios):
    fitness_total = 0
    rand = random.random()
    p_sum = 0
    for h in horarios:
        fitness_total += h.fitness
          
    for i in range(1, len(horarios)):
        try:
            p_sum = p_sum + horarios[i].fitness / fitness_total
        except:
            p_sum = random.randint(0, len(horarios)-1)
        if(p_sum >= rand):
            return i
        
    return len(horarios)-1

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
        self.profe = ''
        self.cupos = cupos
        self.nrc = nrc
        self.cupo = None
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
        self.id = -1
        self.disponible = np.full((6,15), -1)
        self.fitness = 1000
        self.clases = []
        self.clases_sinColition = []
        
    def clear(self):
        self.disponible = np.full((6,15), -1)
        self.fitness = 1000
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
            
    def updateFitness(self):
        
        self.fitness = 1000
        self.disponible = self.disponible = np.full((6,15), -1)
        self.clases_sinColition = []
        clases_con_colision = {}
        
        # Por cada clase verificar si no hay colisiones, si si hay, no se agregan a la matriz
        # self.disponible y se aumenta el fitness por algun valor alto. Si no hay colision
        # entonces agregamos a la matriz, pero para eso hay que inicializarla de nuevo
        for i in range(0, len(self.clases)-1):
            for j in range (i+1, len(self.clases)):      
                if (self.colisionClases(self.clases[i], self.clases[j])):
                    clases_con_colision[self.clases[i].cupo] = 1
                    clases_con_colision[self.clases[j].cupo] = 1
                    
                if (self.clases[i].materia == self.clases[j].materia):
                    self.fitness -= 90 # Castigo que se repitan materias
                    
        for clase in self.clases:
            try:
                # Castigo colision
                clases_con_colision[clase.cupo] 
                self.fitness -= 60
            except:
                # Escribo en la matriz disponible, las clases que no tienen colision
                self.clases_sinColition.append(clase)
                for dia in clase.dias:
                    for x in range(dia.horaI, dia.horaF):
                        self.disponible[dia.dia][x] = materias.index(clase.materia)

        
        self.fitness -= (len(materias) - len(self.clases)) * (40) # Castigo que falten materias
            

        # Variable que mide que tan alejadas estan las materias entre si
        for i in range(0, len(self.clases_sinColition)-1):
            for j in range (i+1, len(self.clases_sinColition)):
                a = abs(self.clases_sinColition[j].dias[0].horaI - self.clases_sinColition[i].dias[0].horaI)
                if (a > 2):
                    self.fitness -= (a-2)//2 # Castigo distancias
                    
        # Variable de cuantas horas hueco tiene (depende directamente de la variable de hasta arriba)
        for i in range(6):
            flag = False 
            contador = 0
            for j in range(15):
                if j > 0:
                    if self.disponible[i][j] == -1 and self.disponible[i][j-1] != -1 and flag == False:
                        flag = True
                    if self.disponible[i][j] == -1 and flag:
                        contador += 2
                    if self.disponible[i][j] != -1 and flag:
                        self.fitness -= contador # Castigo hucos
                        contador = 0
                        flag = False
        if (len(self.clases) == 0):
            self.fitness = 1
        if self.fitness < 0:
            self.fitness = 1
    
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
        print('')
        string = ''
        for c in self.clases:
            string += ('materia: %s nrc: %s cupo %d\n' %( c.materia, c.nrc, c.cupo))
        print(string)
        print('Fitness:', self.fitness)
    
    def showString(self):
        string = '\n'
        string += ('_|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21\n')
        for i in range(6):
            string += str(diasMap[i]) + '|'
            for j in range(15):
                if(self.disponible[i][j] == -1):
                    string += '__|'
                else:
                    string += str(self.disponible[i][j]) + '_|'
            string += '\n\n'
        #string += ('Fitness: %d\n\n' % self.fitness)
        aux = ''
        for i in range(len(self.clases)):
            aux += self.clases[i].nrc + ' '
            string += ('materia %d: \n\t %s(%s)\n nrc: %s\n profe: %s\n\n' %(i, self.clases[i].materiaName, self.clases[i].materia, self.clases[i].nrc, self.clases[i].profe))

        string += 'nrcs ' + aux + '\n'

        return string

    def getJson(self):
        data = {}
        data['id'] = self.id
        data['fitnes'] = self.fitness
        clases_object = {}
        for clase in self.clases:
            clases_object['clave'] = clase.materia
            clases_object['profe'] = clase.profe
            clases_object['nrc'] = clase.nrc
            clases_object['dias'] = {}
            for dia in clase.dias:
                clases_object['dias'][dia.dia] = {'horaI':dia.horaI, 'horaF':dia.horaF}
        data['clases'] = clases_object
        return data


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
            return cursos

def convertToObjects(cursos_html):
    clases = []
    
    for i in range(len(materias)):
        clases.append([])
        
    cupos = 0
    # Obtener solo los datos que nos interesan
    for curso in cursos_html:        

        if int(curso('td')[6].text) <= 0:
            continue

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
        clase.cupos = int(curso('td')[6].text)
        clase.cupo = cupos
        clase.profe = curso.find_all("td", class_="tdprofesor")[1].text
        
        
        clases[materias.index(clase.materia)].append(copy.deepcopy(clase))
        cupos+=1
         
        
    # Un arreglo de 2 dimenciones donde estan los cupos separados por materias
    return clases, cupos

def genera_aleatorio(_cupos, _curses):
    cupos = _cupos
    curses = copy.deepcopy(_curses)
    particulas = []
    
    while cupos:
        horario = Horario()
        #while ( len(horario.clases) < len(materias) ):
            
        if(cupos == 0):
            break
        
        for i in range(len(materias)): #Por cada materia de las que deberia

            if(len(curses[i]) == 0):
                r = random.randint(0, len(_curses[i]) - 1)
                random_curso = _curses[i][r]
                horario.clases.append(random_curso)
            else:
                r = random.randint(0, len(curses[i]) - 1) #Escoges un cupo de esa materia
                random_curso = curses[i][r]
                horario.clases.append(random_curso)
                curses[i].remove(random_curso)
                cupos -= 1
            
            if(len(horario.clases) == len(materias)):
                break
                                             
        horario.updateFitness()
        horario.id = len(particulas)
        particulas.append(horario) 
        
    return particulas




# Get all clases of each materia in html and convert them into objects
cursos, cupos = convertToObjects(getCourses(materias)) 
particulas = genera_aleatorio(cupos, cursos)

for i in range(1):
    particulas.extend(genera_aleatorio(cupos, cursos))
poblacion = len(particulas)
ng = particulas

sys.stdout.flush() 
print(poblacion)

# Algoritmo genetico
for i in range(generaciones):
    
    hijos = []
    counter = 0
      
    for n in range(len(ng)):
        if(len(ng[n].clases) == len(materias) and ng[n].fitness == 200):
            counter += 1
   
    msg = {'type':'status','body':i+1}

    sys.stdout.flush() 
    print(json.dumps(msg))
    #print(i)
        
    
    for j in range(0, poblacion, 2):
        
        if (len(ng) == 0):
            break
        if(len(ng) == 1):
            aux = ng[0]
            ng.remove(ng[0])
            hijos.append(aux)
            break
        
        r1 = random.randint(0, len(ng)-1)
        r2 = 0

        if (len(ng) == 2):
            r1 = 0
            r2 = 1
        else:
            r1 = seleccion(ng) # Escoger en base a a el fitness
            r2 = r1 
            while r1 == r2:
                r2 = seleccion(ng)
                #if(random.randint(0, 1)):
                r2 = random.randint(0, (len(ng)-1))
        if(r1 == None or r2 == None):
            r1 = 0
            r2 = 1
            
        a = ng[r1]
        b = ng[r2]
        ng.remove(a)
        ng.remove(b)
        
        # Recombinacion        
        res1, res2 = recombina(a, b)
        
        
        #mutacion
        if(random.randint(0, 999999) == 250):
            victima = 0
            for i in range(len(ng)-1):
                if(len(ng) > 0):
                    if(ng[i].fitness > 1):
                        victima = i
                        break
                
            victima_horario = ng[victima]
            ng.remove(victima_horario)
            
            recombinaMutacion(res1, res2, victima_horario)
            hijos.append(victima_horario)
        
        hijos.append(res1)
        hijos.append(res2)  
    
    ng = hijos
    ng.sort(key=lambda x: x.fitness)

ng = ng[::-1]
buenos = []

for h in ng:
    if(len(h.clases_sinColition) == len(materias)):
        buenos.append(h)

buenos.sort(key=lambda x: x.fitness)
buenos = buenos[::-1]
# Devolver un arreglo de cadenas


if (len(buenos) < 300):
    for i in range(len(buenos)):
        #f.write(h.showString())     
        msg = {'type':'horario','body':buenos[i].showString(),'key':i}
        sys.stdout.flush() 
        print(json.dumps(msg))
#f.close()
else:
    for i in range(300):
        #f.write(h.showString())     
        msg = {'type':'horario','body':buenos[i].showString(),'key':i}
        sys.stdout.flush() 
        print(json.dumps(msg))  

msg = {'type':'status','body':'finished'}
sys.stdout.flush() 
print(json.dumps(msg))

