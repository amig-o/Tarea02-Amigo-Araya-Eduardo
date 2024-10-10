import requests
import time
import getopt
import sys
import subprocess

def get_fabricante(direccion_mac):
    url = f"https://api.maclookup.app/v2/macs/{direccion_mac}"
    try:
        tiempo1 = time.time()
        respuesta = requests.get(url)
        tiempo2 = time.time()
        tiempo_respuesta = (tiempo2 - tiempo1) * 1000

        if respuesta.status_code == 200:
            fabricante = respuesta.json().get('company', 'Fabricante no encontrado')
        else:
            fabricante = None  #En caso de error
    except requests.RequestException as e:
        print(f"Error en la consulta: {e}")
        return None, None

    return fabricante, tiempo_respuesta


def obtener_tabla_arp():
    #Ejecuta -arp a
    resultado = subprocess.run(['arp', '-a'], capture_output=True, text=True)
    
    #Omitir las primeras dos lineas de arp -a
    lineas = resultado.stdout.splitlines()[3:]  # Ignorar las primeras 2 líneas

    #lista de direcciones mac en la tabla arp
    direcciones_mac = []
    for linea in lineas:
        partes = linea.split()
        if len(partes) > 1:
            mac = partes[1]
            direcciones_mac.append(mac)
    return direcciones_mac


    

def mostrar_ayuda():
    print("""
Use: python OUILookup.py --mac <mac> | --arp | [--help]
  --mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.
  --arp: muestra los fabricantes de los hosts disponibles en la tabla ARP.
  --help: muestra este mensaje y termina.
""")

def main(argv):
    mac = None
    arp = False

    try:
        #Definir los parámetros
        opts, args = getopt.getopt(argv, "hm:a", ["help", "mac=", "arp"])
    except getopt.GetoptError:
        mostrar_ayuda()
        sys.exit(2)

    # Procesar los argumentos
    for opt, arg in opts:
        if opt in ("--help"):
            mostrar_ayuda()
            sys.exit()
        elif opt in ("--mac"):
            mac = arg
        elif opt in ("--arp"):
            arp = True

    # Opciones
    if mac:
        fabricante, tiempo_respuesta = get_fabricante(mac)
        if fabricante:
            print(f"""
Direccion MAC        : {mac}
Fabricante           : {fabricante}
Tiempo de respuesta  : {tiempo_respuesta:.0f} ms""")
        else:
            print(f"""
Direccion MAC        : {mac}
Fabricante           : Not found
Tiempo de respuesta  : {tiempo_respuesta:.0f} ms""")
    elif arp:
        #bbtener la tabla ARP y procesar cada direccion MAC
        direcciones_mac = obtener_tabla_arp()
        print("MAC // Fabricante")
        for mac in direcciones_mac:
            fabricante, tiempo_respuesta = get_fabricante(mac)
            if fabricante:
                print(f"""{mac} // {fabricante}""")
            else:
                print(f"{mac} // Fabricante no encontrado")
    else:
        mostrar_ayuda()
        sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])
