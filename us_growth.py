# Copyleft 2020 Forrest Sheng Bao 

#%%

import urllib
import numpy 
import matplotlib.pyplot as plt


response = urllib.request.urlopen('https://covidtracking.com/api/us/daily')
html = response.read()

# %%
x = json.loads(html)

#%% 

def get_number(x, keyname):
    d = [daily[keyname] for daily in x]
    d = d[:-1]
    d = d[::-1]
    return numpy.array(d )

names = ['positiveIncrease', 'totalTestResultsIncrease', \
    'totalTestResults', 'positive']

for n in names:
    cmd = "{}=get_number(x, \'{}\')".format(n, n)
    print (cmd)
    exec (cmd)

# %%
# compute the correlation coefficient 
cc = numpy.corrcoef(positiveIncrease, totalTestResultsIncrease)
print ("correlation cofficient: ", cc[1,0])

# %%
plt.figure(figsize=(6,4)) 
plt.plot(totalTestResults, positive, \
    'k+-', linewidth=2, markersize=10)
plt.xlabel("cumulative tests")
plt.ylabel("cumulative positive")
plt.title("US COVID-19\n cumulative positive cases (y) vs. cumulative tests (x)")
plt.xticks(rotation=35)
plt.yticks(rotation=35)
plt.text(100000,250000, "R ="+str(cc[0,1])+"\n from March 04 to April 04")
plt.savefig("growth.png")


# %%
plt.figure(figsize=(6,4)) 
plt.plot(range(len(positive)), totalTestResultsIncrease, \
    'r.-', linewidth=2, markersize=10)
plt.plot(range(len(positive)), positiveIncrease, \
    'gx-', linewidth=2, markersize=6)
plt.xlabel('Days since March 04')
plt.title("US COVID-19 daily increases of positive and total cases")
plt.yticks(rotation=35)
plt.legend(["Test case increase", "positive case increase"])
# plt.text(100000,250000, "R ="+str(cc[0,1])+"\n from March 04 to April 04")
plt.savefig("increase.png")

# %%
plt.figure(figsize=(6,4)) 
plt.plot(range(len(positive)), positiveIncrease/totalTestResultsIncrease*100, \
    'r.-', linewidth=2, markersize=10)
plt.xlabel('Days since March 04')
plt.ylabel('Ratio (%)')
plt.title("US COVID-19, ratio of positive cases in daily tests")
# plt.yticks(rotation=35)
plt.savefig("ratio.png")


# %%
