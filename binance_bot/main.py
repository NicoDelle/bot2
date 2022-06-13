import db_creator
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

db = db_creator.db_constructor()

fig, ax = plt.subplots()
ax.plot(db.index, db.open)
plt.show()
