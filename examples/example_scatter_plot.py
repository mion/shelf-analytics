# https://www.digitalocean.com/community/tutorials/how-to-plot-data-in-python-3-using-matplotlib
import matplotlib.pyplot as plt

X = [590,540,740,130,810,300,320,230,470,620,770,250]
Y = [32,36,39,52,61,72,77,75,68,57,48,48]

plt.scatter(X, Y, s=60, c='red', marker='^')

plt.xlim(0,1000)
plt.ylim(0,100)

plt.title('Relationship between Temperature and Iced Coffee Sales')
plt.xlabel('Cups of Iced Coffee Sold')
plt.ylabel('Temperature in Farenheit')

plt.show()
