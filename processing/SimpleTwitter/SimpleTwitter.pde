/**
* @author Victor Torre (aka ehooo) 
* Hace falta tener instalado el plugin "oauthP5" by New York Times R&D Lab (achang), 2012 www.nytlabs.com/oauthp5
* 
*/

final String CONSUMER_KEY = "";
final String CONSUMER_SECRET = "";
final String ACCESS_TOKEN = "";
final String ACCESS_TOKEN_SECRET = "";

SimpleTwitterLib twitter = new SimpleTwitterLib(CONSUMER_KEY, CONSUMER_SECRET);
twitter.auth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET);
twitter.update("i wish");
ArrayList<String> twees = twitter.get_tweets();
println("> Lista de deseos:");
for(String twee:twees)
  println(twee);
println();
println("> Y la lista de sus enlaces:");
ArrayList<String> urls = twitter.get_urls();
for(String url:urls)
  println(url);
