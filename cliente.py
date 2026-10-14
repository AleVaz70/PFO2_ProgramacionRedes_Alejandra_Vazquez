# Cliente en consola para probar la API del PFO 2

import requests
import webbrowser

URL = "http://localhost:5000"

# Session mantiene la cookie de login entre pedidos
sesion = requests.Session()
logueado = False


def registrar():
    usuario = input("Usuario: ").strip()
    contraseña = input("Contraseña: ")
    if not usuario or not contraseña:
        print("Error: usuario y contraseña no pueden estar vacíos.")
        return

    r = sesion.post(f"{URL}/registro", json={"usuario": usuario, "contraseña": contraseña})
    data = r.json() if r.content else {}
    if r.status_code == 201:
        print(f"OK ({r.status_code}): {data.get('mensaje')}")
    else:
        print(f"Error ({r.status_code}): {data.get('error', r.text)}")


def iniciar_sesion():
    global logueado
    usuario = input("Usuario: ").strip()
    contraseña = input("Contraseña: ")
    if not usuario or not contraseña:
        print("Error: usuario y contraseña no pueden estar vacíos.")
        return

    r = sesion.post(f"{URL}/login", json={"usuario": usuario, "contraseña": contraseña})
    data = r.json() if r.content else {}
    if r.status_code == 200:
        logueado = True
        print(f"OK ({r.status_code}): {data.get('mensaje')}")
    else:
        logueado = False
        print(f"Error ({r.status_code}): {data.get('error', r.text)}")


def ver_tareas():
    if not logueado:
        print("Error: primero tenés que iniciar sesión (opción 2).")
        return

    r = sesion.get(f"{URL}/tareas")
    if r.status_code == 200:
        print(f"OK ({r.status_code}): se recibió el HTML de bienvenida.")
        abrir = input("¿Abrir la página en el navegador? (s/n): ").strip().lower()
        if abrir in ("s", "si", "sí", "y"):
            webbrowser.open(f"{URL}/tareas")
            print("Página abierta en el navegador.")
        else:
            print("-" * 40)
            print("¡Bienvenido al Sistema de Gestión de Tareas!")
            print("Accediste correctamente a la sección de tareas.")
            print("-" * 40)
    else:
        data = r.json() if r.headers.get("Content-Type", "").startswith("application/json") else {}
        print(f"Error ({r.status_code}): {data.get('error', r.text)}")



def main():
    while True:
        print("\n1. Registrarse\n2. Iniciar sesión\n3. Ver tareas\n4. Salir")
        opcion = input("Seleccione una opción: ").strip()

        try:
            if opcion == "1":
                registrar()
            elif opcion == "2":
                iniciar_sesion()
            elif opcion == "3":
                ver_tareas()
            elif opcion == "4":
                break
            else:
                print("Opción inválida.")
        except requests.exceptions.ConnectionError:
            print("No se pudo conectar con el servidor. ¿Está encendido?")
        except ValueError:
            print("Error: respuesta inválida del servidor.")


if __name__ == "__main__":
    main()
