#Modulos para enviar correos
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#Modulo fecha
import datetime

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
    sender_password = 'Contraseña generada en gmail'

    #Lista de distribución opcional (Multiples correos)
    #destinatarios = ['correos']

    # Destinatario y contenido del correo electrónico
    recipient_email = 'destinatario@gmail.com'
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
        
#Código main
if __name__ == '__main__':
    enviaCorreo()