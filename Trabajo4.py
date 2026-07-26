#Creamos la base para las clases abstractas

from abc import ABC, abstractmethod

#Se guardaran los logs y eventos en un archivo

def guardar_logs(mensaje):
    archivo = open("logs.txt", "a", encoding="utf-8")
    archivo.write(mensaje + "\n")
    archivo.close()
    
#Errores propios para excepciones personalizadas

class DatosInvalidos(Exception):
    pass

class ServicioNoDisponible(Exception):
    pass

#Creamos la clase base Abstracta que usaran las demas

class Entidad(ABC):
   @abstractmethod
   def describir(self):
       pass
   
#Cliente que representara a la persona y sus datos

class Cliente(Entidad):
    def __init__(self, nombre, correo):
        if nombre == "":
            raise DatosInvalidos("El nombre no puede estar vacio")
        if "@" not in correo:
            raise DatosInvalidos("El correo usado es invalido")
        self.nombre = nombre
        self.correo = correo
        
    def describir(self):
        return f"Cliente: {self.nombre} ({self.correo})"
    
#clase abstracta para el servicio para los demas modelos de servicio

class Servicio(Entidad):
    def __init__(self, nombre, precio, disponible):
        if precio <= 0:
            raise DatosInvalidos("El Precio no puede ser 0")
        self.nombre = nombre
        self.precio = precio
        self.disponible = disponible
        
    @abstractmethod
    def calcular_costo(self,cantidad):
        pass

#Devolver el nombre del servicio
    def describir(self):
        return f"Servicio: {self.nombre}"
    
#Primer servicio = RESERVAR SALA POR HORA

class ReservaSala(Servicio):
    def calcular_costo(self, horas):
        return self.precio * horas
    
#Segundo servicio = alquiler de los equipos

class AlquilarEquipo(Servicio):
    def calcular_costo(self, horas):
        return (self.precio)
    
#Tercer servicio para asesoria
    
class Aseroria(Servicio):
    def calcular_costo(self, sesiones):
        return self.precio  * sesiones * 2

#Reservas para unir cliente con el servicio requerido

class Reserva(Entidad):
    def __init__(self,cliente, servicio, cantidad):
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad = cantidad
        self.estado = "pendiente" 

    def confirmar(self):
        if self.servicio.disponible == False:
            raise ServicioNoDisponible("El servicio no se encuentra disponible")
        self.estado == "Confirmado"
    
    def calcular_total(self):
        costo = self.servicio.calcular_costo(self.cantidad)
        return costo
    
    def describir(self):
        return f"Reserva de {self.cliente.nombre} - {self.estado}"

#Manejo de errores

#registraar clientes

def registrar_clientes(nombre, correo):
    print("Registando cliente", nombre)
    try:
        cliente = Cliente(nombre,correo)
    except DatosInvalidos as error:
        print(" ERROR:", error)
        guardar_logs("error al crear cliente: " + str(error))
    else:
        print(" Correcto:", cliente.describir())
        guardar_logs("cliente creado:" + nombre)
        return cliente
    finally:
        print(" (fin del intento)")

#registrar reservas

def hacer_reservas(cliente, servicio, cantidad):
    print("Reserva de", servicio.nombre)
    try:
        reserva = Reserva(cliente, servicio, cantidad)
        reserva.confirmar()
        total = reserva.calcular_total()
    except ServicioNoDisponible as error:
        print(" Error:", error)
        guardar_logs("Reserva ha fallado" + str(error))
    except Exception as error:
        print(" Error inesperado: ", error)
        guardar_logs("Error inesperado: " + str(error))
    else:
        print("Tota a pagar: $ " + str(total))
        guardar_logs("Reserva completada. total a pagar" + str(total))
    finally:
         print(" (intento finalizado)")
         
#Programa principal

print(" Software FJ Reservas")
guardar_logs("Inicio")

#Creamos la disponibilidad y cantidades

sala = ReservaSala("Sala Ejecutiva", 300000, True)
equipo = AlquilarEquipo("SmartBoard", 100000, True)
asesoria = Aseroria("Consultorias", 200000, True)
equipos_dañados = AlquilarEquipo("Laptop Antigua", 50000, False)

#cliente valido
Camilo = registrar_clientes("Camilo", "Camilo1@hotmail.com")

#cliente sin arroba (falla)
registrar_clientes("Sutano", "sutano-gmail.com")

#cliente sin nombre (falla)
registrar_clientes("", "x@mail.com")

#cliente valido
Carolina = registrar_clientes("Carolina", "caropa@unad.edu.com")

#reserva de sala exitosa
hacer_reservas(Camilo, sala, 3)

#reserva de equipo
hacer_reservas(Camilo, equipo, 2)

#reserva de asesoria exitosa
hacer_reservas(Carolina, asesoria, 1)

#reserva de equipo no disponible
hacer_reservas(Carolina, equipos_dañados, 1)

#otra reserva de sala
hacer_reservas(Carolina, sala, 5)

#reserva de asesoria con descuento
hacer_reservas(Camilo, asesoria, 2)

print("FIN")
print("Revisa el archivo 'eventos.txt'")
guardar_logs("FIN")

