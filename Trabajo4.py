# ==========================================================
# EJERCICIO 1: SISTEMA INTEGRAL SOFTWARE FJ
# ==========================================================

from abc import ABC, abstractmethod

# ----------------------------------------------------------
# 1. ARCHIVO DE LOGS Y EXCEPCIONES PERSONALIZADAS
# ----------------------------------------------------------

def guardar_logs(mensaje):
    """Guarda eventos y errores en un archivo de texto persistente."""
    try:
        with open("logs.txt", "a", encoding="utf-8") as archivo:
            archivo.write(mensaje + "\n")
    except Exception as e:
        print(f"Error al escribir en el archivo de log: {e}")

# Jerarquía de Excepciones Personalizadas
class SoftwareFJError(Exception):
    """Excepción base del sistema."""
    pass

class DatosInvalidos(SoftwareFJError):
    """Lanzada cuando un dato de entrada no cumple con los criterios de validación."""
    pass

class ServicioNoDisponible(SoftwareFJError):
    """Lanzada cuando se intenta reservar un servicio inactivo o sin stock."""
    pass

class EstadoReservaError(SoftwareFJError):
    """Lanzada cuando la operación no coincide con el estado de la reserva."""
    pass


# ----------------------------------------------------------
# 2. CLASE BASE ABSTRACTA Y ENTIDADES
# ----------------------------------------------------------

class Entidad(ABC):
    """Clase abstracta base para las entidades generales del sistema."""
    
    @abstractmethod
    def describir(self):
        pass


class Cliente(Entidad):
    """Representa a un cliente del sistema con datos encapsulados."""
    
    def __init__(self, nombre, correo):
        self.nombre = nombre
        self.correo = correo

    # Encapsulación con validaciones
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or valor.strip() == "":
            raise DatosInvalidos("El nombre del cliente no puede estar vacio.")
        self._nombre = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if "@" not in valor or "." not in valor:
            raise DatosInvalidos(f"El correo '{valor}' no tiene un formato valido.")
        self._correo = valor

    def describir(self):
        return f"Cliente: {self.nombre} ({self.correo})"


# ----------------------------------------------------------
# 3. JERARQUÍA DE SERVICIOS (HERENCIA Y POLIMORFISMO)
# ----------------------------------------------------------

class Servicio(Entidad):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""
    
    def __init__(self, nombre, precio, disponible=True):
        if precio <= 0:
            raise DatosInvalidos("El precio del servicio debe ser mayor a cero.")
        self.nombre = nombre
        self.precio = precio
        self.disponible = disponible

    @abstractmethod
    def calcular_costo(self, cantidad, descuento=0.0, impuesto=0.19):
        """Método polimórfico con soporte para parámetros opcionales (Sobrecarga)."""
        pass

    def describir(self):
        estado = "Disponible" if self.disponible else "No Disponible"
        return f"Servicio: {self.nombre} | Tarifa: ${self.precio} | Estado: {estado}"


class ReservaSala(Servicio):
    """Servicio 1: Reserva de salas por horas."""
    
    def calcular_costo(self, horas, descuento=0.0, impuesto=0.19):
        if horas <= 0:
            raise DatosInvalidos("La cantidad de horas debe ser mayor a 0.")
        subtotal = self.precio * horas
        subtotal_descuento = subtotal * (1 - descuento)
        total = subtotal_descuento * (1 + impuesto)
        return round(total, 2)


class AlquilarEquipo(Servicio):
    """Servicio 2: Alquiler de equipos de cómputo/tecnológicos."""
    
    def calcular_costo(self, dias, descuento=0.0, impuesto=0.19):
        if dias <= 0:
            raise DatosInvalidos("La cantidad de días de alquiler debe ser mayor a 0.")
        seguro = 15000 * dias 
        subtotal = (self.precio * dias) + seguro
        subtotal_descuento = subtotal * (1 - descuento)
        total = subtotal_descuento * (1 + impuesto)
        return round(total, 2)


class Asesoria(Servicio):
    """Servicio 3: Asesorías especializadas en software."""
    
    def calcular_costo(self, sesiones, descuento=0.0, impuesto=0.19):
        if sesiones <= 0:
            raise DatosInvalidos("La cantidad de sesiones debe ser mayor a 0.")
        subtotal = self.precio * sesiones
        subtotal_descuento = subtotal * (1 - descuento)
        total = subtotal_descuento * (1 + impuesto)
        return round(total, 2)


# ----------------------------------------------------------
# 4. CLASE RESERVA Y OPERACIONES
# ----------------------------------------------------------

class Reserva(Entidad):
    """Integra Cliente, Servicio y la gestión del proceso de reserva."""
    
    def __init__(self, cliente, servicio, cantidad):
        if cliente is None:
            raise DatosInvalidos("No se puede crear una reserva sin un cliente valido.")
        if servicio is None:
            raise DatosInvalidos("No se puede crear una reserva sin un servicio valido.")
            
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad = cantidad
        self.estado = "PENDIENTE"

    def confirmar(self):
        if not self.servicio.disponible:
            raise ServicioNoDisponible(f"El servicio '{self.servicio.nombre}' no se encuentra disponible.")
        
        if self.estado == "CONFIRMADO":
            raise EstadoReservaError("La reserva ya se encuentra confirmada.")
            
        self.estado = "CONFIRMADO"

    def cancelar(self):
        if self.estado == "CANCELADO":
            raise EstadoReservaError("La reserva ya se encuentra cancelada.")
        self.estado = "CANCELADO"

    def calcular_total(self, descuento=0.0, impuesto=0.19):
        try:
            return self.servicio.calcular_costo(self.cantidad, descuento, impuesto)
        except Exception as e:
            raise SoftwareFJError("Fallo al liquidar el costo total de la reserva.") from e

    def describir(self):
        return f"Reserva [{self.estado}] - Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre}"


# ----------------------------------------------------------
# 5. FUNCIONES DE CONTROL (GESTIÓN DE TRY/EXCEPT/ELSE/FINALLY)
# ----------------------------------------------------------

def registrar_cliente(nombre, correo):
    print(f"\n[OPERACION] Intentando registrar cliente: '{nombre}'")
    try:
        cliente = Cliente(nombre, correo)
    except DatosInvalidos as error:
        print(f"  [ERROR]: {error}")
        guardar_logs(f"ERROR - Fallo registro cliente '{nombre}': {error}")
        return None
    else:
        print(f"  [OK]: {cliente.describir()}")
        guardar_logs(f"INFO - Cliente registrado correctamente: {cliente.nombre}")
        return cliente
    finally:
        print("  --> Finalizado proceso de registro de cliente.")


def hacer_reserva(cliente, servicio, cantidad, descuento=0.0):
    nombre_cli = cliente.nombre if cliente else "Cliente Desconocido"
    nombre_ser = servicio.nombre if servicio else "Servicio Desconocido"
    
    print(f"\n[OPERACION] Procesando reserva para {nombre_cli} - Servicio: {nombre_ser}")
    try:
        reserva = Reserva(cliente, servicio, cantidad)
        reserva.confirmar()
        total = reserva.calcular_total(descuento=descuento)
    except (ServicioNoDisponible, DatosInvalidos, EstadoReservaError) as error:
        print(f"  [ERROR EN RESERVA]: {error}")
        guardar_logs(f"ERROR - Fallo en reserva para '{nombre_cli}': {error}")
        return None
    except SoftwareFJError as error:
        print(f"  [ERROR DE SISTEMA]: {error} (Causa origen: {error.__cause__})")
        guardar_logs(f"ERROR GRAVE - {error} | Origen: {error.__cause__}")
        return None
    except Exception as error:
        print(f"  [ERROR INESPERADO]: {error}")
        guardar_logs(f"CRITICAL - Error no controlado: {error}")
        return None
    else:
        print(f"  [OK]: Reserva confirmada. Total a pagar: ${total:,.2f}")
        guardar_logs(f"INFO - Reserva completada para {nombre_cli}. Total: ${total}")
        return reserva
    finally:
        print("  --> Finalizado procesamiento de solicitud de reserva.")


# ----------------------------------------------------------
# 6. PROGRAMA PRINCIPAL (SIMULACIÓN DE 10 OPERACIONES)
# ----------------------------------------------------------

if __name__ == "__main__":
    print("==========================================================")
    print("      SOFTWARE FJ - SISTEMA INTEGRAL DE RESERVAS")
    print("==========================================================")
    guardar_logs("--- INICIO DE SESION DEL SISTEMA ---")

    # Creación de Servicios
    sala_ejecutiva = ReservaSala("Sala Ejecutiva", 300000, disponible=True)
    smartboard = AlquilarEquipo("SmartBoard 4K", 100000, disponible=True)
    consultoria = Asesoria("Consultoria Arquitectura", 200000, disponible=True)
    laptop_danada = AlquilarEquipo("Laptop Vieja", 50000, disponible=False)

    # --- SIMULACIÓN DE 10 OPERACIONES ---

    # Operación 1: Registro correcto
    c1 = registrar_cliente("Camilo Cruz", "camilo1@hotmail.com")

    # Operación 2: Correo sin punto
    c_fallo1 = registrar_cliente("Sutano Perez", "sutano-gmailcom")

    # Operación 3: Nombre vacío
    c_fallo2 = registrar_cliente("", "x@mail.com")

    # Operación 4: Registro correcto de segundo cliente
    c2 = registrar_cliente("Carolina Paez", "caropa@unad.edu.co")

    # Operación 5: Reserva exitosa (Sala por 3 horas)
    r1 = hacer_reserva(c1, sala_ejecutiva, cantidad=3)

    # Operación 6: Reserva exitosa con descuento
    r2 = hacer_reserva(c2, consultoria, cantidad=2, descuento=0.10)

    # Operación 7: Reserva fallida (Servicio NO disponible)
    r3 = hacer_reserva(c2, laptop_danada, cantidad=1)

    # Operación 8: Reserva fallida (Horas = -2)
    r4 = hacer_reserva(c1, smartboard, cantidad=-2)

    # Operación 9: Reserva fallida (Cliente no registrado)
    r5 = hacer_reserva(c_fallo1, sala_ejecutiva, cantidad=1)

    # Operación 10: Re-confirmación no permitida
    print("\n[OPERACION] Intentando re-confirmar una reserva ya procesada...")
    try:
        if r1:
            r1.confirmar()
    except EstadoReservaError as error:
        print(f"  [ERROR DE ESTADO]: {error}")
        guardar_logs(f"ERROR - Operación no permitida: {error}")
    finally:
        print("  --> Finalizado intento de re-confirmacion.")

    print("\n==========================================================")
    print("  SIMULACION COMPLETADA CON EXITO SIN CAIDAS DEL PROGRAMA")
    print("  Consulte el archivo 'logs.txt' para verificar los registros.")
    print("==========================================================")
    guardar_logs("--- FIN DE SESION DEL SISTEMA ---")