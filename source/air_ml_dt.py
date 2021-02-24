# Importimi i librarive
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import pydotplus
from sklearn import tree
import collections
import graphviz

# Importimi i bazes se te dhenave
dataset = pd.read_excel('parametrat_ajri_dataset_excel.xlsx')
X=dataset.iloc[:, 0:5].values #vendos ne matrice cdo rresht(vlere) te variablave dhe ne kolone llojin e tyre qe duam sipas rendit duke nisur numerimin nga 0 
y = dataset.iloc[:, 5].values #vendos outputin qe duam

print(dataset.isnull().sum()) #shfaq numrin e vlerave te munguara per cdo kolone

#encode - imi i stringave ne int
from sklearn.preprocessing import LabelEncoder
labelencoder_X=LabelEncoder() 
X[:, 0]=labelencoder_X.fit_transform(X[:, 0])
labelencoder_X=LabelEncoder() 
X[:, 1]=labelencoder_X.fit_transform(X[:, 1])
labelencoder_X=LabelEncoder()
X[:, 2]=labelencoder_X.fit_transform(X[:, 2])
labelencoder_X=LabelEncoder()
X[:, 2]=labelencoder_X.fit_transform(X[:, 3])
labelencoder_X=LabelEncoder()
X[:, 2]=labelencoder_X.fit_transform(X[:, 4])

labelencoder_y=LabelEncoder() 
y=labelencoder_y.fit_transform(y)


# Ndarja e bazes se te dhenave ne grupin e Trainimit dhe ne grupin e Test
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 0)


# Fitting classifier to the Training set
from sklearn.tree import DecisionTreeClassifier, export_graphviz
classifier = DecisionTreeClassifier(criterion="entropy")
classifier.fit(X_train,y_train)

# Parashikimi i vlerave te grupit Test
y_pred = classifier.predict(X_test)

# Matrica e Konfuzionit
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred)


# konvertimi ne txt dhe dot file
from sklearn import tree
with open("decision_tree.txt", "w") as f:
    f = export_graphviz(classifier, out_file=f)

def visualize_tree(tree, feature_names):
    """Create tree png using graphviz.

    Args
    ----
    tree -- scikit-learn DecsisionTree.
    feature_names -- list of feature names from X array
    """
    with open("dt.dot", 'w') as f:
        export_graphviz(tree, out_file=f,
                        feature_names=feature_names)

    command = ["dot", "-Tpng", "decision_tree.dot", "-o", "decision_tree.png"]

visualize_tree(classifier,["pm2_5","pm10","temp", "trysnia", "lageshtira"])

print('Confusion matrix: ')
print(cm)
print('Accuracy of decision tree classifier on test set: {:.2f}'.format(classifier.score(X_test, y_test)))

#shfaq informacion: si psh precizioni per parashikimin e sakte 0/1 etc.
from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred))

#vizualizimi i decision tree ne foto format png  
from IPython.display import Image  
from sklearn.tree import export_graphviz

feature_names = ["pm2_5","pm10","temp", "trysnia", "lageshtira"]
export_graphviz(classifier, out_file="dt.dot", feature_names=feature_names)

import graphviz
with open("dt.dot") as f:
    dot_graph = f.read()

graphviz.Source(dot_graph)
graph = pydotplus.graph_from_dot_data(dot_graph)
graph.write_png('tree.png')

