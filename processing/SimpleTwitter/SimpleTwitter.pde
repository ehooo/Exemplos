/**
* @author Victor Torre (aka ehooo) 
* Hace falta tener instalado el plugin "oauthP5" by New York Times R&D Lab (achang), 2012 www.nytlabs.com/oauthp5
* 
*/

final String CONSUMER_KEY = "";
final String CONSUMER_SECRET = "";
final String ACCESS_TOKEN = "";
final String ACCESS_TOKEN_SECRET = "";

final String BUSQUEDA = "\"i wish\"";

SimpleTwitterLib twitter = null;

//Incremento para el eje Y
final int gravedad=1;
//Clave para saver si ya hemos "gastado" todos los Tweets consultados
int act_tweet = 0;

//Clase para almacenar la posicion del Tweet
class Posicion{
  public int x, y;
  public Posicion(int x, int y){
    this.x = x;
    this.y = y;
  }
}

//Listado interno de Tweets/Posicion
final HashMap<String, Posicion> tuit = new HashMap<String, Posicion>();
//Parametros extra para la busqueda
final HashMap<String, String> filtro = new HashMap<String, String>();
//Espacio de linea
final int X_WIN=400, Y_WIN=400, WORD_H=10;
//Esta posicion es el tope de la pila
Posicion inferior = new Posicion(0,Y_WIN);

void setup() {
  //Inicializamos el filtro
  filtro.put("count",String.valueOf(15));//Numero de Tweets por busqueda
  filtro.put("geocode","37.781157,-122.398720,1000km");//Posicion GPS y area para la busqueda
  //Para una respuesta mas rapida  datos extras, pero no podremos acceder a las urls
  //filtro.put("include_entities","false");

  //Creamos la ventana
  size(X_WIN, Y_WIN);
  twitter = new SimpleTwitterLib(CONSUMER_KEY, CONSUMER_SECRET);
  twitter.auth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET);
  //Hacemos la primera busqueda para no hacer esperas luego
  twitter.update(BUSQUEDA, filtro);
  for(String uri: twitter.get_media_urls()){
    print(uri);
  }
}

void draw(){ 
  background(0);
  fill(255);

  //Si no hay Tweets que mostrar no modificamos nada
  if(tuit.size()<=0) return;

  /*
   * Equivale a:
   * String claves[] = tuit.keySet();
   * for(int i=0;i<claves.length; i++){
   *   String twee = clave[i];
   * }
   */
  for(String twee : tuit.keySet()){
    //Cogemos la posicion actual del tuit
    Posicion p = tuit.get(twee);
    if(p.y < inferior.y)
      p.y += gravedad;
    else if(p.y >= inferior.y)
      inferior.y = p.y-WORD_H;
    //Mostramos el texto en su posicion
    text(twee, p.x, p.y);
  }
}

void mousePressed()
{
  //Cogemos la lista de Tweets
  ArrayList<String> twees = twitter.get_tweets();
  //Si ya estamos en el ultimo Tweet, cargamos la nueva lista
  if(twees.size() <= act_tweet){
    twitter.update(BUSQUEDA, filtro);
    twees = twitter.get_tweets();
    act_tweet = 0;
  }
  //Insertamos el nuevo Tweet con su posicion inicial
  String nuevo_tuit = twees.get(act_tweet);
  tuit.put( nuevo_tuit , new Posicion(180, 0) );
  //Incrementamos la posicion para leer el proximo
  act_tweet += 1;
}

