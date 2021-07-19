import sqlite3
import time
from datetime import date
from datetime import datetime
from src.user import User
from riotwatcher import ApiError, TftWatcher

class CRUDSummoners():
    my_region = 'euw1'

    def conectarBase(self):
        return sqlite3.connect("src/database/data.sqlite")

    def createUser(self, name):
        # 1. Obtengo los datos del nuevo usuario
        summoner = self.getSummoner(name)
        liga = self.getLiga(summoner[1])
        # 2. Agregar Datos en nuestra base de datos
        con = self.conectarBase()
        cursorObj = con.cursor()
        cursorObj.execute("INSERT INTO summoners (name, id, lvl, puuid) VALUES('"+summoner[0]+"','"+summoner[1]+"',"+summoner[2]+", '"+summoner[3]+"')")
        cursorObj.execute("INSERT INTO leagueTFT (id, tier, rank, lp, ptotal, score, avgplacement) VALUES('"+summoner[1]+"','"+liga[0]+"','"+ liga[1]+"',"+ liga[2]+","+liga[3]+", "+liga[4]+", 0)")
        con.commit()
        con.close()

    
    def readLeague(self):
        con = self.conectarBase()
        cursorObj = con.cursor()
        cursorObj.execute('SELECT name, tier, rank, lp, ptotal, score, avgplacement, updatesummon, summoners.ID FROM summoners, leagueTFT where summoners.id = leagueTFT.id')
        read = cursorObj.fetchall()
        con.close()
        return read


    def updateLeague(self):
        con = self.conectarBase()
        cursorObj = con.cursor()
        cursorObj.execute('SELECT ID, puuid, name FROM summoners')
        ids = cursorObj.fetchall()
        for id in ids:
            puuid = id[1]
            liga = self.getLiga(id[0])
            cursorObj.execute("SELECT tier, rank, lp FROM leagueTFT where leagueTFT.id = '"+id[0]+"'")
            ligaBase = cursorObj.fetchone()
            update = False
            if(liga[0] != ligaBase[0] or liga[1]!= ligaBase[1] or str(liga[2]) != str(ligaBase[2])):
                matchs = self.getMatches(puuid)
                for match in matchs:
                    cursorObj.execute("SELECT * from matchrank WHERE matchid = '"+match+"'")
                    if (len(cursorObj.fetchall()) == 0):
                        nuevoMatch = self.getPlacementByMatch(match, puuid)
                        cursorObj.execute("INSERT INTO matchrank (puuid, matchid, placement) VALUES ('"+puuid+"', '"+nuevoMatch[1]+"',"+str(nuevoMatch[2])+")")
                cursorObj.execute("SELECT placement FROM matchrank where puuid = '"+puuid+"'")
                placements = cursorObj.fetchall()
                totalplacement = 0
                avg = 0
                for placement in placements:
                    avg +=placement[0]
                    totalplacement +=1
                try:
                    avg = avg/totalplacement
                except ZeroDivisionError:
                    avg = 0
                cursorObj.execute("UPDATE leagueTFT SET tier ='"+liga[0]+"',rank='"+ liga[1]+"',lp="+ liga[2]+",ptotal="+liga[3]+", Score="+liga[4]+", avgplacement="+str(avg)+", updateSummon=True where id ='"+id[0]+"'")
            else:
                cursorObj.execute("UPDATE leagueTFT SET updateSummon=False where id ='"+id[0]+"'")
        cursorObj.execute("UPDATE riotAPI SET api='"+self.fechaActual()+"' where valor='lastupdate'")
        con.commit()
        con.close()

    def deleteUser(self, name):
        con =  self.conectarBase()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT id FROM summoners where name='"+name+"'")
        id = cursorObj.fetchone()
        if( len(id) == 0):
            raise Exception("No se ha encontrado al summoner")
        cursorObj.execute("DELETE FROM leagueTFT WHERE id='"+ id[0]+"'")
        cursorObj.execute("DELETE FROM summoners WHERE id='"+ id[0]+"'")
        con.commit()
        con.close()

    def getLiga(self, id):
        tier = "No hay datos"
        rank = ""
        watchertft = self.apiRiotInit()
        try:
            liga = watchertft.league.by_summoner(self.my_region, id)
            tier = liga[0]['tier']
            rank = liga[0]['rank']
            lp = str(liga[0]['leaguePoints'])
            ptotal = str(liga[0]["wins"] + liga[0]["losses"])
            score = str (self.obtenerScore(liga[0]['tier'],liga[0]['rank'],liga[0]['leaguePoints']))
            tier = self.englishToSpanish(tier)
        except IndexError:
            lp = "0"
            ptotal = "0"
            score = "0"
        except:
            raise Exception("Problemas para obtener datos de la api")
        return (tier, rank, lp, ptotal, score)
        
    def getSummoner(self, name):
        # Buscar Usuario en la API de Riot
        watchertft = self.apiRiotInit()
        try:
            summoner = watchertft.summoner.by_name(self.my_region, name)
        except:
            raise Exception("Problemas para obtener datos de la api")
        return ( summoner["name"], summoner["id"], str(summoner["summonerLevel"]), summoner["puuid"])
    
    def getMatches(self, puuid):
        # Buscar matchs de un usuario a través del puuid
        watchertft = self.apiRiotInit()
        try:
            matches = watchertft.match.by_puuid("europe", puuid,100)
        except ApiError:
            raise Exception("Problemas para obtener datos de la api")
        return matches

    def getPlacementByMatch(self, matchid, puuid):
        watchertft = self.apiRiotInit()
        try:
            match = watchertft.match.by_id("europe", matchid)
        except ApiError:
            raise Exception("Problemas para obtener datos de la api")
        placement = 0
        if(match["info"]["tft_game_type"] == "standard"):
            for participants in match["info"]["participants"]:
                if( participants["puuid"] == puuid):
                    placement = participants["placement"]
        return (puuid, matchid, placement)

    def apiRiotInit(self):
        return TftWatcher(self.readApi())

    def obtenerScore(self, tier, rank, lp):
        ligaScore ={
            "No hay datos": 0,
            "IRON":0,
            "BRONZE": 400,
            "SILVER": 800,
            "GOLD": 1200,
            "PLATINUM": 1600,
            "DIAMOND": 2000,
            "MASTER": 2400,
            "GRANDMASTER": 2800,
            "CHALLENGER": 3200
        }

        rankScore ={
            "":0,
            "IV":0,
            "III": 100,
            "II": 200,
            "I": 300,
        }
        return ligaScore.get(tier) + rankScore.get(rank) + lp

    def refreshData(self):
        horaActual = time.time()
        f = open("database/time.txt", "r+")
        tiempo = f.read()
        if(float(tiempo)+30 < horaActual):
            self.updateLeague()
            f.seek(0)
            f.write(str(horaActual))
            f.truncate()
        f.close()
    
    def englishToSpanish(self,tier):
        change ={
            "No hay datos": "No hay Datos",
            "IRON":"Hierro",
            "BRONZE": "Bronce",
            "SILVER": "Plata",
            "GOLD": "Oro",
            "PLATINUM": "Platino",
            "DIAMOND": "Diamante",
            "MASTER": "Maestro",
            "GRANDMASTER": "Gran Maestro",
            "CHALLENGER": "Retador"
        }
        return change.get(tier)

    def ordenarLista(self, tupla):
        lista = [ list(x) for x in tupla]
        lista = sorted(lista, reverse= True, key=lambda score: score[5])
        posicion = 1
        for user in lista:
            user.insert(0,posicion)
            posicion +=1
        return lista

    def updateRiotApi(self,api):
        con = self.conectarBase()
        cursorObj = con.cursor()
        cursorObj.execute("UPDATE riotAPI SET api='"+api+"' where valor='unica'")
        con.commit()
        con.close()

    def readApi(self):
        con = self.conectarBase()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT api FROM riotapi where valor = 'unica'")
        read = cursorObj.fetchone()
        con.close()
        return read[0]

    def readUpdateTime(self):
        con = self.conectarBase()
        cursorObj = con.cursor()
        cursorObj.execute("SELECT api FROM riotapi where valor = 'lastupdate'")
        read = cursorObj.fetchone()
        con.close()
        lastime = float(format(time.time() - float(read[0])))
        minutos = int(lastime /60)
        segundos = lastime % 60
        print(lastime)
        return "{0:.0f}".format(minutos)+" min : {0:.0f}".format(segundos)+" seg"
        

    def fechaActual(self):
        return str(time.time())
        
       

    
class CRUDUser():

    database = "src/database/users.db"

    def loginUser(self, user):
        con = sqlite3.connect(self.database)
        cursorObj = con.cursor()
        cursorObj.execute('SELECT name, password FROM registrados where name="'+user+'"')
        read = cursorObj.fetchone()
        con.close()
        if read is None :
            return None
        else:
            return User(read[0], read[1])

    