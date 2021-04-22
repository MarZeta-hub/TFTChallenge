import sqlite3
import time
import psycopg2
from src.user import User
from riotwatcher import ApiError, TftWatcher

class CRUDSummoners():
    my_region = 'euw1'

    def conectarBase(self):
        return psycopg2.connect(host='ec2-35-174-35-242.compute-1.amazonaws.com', database="d2jupu9j7rqd7", user="rsqaemfmnjiqpw",  password="4049dfdb8302dbd1c5c86d5312d2d989ad0ee18fce5595758cc4872ffcfc77f1", sslmode='require')

    def createUser(self, name):
        # 1. Obtengo los datos del nuevo usuario
        summoner = self.getSummoner(name)
        liga = self.getLiga(summoner[1])
        # 2. Agregar Datos en nuestra base de datos
        con = self.conectarBase()
        cursorObj = con.cursor()
        cursorObj.execute("INSERT INTO summoners (name, id, lvl) VALUES('"+summoner[0]+"','"+summoner[1]+"',"+summoner[2]+")")
        cursorObj.execute("INSERT INTO leagueTFT (id, tier, rank, lp, ptotal, score) VALUES('"+summoner[1]+"','"+liga[0]+"','"+ liga[1]+"',"+ liga[2]+","+liga[3]+", "+liga[4]+")")
        con.commit()
        con.close()

    
    def readLeague(self):
        con = self.conectarBase()
        cursorObj = con.cursor()
        cursorObj.execute('SELECT name, tier, rank, lp, ptotal, score, summoners.ID FROM summoners, leagueTFT where summoners.id = leagueTFT.id')
        read = cursorObj.fetchall()
        con.close()
        return read


    def updateLeague(self):
        con = self.conectarBase()
        cursorObj = con.cursor()
        cursorObj.execute('SELECT ID FROM summoners')
        ids = cursorObj.fetchall()
        for id in ids:    
            liga = self.getLiga(id)
            cursorObj.execute("UPDATE leagueTFT SET tier ='"+liga[0]+"',rank='"+ liga[1]+"',lp="+ liga[2]+",ptotal="+liga[3]+", Score="+liga[4]+" where id ='"+id[0]+"'")
        con.commit()
        con.close()

    def deleteUser(self, name):
        con =  self.conectarBase()
        cursorObj = con.cursor()
        print(name)
        cursorObj.execute("SELECT id FROM summoners where name='"+name+"'")
        id = cursorObj.fetchone()
        print(id[0])
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
        return (summoner["name"], summoner["id"], str(summoner["summonerLevel"]))
    
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

    