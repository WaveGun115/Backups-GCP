import os
import json
import subprocess

#MODULOS
def buscarLlaves():
    #Obtener la ruta de la carpeta que contiene las llaves
    rutaActual = os.getcwd() + "/key"
    
    #Listamos los archivos existgentes en la carpeta
    archivos = os.listdir(rutaActual)
    
    #Arreglo para guardar los nombres de archivos
    archivosJson = []
    for archivo in archivos:
        #Si termina el archivo con .json
        if archivo.endswith('.json'):
            #Guardamos el nombre del archivo en el arreglo
            archivosJson.append(archivo)
    return archivosJson

def crearProyectos(archivos):
    #Arreglo para guardar los nombres de los proyectos
    proyectos = []
    for archivo in archivos:
        #Asignar la ruta del archivo json a la variable
        rutaActual = os.getcwd() + "/key/" + archivo
        
        #Código para leer el contenido del json
        with open(rutaActual, 'r') as file:
            contenido = file.read()
            datosJson = json.loads(contenido)
            #Obtener el valor de project_id
            projectId = datosJson.get('project_id')
            #Guardamos el project_id en el arreglo
            proyectos.append(projectId)
    validacion = validarProyectos(proyectos)
    if validacion != '':
        return validacion
    else:
        return proyectos

def validarProyectos(proyectos):
    # Crear un diccionario para contar la frecuencia de cada proyecto
    frecuencia_proyectos = {}

    for proyecto in proyectos:
        # Incrementar el contador para el proyecto actual en el diccionario
        frecuencia_proyectos[proyecto] = frecuencia_proyectos.get(proyecto, 0) + 1

    # Verificar si algún proyecto se repite más de una vez
    proyecto_repetido = None

    for proyecto, frecuencia in frecuencia_proyectos.items():
        if frecuencia > 1:
            proyecto_repetido = proyecto
            break

    # Escribir el nombre del proyecto repetido, si hay alguno
    if proyecto_repetido is not None:
        return "el proyecto repetido es " + proyecto_repetido
    else:
        return ''

def listarDiscos(proyecto):
    arrZonasLimpias = ['']
    
    #Comando para listar los nombres de los discos --filter="labels.backupw=weekly"
    comandoName = subprocess.run(['gcloud', 'compute', 'disks', 'list', '--project', proyecto, '--filter', 'labels.backupw=weekly OR labels.weekly-backup=yes', '--format', 'value(name)'], capture_output=True, text=True, check=True)
    
    if comandoName.returncode == 0:
        print("Exito de comando")
        #Dar formato al resultado del comando
        nombreDiscos = comandoName.stdout.strip().split('\n')
        
        #Comando para listar las zonas de los discos
        comandoZone = subprocess.run(['gcloud', 'compute', 'disks', 'list', '--project', proyecto, '--filter', 'labels.backupw=weekly OR labels.weekly-backup=yes', '--format', 'value(zone)'], capture_output=True, text=True, check=True)
        #Dar formato al resultado del comando
        zonasDiscos = comandoZone.stdout.strip().split('\n')
        
        #Si las consultas anteriores SI traen datos continuamos con limpiar las zonas
        if nombreDiscos[0] != '' and zonasDiscos[0] != '':
            #Llamamos a la función limpiarZonas y asignamos el arreglo resultante a la variable arrZonasLimpias
            arrZonasLimpias = limpiarZonas(zonasDiscos)
    else:
        print("Error en el comando...")
        print(comandoName.stderr)
    
    return nombreDiscos, arrZonasLimpias
    
def limpiarZonas(zonas):
    arrZonas = []
    
    #Recorrer el arreglo de las zonas
    for cadena in zonas:
        #Código para eliminar toda la cadena de texto anterior a "zonez/" esto para obtener la zona del disco
        valores = cadena.split("/")        
        indiceZonas = valores.index("zones") + 1
        valoresDespuesZones = valores[indiceZonas]
        resultado = (valoresDespuesZones)
        #Guardamos la zona en el arreglo
        arrZonas.append(resultado)
    return arrZonas

def crearSnapshots(names, zones):
    #Comando para obtener el proyecto actual en el que se está trabajando
    result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], capture_output=True, text=True, check=True)
    # Obtener el valor del proyecto de la salida capturada
    proyecto = result.stdout.strip()
    print("PROYECTO ACTUAL: ", proyecto)

    #Variable con propósito de contador (índice)
    i = 0
    #Recorremos el arreglo de names que contiene los nombres de los discos
    for nom in names:
        #Creación de la nomenclatura para nombre de los snapshots
        nomenclatura = f"{nom}-snapshot"
        
        #Comando para crear el snapshot
        subprocess.run(['gcloud', 'compute', 'disks', 'snapshot', nom, '--snapshot-names', nomenclatura, '--zone', zones[i]], check=True)
        print(f"Snapshot creado para el disco {nom}: {nomenclatura}")
        #Incrementamos el contador para recorrer el for
        i = i+1

#Código main
if __name__ == '__main__':
    #Función para encontrar los archivos json key para realizar la autenticación de service account
    llaves = buscarLlaves()
    print("LLAVES ENCONTRADAS: ")
    for x in llaves:
        print(x)
    
    #Condicional IF para saber si la función nos regresó archivos json localizados en el directorio
    if not llaves:
        print("La carpeta no contiene ningún archivo json.")
    else:
        #Si hay llaves por lo tanto llamamos a la función crearProyecto para obtener los nobmres de los proyectos
        proyectos = crearProyectos(llaves)
        
        #Validar resputa de la validación
        if "el proyecto repetido es" in proyectos:
            print("")
            print("No es posible continuar, llave de proyecto duplicada, ", proyectos)
        else:
            print("Proyectos y llaves validadas. Continuando con el proceso ...")
            #Variable contador (índice)
            i = 0
            #Recorremos el arreglo de llaves obtenidas anteriormente
            for llave in llaves:
                #Asigamos la ruta de cada llave json a la variable para realizar la autenticación service-account
                rutaJson = os.getcwd() + "/key/" + llave

                #Print para dar espaciado
                print("")
                # Ejecutar el comando 'gcloud auth activate-service-account' para autenticar con la cuenta de servicio
                subprocess.run(['gcloud', 'auth', 'activate-service-account', '--key-file', rutaJson, '--project', proyectos[i]], check=True)
                
                #Función para obtener los nombrees y zonas de los discos
                nombres, zonas = listarDiscos(proyectos[i])
                
                #Condicional IF para saber si obtuvimos datos en los arreglos anteriormente asignados
                if nombres[0] != '' and zonas[0] != '':
                    print("Iniciando proceso de snapshots en el proyecto ", proyectos[i], " ...")
                    crearSnapshots(nombres, zonas)
                else:
                    print("El proyecto ", proyectos[i], "no tiene discos que cumplan con las etiquetas requeridas.")
                #Incrementamos el contador para seguir recorriendo el arreglo proyectos
                i = i+1
            print("Respaldos semanales finalizados. ")