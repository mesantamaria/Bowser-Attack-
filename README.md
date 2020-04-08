Game made for my Advanced Programming class

# Sobre los archivos

- Frontend
	- frontend.py: es para ejecutar el juego completo (interfaz) y contiene las clases de la interfaz de inicio, desarrollo (MiVentana) y final
	- tienda.py: contiene la ventana que se abre al ingresar a la tienda desde el juego

- Backend
	- backend.py: contiene las entidades que se usaron: Character (personaje principal), Enemy (enemigos) son threads y Bomba son threads.
	- colisiones.py: contiene las funciones que se usaron para determinar distancias, colisiones, etc. en la interfaz

- constantes.py: contiene algunas constantes ajustables del juego. Por ejemplo: puedes modificar el factor de velocidad de los enemigos (para hacerlo más fácil) con la constante TIEMPO_VELOCIDAD_ENEMIGOS

- Assets:
	- Contiene las imágenes usadas en diferentes partes de la interfaz (los de p_extra, safe_zone, vida_extra) no se incluyeron
	- bowser: contiene el sprite separado en varias imágenes (JUG PRINCIPAL)
	- clubba: contiene el sprite separado en varias imágenes (ENEMIGOS)


# Sobre ajustes

- Se reajustó el rango de visión de los enemigos en constantes.py. Se puso más grande de lo que era porque se encontró que era muy poco.
- Se reajustó la velocidad de los enemigos. Se disminuyó esta porque se encontró que era muy difícil si los enemigos tenían la misma velocidad que el personaje principal (dependiendo del tamaño obviamente), ya que el jug principal no puede girar tan rápido y avanzar como lo hacen los enemigos. Si se quiere cumplir con lo del enunciado (jugador y enemigos misma velocidad según tamaño)
- GRADOS_ROTACION: le puse que cada vez que se apreta 'a' o 'd' se girara 3 grados, pero si se quiere llegar a cualquier ángulo, se puede reducir este número a 1 grado, pero rotaría más lento.
- El rango de explosión de las bombas también se aumentó en constantes.py


# Cosas no especificadas en el enunciado

- Durante el tiempo (1 segundo) entre ataques, los personajes van a hacer sus movimientos de ataque, cuando dejen de hacerlos significa que se puede atacar de nuevo. Durante este tiempo se pueden mover, por ejemplo si el enemigo es de menor tamaño, va a intentar escapar en ese segundo. 
- Hay sola 1 safe zone por juego
- Al abrir la tienda se pausa el juego, por lo que al cerrarla hay que apretar el boton de pausa para seguir jugando. Eso le da tiempo al jugador de ver lo que estaba haciendo.
- En el enunciado dice que el inventario se "tiene que poder mostrar" durante el juego y eso se puede hacer pulsando la tienda. Vi en una issue que tenía que ser en la misma interfaz del juego, pero la issue era el último día y ya no tenía tiempo para cambiarlo.
- El rango de visión toma la distancia entre los 2 centros (enemigo y jugador principal)
- Si se compra el poder de vida y luego se rellena la vida, se tendrá la vida máxima con el poder. Pero si después de esto en el inventario se reemplaza el poder de vida, la barra de vida quedará sobre 100% porque tiene la vida actual mayor a la vida maxima sin poder.


# Sobre el alcance

- La tienda funciona todo menos el "poder" de aumento de velocidad de ataque (siempre es 1 segundo).
- Los enemigos no se cruzan, chocan. Pero al ocurrir esto a veces se demoran en dejar de chocar, ya que cambian su dirección pero esa "nueva dirección" sigue chocando con otro enemigo, pero después de un tiempo logran "escapar" de esta colisión. A veces falla cuando aparece un enemigo justo en una posición donde se moverá otro enemigo, ahí se quedan pegados en la colisión hasta que mueren (pero no pasa mucho). Antes de aparecer siempre se controla que no aparezca en alguna posición donde haya otro label enemigo
- Preferí que los enemigos si se puedan "cruzar" con los enemigos porque cuando hacía que chocaran, el jugador se frenaba y el enemigo se escapaba en ese tiempo sin atacar, por lo que era muy difícil el juego. Ahora con esto se puede atacar y seguir persiguiendo al enemigo esperando que pase el segundo para atacarlo de nuevo, se puede quedar "sobre el enemigo" para que no se escape. Para hacer que no se crucen, era hacer lo mismo que lo que hago entre enemigos.
- El resto debería estar funcionando correctamente (no se hizo el bonus de desarrollador y multijugador, pero si el de estiloso).
