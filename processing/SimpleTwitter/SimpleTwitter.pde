/**
* @author Victor Torre (aka ehooo) 
* Hace falta tener instalado el plugin "oauthP5" by New York Times R&D Lab (achang), 2012 www.nytlabs.com/oauthp5
* 
*/

final String CONSUMER_KEY = "";
final String CONSUMER_SECRET = "";
final String ACCESS_TOKEN = "";
final String ACCESS_TOKEN_SECRET = "";

SimpleTwitterLib twitter = null;
final int UPDATE_SEC = 60;
int last_update = -1;
int textLine = 60;
int act_tweet = 0;

void setup() {
  size(400, 400);
  textFont(createFont("SanSerif", 16));
  twitter = new SimpleTwitterLib(CONSUMER_KEY, CONSUMER_SECRET);
  twitter.auth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET);
  background(0);
}

void write_line(){
  final ArrayList<String> twees = twitter.get_tweets();
  if(twees.size() <= act_tweet) return;
  final String s = twees.get(act_tweet);
  text(s, 15, textLine);
  textLine += 35;
  act_tweet += 1;
}
void print_all(){
  final ArrayList<String> twees = twitter.get_tweets();
  println("> Lista de deseos:");
  for(String twee:twees)
    println(twee);
  println();
  println("> Y la lista de sus enlaces:");
  final ArrayList<String> urls = twitter.get_urls();
  for(String url:urls)
    println(url);
}

void draw() {
  int actual = millis();
  if( actual-last_update > UPDATE_SEC*1000 || last_update<0){
    last_update = actual;
    act_tweet = 0;
    twitter.update("\"i wish\"");
    print_all();
  }
  write_line();
}