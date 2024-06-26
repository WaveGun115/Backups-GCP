#Modulos para directorios, manejar archivos json y ejecutar comandos
import os
import json
import subprocess
#Modulos para enviar correos
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#Modulo fecha
import datetime


#FUNCIONES
def extraerLog():
    contenido_extraido = ""
    encontrado = False

    #Ruta del log, es necesario crearlo anteriormente
    with open("log.txt", "r") as archivo:
        for linea in archivo:
            if encontrado:
                contenido_extraido += linea
            elif "Proyectos y llaves validadas. Continuando con el proceso ..." in linea:
                encontrado = True
    return contenido_extraido

def enviaCorreo():
    contenidoLog = extraerLog()

    # Obtener la fecha actual
    fechaActual = datetime.datetime.now()
    anio = str(fechaActual.year)
    mes = str(fechaActual.month).zfill(2)
    dia = str(fechaActual.day).zfill(2)
    fechaFormato = dia + "/" + mes + "/" + anio
    
    # Configuración del servidor SMTP
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Puerto para SMTP (TLS)

    # Credenciales de correo electrónico
    sender_email = 'remitente@gmail.com'
    sender_password = 'contraseña generada en gmail'

    #Lista de distribución opcional (Multiples correos)
    #destinatarios = ['correos']

    # Destinatario y contenido del correo electrónico
    recipient_email = 'destinatariop@gmail.com'
    subject = 'Reporte Snapshots ' + fechaFormato
    body = contenidoLog

    # Configurar el correo electrónico
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email #', '.join(destinatarios)
    message['Subject'] = subject

    # Agregar el cuerpo del mensaje
    message.attach(MIMEText(body, 'plain'))

    # Iniciar la conexión SMTP
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Habilitar el cifrado TLS
        server.login(sender_email, sender_password)
        
        # Enviar correo electrónico
        server.sendmail(sender_email, recipient_email, message.as_string())
        #print('Correo electrónico enviado exitosamente.')
        
    except Exception as e:
        print('Error al enviar el correo electrónico:')
        print(e)
        
    finally:
        # Cerrar la conexión SMTP
        server.quit()

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
    
    #Etiqueta para filtrar los discos que coincidan
    etiqueta = "labels.backupw=yes"
    comandoName = subprocess.run(['gcloud', 'compute', 'disks', 'list', '--project', proyecto, '--filter', etiqueta, '--format', 'value(name)'], capture_output=True, text=True, check=True)
    
    if comandoName.returncode == 0:
        #print("Exito de comando")
        #Dar formato al resultado del comando
        nombreDiscos = comandoName.stdout.strip().split('\n')
        print("Lista de discos: ")
        for lista in nombreDiscos:
            print(lista)
        
        #Comando para listar las zonas de los discos
        comandoZone = subprocess.run(['gcloud', 'compute', 'disks', 'list', '--project', proyecto, '--filter', etiqueta, '--format', 'value(zone)'], capture_output=True, text=True, check=True)
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
    #result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], capture_output=True, text=True, check=True)
    # Obtener el valor del proyecto de la salida capturada
    #proyecto = result.stdout.strip()
    #print("PROYECTO ACTUAL: ", proyecto)

    #Obtener fecha actual para nomenclatura
    fechaActualD = datetime.datetime.now()
    anio = str(fechaActualD.year)
    mes = str(fechaActualD.month).zfill(2)
    dia = str(fechaActualD.day).zfill(2)
    fechaFormato = dia + mes + anio

    #Agregar etiqueta al snapshot
    etiquetaSemanal = "backupw=weekly"

    #Variable con propósito de contador (índice)
    i = 0
    #Recorremos el arreglo de names que contiene los nombres de los discos
    for nom in names:
        #Split a variable zonas
        location = zones[i].split("-")
        locationSplit = location[0] + "-" + location[1]
        
        #Creación de la nomenclatura para nombre de los snapshots
        nomenclatura = f"snapshot-{nom}-semanal-{fechaFormato}"
        
        #Comando para crear el snapshot
        subprocess.run(['gcloud', 'compute', 'disks', 'snapshot', nom, '--labels', etiquetaSemanal, '--snapshot-names', nomenclatura, '--zone', zones[i], '--storage-location', locationSplit], check=True)    
        
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
                
                #Función para obtener los nombres y zonas de los discos
                nombres, zonas = listarDiscos(proyectos[i])
                
                #Condicional IF para saber si obtuvimos datos en los arreglos anteriormente asignados
                if nombres[0] != '' and zonas[0] != '':
                    print("Proyecto ", proyectos[i], ":")
                    crearSnapshots(nombres, zonas)
                else:
                    print("El proyecto", proyectos[i], "no tiene discos que cumplan con las etiquetas semanales requeridas.")
                #Incrementamos el contador para seguir recorriendo el arreglo proyectos
                i = i+1
            #print("Respaldos semanales finalizados exitosamente. ")
            #Agregar el log al correo
            enviaCorreo()