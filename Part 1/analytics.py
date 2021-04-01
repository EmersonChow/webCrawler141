import tldextract
from collections import defaultdict
from urllib.parse import urlparse
from bs4 import BeautifulSoup

#Lauryn Newsome (lnewsome)
#Lydia Lee (lydiaml)
#Emerson Chow (emersoc)

class Analytic:
    
    def __init__(self):
        self.subDomDict = defaultdict(int)
        self.outLinkDict = defaultdict(int)
        self.commonWordsDict = defaultdict(int)
        self.outfile = open("analyticFile.txt", 'w', encoding = "utf-8")
        self.stopWords = """
a
about
above
after
again
against
all
am
an
and
any
are
aren't
as
at
be
because
been
before
being
below
between
both
but
by
can't
cannot
could
couldn't
did
didn't
do
does
doesn't
doing
don't
down
during
each
few
for
from
further
had
hadn't
has
hasn't
have
haven't
having
he
he'd
he'll
he's
her
here
here's
hers
herself
him
himself
his
how
how's
i
i'd
i'll
i'm
i've
if
in
into
is
isn't
it
it's
its
itself
let's
me
more
most
mustn't
my
myself
no
nor
not
of
off
on
once
only
or
other
ought
our
ours	ourselves
out
over
own
same
shan't
she
she'd
she'll
she's
should
shouldn't
so
some
such
than
that
that's
the
their
theirs
them
themselves
then
there
there's
these
they
they'd
they'll
they're
they've
this
those
through
to
too
under
until
up
very
was
wasn't
we
we'd
we'll
we're
we've
were
weren't
what
what's
when
when's
where
where's
which
while
who
who's
whom
why
why's
with
won't
would
wouldn't
you
you'd
you'll
you're
you've
your
yours
yourself
yourselves """
        self.goodFiles = []
        self.traps = []
        self.longestPage = (None,0)


    #https://pypi.org/project/tldextract/
    #Used this package to grab the subdomain
    def addToSubDomDict(self, url:str) -> None:
        self.subDomDict[tldextract.extract(url).subdomain] += 1
    
    def countOutlinks(self,url):
        self.outLinkDict[url] += 1

    def addToGoodFiles(self,url):
        self.goodFiles.append(url)

    def addToTraps(self,url):
        self.traps.append(url)

    def writeAHandfulOfEmptyLines(self, lines:int):
        for i in range(lines):
            self.outfile.write("\n")
    
    def htmlText(self, content):
        soup = BeautifulSoup(content, features = "lxml")
        for script in soup(["script", "style"]):
            script.decompose()
        
        strips = list(soup.stripped_strings)
        y = " ".join(strips)
        wordList = "".join([x.lower() if (x.isalnum() or x=="\'") else " " for x in y]).split()
        return wordList
        
    def findLongest(self, content, url):
        wordList = self.htmlText(content)
        if len(wordList) > self.longestPage[1]:
            self.longestPage = (url, len(wordList))

    def addToCommonWordsDict(self, content):
        wordList = self.htmlText(content)
        for word in wordList:
            if word not in self.stopWords:
                self.commonWordsDict[word] += 1
    
    def findTopFifty(self):
        items = self.commonWordsDict.items()
        sortedItems = sorted(items, key=lambda x: x[1], reverse = True)
        for i in range(50):
            self.outfile.write("\t"+str(sortedItems[i])+"\n")

    def closeFile(self):
        #Number 1
        self.outfile.write("#1\n")
        for key,value in self.subDomDict.items():
            self.outfile.write("\t" + str(key) + ":" + str(value) +"\n")
        
        self.writeAHandfulOfEmptyLines(5)
        
        self.outfile.write("#2\n")
        self.outfile.write(max(self.outLinkDict, key=self.outLinkDict.get))
        
        self.writeAHandfulOfEmptyLines(5)
        
        self.outfile.write("#3\n")
        self.outfile.write("Downloaded URLS (note: think of this as 'crawler websites that are valid')\n")
        self.outfile.write(str(self.goodFiles))
        self.writeAHandfulOfEmptyLines(5)
        self.outfile.write("Crawler traps (i.e. when is_vaid returned False from extract_next_link)\n")
        self.outfile.write(str(self.traps))


        self.writeAHandfulOfEmptyLines(5)
        
        self.outfile.write("#4\n")
        self.outfile.write(self.longestPage[0])
        
        self.writeAHandfulOfEmptyLines(5)
        
        self.outfile.write("#5\n")
        self.findTopFifty()
        
        self.outfile.close()