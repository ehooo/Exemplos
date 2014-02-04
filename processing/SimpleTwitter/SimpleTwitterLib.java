/**
* @author Victor Torre (aka ehooo) 
* Hace falta tener instalado el plugin "oauthP5" by New York Times R&D Lab (achang), 2012 www.nytlabs.com/oauthp5
* 
*/
import oauthP5.apis.TwitterApi;
import oauthP5.oauth.*;
import java.util.HashMap;
import java.util.ArrayList;
import processing.data.JSONObject;
import processing.data.JSONArray;

public class SimpleTwitterLib{
  public static final String BASE_URL="https://api.twitter.com/1.1/";
  public static final HashMap<String,String> LANGS = new HashMap<String,String>();
  static{
    LANGS.put("aleman","de");
    LANGS.put("turko","tr");
    LANGS.put("ingles","en");
    LANGS.put("esperanto","eo");
    LANGS.put("portugues","pt");
    LANGS.put("italiano","it");
    LANGS.put("castellano","es");
    LANGS.put("galego","gl");
    LANGS.put("catala","ca");
    LANGS.put("euskera","eu");
    LANGS.put("aragones","an");
  }
  public static final String getGeoCode(final double latitude, final double longitude, final int km_radius){
    return String.valueOf(latitude)+","+String.valueOf(longitude)+","+String.valueOf(km_radius)+"km";
  }
  private OAuthService service;
  private Token requestToken=null;
  private Token accessToken=null;
  private int remaining=180;

  private String since_id=null;
  private JSONObject last_search=null;

  public SimpleTwitterLib(final String CONSUMER_KEY, final String CONSUMER_SECRET){
    this.service = new ServiceBuilder()
      .provider(TwitterApi.class)
      .apiKey(CONSUMER_KEY).apiSecret(CONSUMER_SECRET)
      .build();
  }

  public String getUrlAuth(){
    this.requestToken = this.service.getRequestToken();
    return this.service.getAuthorizationUrl(this.requestToken);
  }
  public void auth(final String verifierString){
    Verifier verifier = new Verifier(verifierString);
    this.accessToken = service.getAccessToken(this.requestToken, verifier);
  }
  public void auth(final String ACCESS_TOKEN, final String ACCESS_TOKEN_SECRET){
    this.accessToken = new Token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET);
  }

  public Response send(final String post_url, final HashMap<String,String> post){
    return this.send(post_url, post, Verb.GET, this.accessToken);
  }
  public Response send(final String post_url, final HashMap<String,String> post, Verb method){
    return this.send(post_url, post, method, this.accessToken);
  }
  public Response send(final String post_url, final HashMap<String,String> post, Verb method, final String ACCESS_TOKEN, final String ACCESS_TOKEN_SECRET){
    Token token=null;
    if(ACCESS_TOKEN!=null && ACCESS_TOKEN_SECRET!=null)
      token = new Token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET);
    return this.send(post_url, post, method, token);
  }
  public Response send(final String post_url, final HashMap<String,String> post, Verb method, final Token accessToken){
    OAuthRequest request = new OAuthRequest(method, post_url);
    for(String clave : POST.keySet()){
      if(method == Verb.POST) request.addBodyParameter(clave, POST.get(clave));
      else request.addQuerystringParameter(clave, post.get(clave));
    }
    if(accessToken!=null) this.service.signRequest(accessToken, request);
    Response response = request.send();
    try{
      this.remaining = Integer.parseInt(response.getHeader("X-Rate-Limit-Remaining"));
    }catch(NumberFormatException ex){}
    try{
    		this.last_search = JSONObject.parse(response.getBody());
    }catch(Exception ex){ this.last_search = null; }
    return response;
  }

  public Response update(final String query){
    return this.update(query, null);
  }
  public Response update(final String query, int max){
    HashMap<String,String> post = new HashMap<String,String>();
    post.put("count",String.valueOf(max));
    return this.update(query, post);
  }
  public Response update(final String query, HashMap<String,String> post){
    if(post==null) post = new HashMap<String,String>();
    if(this.since_id!=null) post.put("since_id",this.since_id);
    post.put("result_type","recent");
    Response response = this.search(query, post);
    try{
      this.since_id = this.last_search.getJSONObject("search_metadata").getString("since_id_str");
    }catch(Exception ex){ this.since_id = null; }
    return response;
  }
  //https://dev.twitter.com/docs/using-search
  public Response search(final String query, HashMap<String,String> post){
    if(post==null) post = new HashMap<String,String>();
    post.put("q",query);
    return this.send(SimpleTwitterLib.BASE_URL+"search/tweets.json", post);
  }
  
  public ArrayList<String> get_tweets(){
    ArrayList<String> ret = new ArrayList<String>();
    if(this.last_search != null){
      JSONArray statuses = this.last_search.getJSONArray("statuses");
      for (int i = 0; i < statuses.size(); i++)
        ret.add( statuses.getJSONObject(i).getString("text") );
    }
    return ret;
  }

  public ArrayList<String> get_urls(){
    ArrayList<String> ret = new ArrayList<String>();
    try{
      if(this.last_search != null){
        JSONArray statuses = this.last_search.getJSONArray("statuses");
      for (int i = 0; i < statuses.size(); i++){
        JSONArray urls = statuses.getJSONObject(i).getJSONObject("entities").getJSONArray("urls");
        for (int j = 0; j < urls.size(); j++) {
          ret.add( urls.getJSONObject(j).getString("expanded_url") );
        }
      }
    } catch(RuntimeException ex){;}
    return ret;
  }
}
