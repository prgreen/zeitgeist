import redis
from bottle import route, run, template, get, post, request, redirect

r = redis.StrictRedis(host='localhost', port=6379, db=0)

SENTENCES_KEY = 'zeitgeist:sentences'
ZEITGEIST_KEY = 'zeitgeist:zeitgeist'


html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

def html_unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    # this has to be last:
    s = s.replace("&amp;", "&")
    s = s.replace("&quot;", '"')
    s = s.replace("&apos;", "'")
    return s

@get('/')
def zeitgeist():
    #load all sentences from redis
    sentences = r.zrange(SENTENCES_KEY, 0, -1, desc=True, withscores=True)
    sentence_list = ""
    sentence_list += "<ul>"
    for s in sentences:
        sentence_list += "<li>"
        sentence_list += html_escape(str(s[0]))
        sentence_list += "<br/>"
        sentence_list += str(s[1])[:-2]
        sentence_list += "<br/>"
        sentence_list += "<form method=\"POST\" action=\"/upvote\">"
        sentence_list += "<input type=\"hidden\" name=\"sentence\" value=\"" + html_escape(str(s[0])) + "\">"
        sentence_list += "<input type=\"submit\"/ value=\"+\">"
        sentence_list += "</form>"
        sentence_list += "</li>"
    sentence_list += "</ul>"
    zeitgeist = "Undetermined!"
    try:
        zeitgeist = sentences[0][0]
    except:
        pass
    z = r.get(ZEITGEIST_KEY)
    if z != None:
        zeitgeist = z

    #TODO add reCAPTCHA to form
    return """
    <h1>The current Zeitgeist is:
    """+ html_escape(zeitgeist) +"""</h1>
    <h2>Vote for the next Zeitgeist:</h2>
    """+ sentence_list +"""
    <p>Try your own Zeitgeist:</p>
    <form method="POST" action="/sentence">
    <input name="sentence" type="text"/>
    <input type="submit"/>
    </form>
    """

@post('/sentence')
def submit_sentence():
    #TODO Check IP address for limitation
    sentence = request.forms.get('sentence')
    if len(sentence) <= 140 and sentence != '':
        #save it in redis
        r.zadd(SENTENCES_KEY, 0, sentence)
        return "Your contribution " + html_escape(sentence) + " has been saved.<br/><a href=\"/\">Go back.</a>"
    else:
        return "Your contribution is empty or too long (max 140 characters), so it was refused.<br/><a href=\"/\">Go back.</a>"

@post('/upvote')
def submit_upvote():
    #TODO Check IP address for limitation
    sentence = html_unescape(request.forms.get('sentence'))
    if len(sentence) <= 140 and sentence != '':
        if r.zscore(SENTENCES_KEY, sentence) != None:
            r.zincrby(SENTENCES_KEY, sentence)
    redirect('/')
run(host='0.0.0.0', port=8082)