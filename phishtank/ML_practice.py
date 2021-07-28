import pandas as pd 
import numpy as np 
from matplotlib import pyplot as plt 
from sklearn import neighbors
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier

df = pd.read_csv("phishtank\diabetes_data_upload.csv", encoding = 'ISO-8859-1')
df = df.replace(["Male","Female"], [1,2])
df = df.replace(["Yes","No"], [0,1])
df = df.replace(["Positive","Negative"], [0,1])
#df.drop(df.iloc[:,4:], axis = 1, inplace = True)
classlabel = df["Gender"]
x_train, x_test, y_train, y_test = train_test_split(df,classlabel,train_size = 0.8, test_size = 0.2, random_state = 100)

dt = DecisionTreeClassifier(random_state=100, max_depth=4)
dt.fit(x_train, y_train)

y_pred_dt=dt.predict(x_test)
print('Accuracy of decision tree: %.3f%%' % (accuracy_score(y_test, y_pred_dt)*100))

knn = neighbors.KNeighborsClassifier(n_neighbors=5)
knn.fit(x_train, y_train)

y_pred_knn5=knn.predict(x_test)
print('Accuracy of k-nn (k=5): %.3f%%' %(accuracy_score(y_test, y_pred_knn5)*100))

knn_new = neighbors.KNeighborsClassifier(n_neighbors=10)
knn_new.fit(x_train, y_train)

y_pred_knn10=knn_new.predict(x_test)
print('Accuracy of k-nn (k=10): %.3f%%' %(accuracy_score(y_test, y_pred_knn10)*100))

