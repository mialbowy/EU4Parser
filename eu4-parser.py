from sly import Lexer, Parser
from os import listdir
import re

"""
SETTINGS
"""
save_file = './test.eu4'
game_dir = 'C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis IV/'
last_pid = 4789 # Replace with automated check? Correct as of 1.30 Austria
"""
END OF SETTINGS
"""

#prov_dir = game_dir + 'history/provinces' # not used with save_file
#cur_date = (1444, 11, 11) # not used with save_file

country_fn = game_dir + 'common/country_tags/00_countries.txt'
localise_fn = game_dir + 'localisation/countries_l_english.yml'



class EU4Lexer(Lexer):
    tokens = { NAME, STRING, NUMBER, COMMENT, ASSIGN, LBRACE, RBRACE }
    ignore = ' \t'
    
    # Tokens
    NAME = r'(?:[a-zA-Z][a-zA-Z0-9_:]+|---)'
    STRING = r'".*?"'
    NUMBER = r'-?\d+(?:\.\d+)?(?:\.\d+)?'
    COMMENT = r'#.*?(?:\n|$)'
    
    # Symbols
    
    ASSIGN = r'='
    LBRACE = r'{'
    RBRACE = r'}'
    
    # Ignored pattern
    ignore_newline = r'\n+'
    
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')
        
    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1
        

class EU4Parser(Parser):
    tokens = EU4Lexer.tokens
    
    precedence = (
        ('left', ASSIGN),
    )
    
    def __init__(self):
        pass
    

    """
    Grammar rules
    
    seq: seq expr
    seq: expr

    expr: ident = value
    expr: value
    expr: comment

    value: { seq }
    value: {}
    value: ident

    ident: name
    ident: string
    ident: number
    """

    @_('seq expr')
    def seq(self, p):
        #print(p.seq, p.expr)
        p.seq.append(p.expr)    
        return p.seq

    @_('expr')
    def seq(self, p):
        #print('[', p.expr, ']')
        return [p.expr]


    @_('ident ASSIGN value')
    def expr(self, p):
        return (p.ident, p.value)

    @_('value')
    def expr(self, p):
        return p.value

    @_('COMMENT')
    def expr(self, p):
        return ('#', p.COMMENT)
    

    @_('LBRACE seq RBRACE')
    def value(self, p):
        return p.seq

    @_('LBRACE RBRACE')
    def value(self, p):
        return []

    @_('ident')
    def value(self, p):
        return p.ident


    @_('NAME')
    def ident(self, p):
        return p.NAME

    @_('STRING')
    def ident(self, p):
        return p.STRING[1:-1]

    @_('NUMBER')
    def ident(self, p):
        return p.NUMBER



def print_tree(t, indent='', tab='  '):
    if isinstance(t, str):
        print(indent + t)
    elif isinstance(t, tuple):
        (name, val) = t
        if name == '#':
            print(indent + val)
        elif isinstance(val, str):
            print(indent + name, '=', val)
        else:
            print(indent + name, '=')
            print_tree(val, indent+tab, tab)
    elif isinstance(t, list):
        for i in t:
            print_tree(i, indent+tab, tab)
    

class Nation:

    def __init__(self, tag, name):
        self.tag = tag
        self.name = name
        self.cores = []
        self.owned = []

    def get_owned_dev(self):
        t = 0
        for p in self.owned:
            t += sum(p.dev)
        return t

    def get_core_dev(self):
        t = 0
        for p in self.cores:
            t += sum(p.dev)
        return t


class Province:

    def __init__(self, p_id):
        self.p_id = p_id
        self.name = ''
        self.owner = None
        self.cores = []
        self.dev = [0, 0, 0]
        self.t_g = ''



lexer = EU4Lexer()
parser = EU4Parser()


r_fn = re.compile('(\d+) *\-? *(.+)\.txt') # file name for /provinces/*
r_date = re.compile('(\d+)\.(\d+)\.(\d+)') # date
r_country = re.compile('([A-Z]{3})\s?=\s?"countries/(.+?)\.txt"') # country name in countries file
r_localise = re.compile('([A-Z]{3}):[01] "(.+?)"') # country name in localisation file

tags = {}

print('Parsing country name file...')

with open(country_fn, 'r') as f:
    text = f.read()

for m in r_country.finditer(text):
    (tag, country) = m.group(1), m.group(2)
    tags[tag] = Nation(tag, country)

print('Parsed country names!')
print('Parsing localised country name file...')

with open(localise_fn, 'r') as f:
    text = f.read()

for m in r_localise.finditer(text):
    (tag, country) = m.group(1), m.group(2)
    if tag in tags:
        tags[tag].name = country
    else:
        tags[tag] = Nation(tag, country)

print('Parsed localised country names!')


with open(save_file, 'r') as f:
    text = f.read()

print('Parsing save file...')

p = parser.parse(lexer.tokenize(text))

print('Parsed save file!')
provs = [Province(i) for i in range(last_pid + 1)]


prov_list = None
for t in p:
    if isinstance(t, tuple) and (t[0] == 'provinces'):
        prov_list = t[1]
        break

if not prov_list:
    print("Couldn't find list of provinces in map_area_data.")
    raise SystemExit

for (i, p) in prov_list:
    p_id = -int(i)
    prov = provs[p_id]

    for a in p:
        if isinstance(a, tuple):
            (n, v) = a
            if n == 'name':
                prov.name = v
            elif n == 'owner':
                prov.owner = v
                tags[v].owned.append(prov)
            elif n == 'cores':
                for t in v:
                    prov.cores.append(tags[t])
                    tags[t].cores.append(prov)
            elif n == 'base_tax':
                prov.dev[0] = float(v)
            elif n == 'base_production':
                prov.dev[1] = float(v)
            elif n == 'base_manpower':
                prov.dev[2] = float(v)
            elif n == 'trade_goods':
                prov.t_g = v

tag_list = []

for t in tags.values():
    tag_list.append((t.tag, t.get_owned_dev(), t.get_core_dev()))

tag_list.sort(reverse=True, key=lambda t: t[2] - t[1])

for t, o, c in tag_list:
    if c > 0:
        print('%s %s owns %d dev, has cores on %d dev' % (t, tags[t].name, o, c))
