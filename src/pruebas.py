from crud import CRUDSummoners 

crud = CRUDSummoners()
un = crud.getSummoner("jamondejorick")
print(un)
crud.getLiga(un[1]+"1")


