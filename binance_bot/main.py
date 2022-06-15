import db_creator
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

db = db_creator.db_constructor()

sns.set_theme(style = 'whitegrid')
sns.lineplot(data = db[['open']], palette = 'tab10')

plt.show()
