#third-party imports
import pandas as pd

#personal imports
import db_creator as dbc
import generic_tools as gt

#constructor of the database
db = dbc.db_constructor()


#SETTINGS------------------------------

MAKE_PLOT = 0 #0 -> non fare il grafico / 1 -> fai il grafico
TO_PLOT = db['open']

#--------------------------------------

if MAKE_PLOT == 0:

    gt.mkplot(db['open'])

