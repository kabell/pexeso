from django.shortcuts import render
import os,re,random,jsonpickle
from django.http import HttpResponse

pexeso_dir = 'pexeso/pexeso_data'


class Player:

    def __init__(self,id,name,score):
        self.id = id
        self.name = name
        self.score = score


class Card:

    def __init__(self,id,image,sound,visible):
        self.id = id
        self.image = image
        self.sound = sound
        self.visible = visible


class Pexeso:

    def __init__(self,request):
        self.number_of_players = int(request.POST['number_of_players'])
        self.pexeso_file = request.POST['pexeso_file']

        self.load_pexeso_file()

        #random shuffle
        random.shuffle(self.cards)

        #load players
        self.players = []
        for i in range(self.number_of_players):
            self.players.append(Player(i, request.POST['player'+str(i)], 0))

        random.shuffle(self.players)

        self.na_tahu = 0
        self.na_tahu_name = self.players[self.na_tahu]
        self.opened = []
        self.no_turns_left = False
        self.sound = None
        self.zostava = -1

    def load_pexeso_file(self):
        with open(pexeso_dir+'/'+self.pexeso_file,'r') as f:
            self.name = f.readline()
            self.number_of_cards = int(f.readline().rstrip('\n'))
            self.cards = []
            self.cards_multiple = int(f.readline().rstrip('\n'))

            for i in range(self.number_of_cards):
                line = f.readline().rstrip('\n')
                if line == '':
                    break
                line = line.split(':')
                for j in range(self.cards_multiple):
                    self.cards.append(Card(i,line[0],line[1],False))

    def close(self):

        if len(self.opened)>1 and self.cards[self.opened[-1]].id!=self.cards[self.opened[-2]].id:
            for i in self.opened:
                self.cards[i].visible = False
        elif len(self.opened) == self.cards_multiple:
            self.players[self.na_tahu].score += 1
            self.na_tahu += self.cards_multiple-1
            self.na_tahu %= self.cards_multiple
        self.na_tahu += 1
        self.na_tahu %= self.number_of_players
        self.na_tahu_name = self.players[self.na_tahu]
        self.opened = []
        self.no_turns_left = False
        self.sound = None

        self.zostava = 0
        for i in self.cards:
            if not i.visible:
                self.zostava += 1


    def tah(self, cislo):
        self.sound = None
        if self.no_turns_left or self.cards[int(cislo)].visible:
            return

        self.opened.append(int(cislo))
        self.cards[int(cislo)].visible = True
        self.sound = self.cards[int(cislo)].sound
        if len(self.opened) == self.cards_multiple:
            self.no_turns_left = True

        if len(self.opened) >1:
            if self.cards[self.opened[-1]].id!=self.cards[self.opened[-2]].id:
                self.no_turns_left = True
                self.hlaska = "Prepáč, ale pexesá sa nezhodujú."
                self.hlaska_color = "red"
            else:
                self.hlaska = "Vyborne pexesá sú rovnaké, môžeš ísť ešte raz."
                self.hlaska_color = 'green'






def setup(request):
    pexesos = os.listdir(pexeso_dir)
    r = re.compile('^.*\.pexeso$')
    filter(r.match, pexesos)
    return render(request, 'setup.html', locals())


def index(request,cardid=-1):


    if request.method == 'POST':
        request.session['Pexeso'] = jsonpickle.encode(Pexeso(request))

    pexeso = None
    if "Pexeso" in request.session:
        pexeso =  jsonpickle.decode(request.session.get('Pexeso'))

    if pexeso == None:
        return setup(request)

    if cardid == -3:
        return render(request, 'vysledky.html',locals())

    if cardid == -2:
        pexeso.close()
    elif cardid != -1:
        pexeso.tah(int(cardid)-1)

    request.session['Pexeso'] = jsonpickle.encode(pexeso)
    if pexeso.zostava == 0:
        return render(request, 'vysledky.html',locals())

    return render(request, 'pexeso.html',locals())

def reset(request):
    del request.session['Pexeso']
    return index(request)