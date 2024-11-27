import math
import matplotlib.pyplot as plt

#FEEL FREE TO MODIFY ANY VARIABLES THAT ARE ONLY EQUAL TO NUMBERS

maxTime = 2000
dt = .005/2
timeSteps = int(maxTime/dt) - 1

dx = .01/2 #how spaced out nodes are in battery

currentThroughBat = 70/3 #really how much current goes through each cell due to parallel setting
batInternalResistance = .015
numCellsPerBranch = 21 #By branch I mean cold plate branch. Also note this really has an effect on the water temperature, gets canceled out for other temp equations
q = numCellsPerBranch*batInternalResistance*currentThroughBat**2 #total power dissappated by batteries in the cold plate branch

flowRateTotal = 16 #change as you like, LPM
flowRateThroughBranch = flowRateTotal/4
totalArea = numCellsPerBranch * math.pi * ((.0186/2)**2)

#FOR VARIABLES: b = battery, k = kapton, t = tim, a = aluminum
kb, kk, kt, ka = 18, .2, 5, 237 #thermal conductivities
pb, pk, pt, pa = .047/(65.2/1000*math.pi*((18.6/2/1000)**2)), 1.42*(100**3)/1000, 3.1*(100**3)/1000, 2710 #densities
lb, lk, lt, la = 65.2/1000,.000254,.001,.0032 #lengths
cb, ck, ct, ca = 1000,1.09*1000, 1175, 900 #specific heats
rk, rt, ra = lk/kk/totalArea, lt/kt/totalArea, la/ka/totalArea #thermal resistances

# Calculate thermal diffusivity val in battery to see if finite works with settings
alpha_b = kb / (pb * cb)
print("Battery stability (Must be below .5 for accuracy):", alpha_b * dt / dx**2) # ensure this is below 0.5, adjust dt and dx as needed


h = 3000 #water convection coeff
rw = 1/(h*totalArea) #water resistance

hair = 5 #convection coefficient of still air
airTemp = 33.8888889 #ambient temp

radiatorEffectiveness = .4

waterHeatCapacityInBranch = 1000*4182*.0000166667*flowRateThroughBranch
waterHeatCapacityTotal = 1000*4181*.0000166667*flowRateTotal
airHeatCapacity = 345.7

#initializing temp arrays at ambient temp
tb = [[airTemp] for x in range(int(lb/dx))] #temp of all battery nodes
tk = [airTemp] #temp at bottom of kapton
tt = [airTemp] #temp at bottom of TIM
ta = [airTemp] #temp at bottom of aluminum
twrad = [airTemp] #temp of water after radiator
twbat = [airTemp] #temp of water after battery segment


for time in range(timeSteps):
    #Figuring Out how much heat goes through sections of the cold plates (qbk = heat from battery to kapton)
    qbk = (tb[-1][-1]-tk[-1])/rk
    qkt = (tk[-1]-tt[-1])/rt
    qta = (tt[-1]-ta[-1])/ra
    qaw = (ta[-1]-twrad[-1])/rw

    #print(qbk-qkt)

    for i in range(len(tb)):
        #Figuring out temp at top node
        if i == 0:
            tb[i].append(tb[i][-1]+q*dt/pb/lb/cb/totalArea+2*kb*dt*(tb[i+1][-1]-tb[i][-1])/dx/dx/pb/cb+2*dt*hair*(airTemp-tb[i][-1])/pb/cb/dx)
        #Figuring out temp at bottom node using heat gen, local battery node, and heat loss to cold plate
        elif i == (len(tb)-1):
            tb[i].append(tb[i][-1]+2*kb*dt*(tb[i-1][-1]-tb[i][-1])/dx/dx/pb/cb+q*dt/pb/cb/lb/totalArea-2*qbk*dt/pb/cb/dx/totalArea)
        #Figuring out temps at diff nodes
        else:
            tb[i].append(tb[i][-1]+q*dt/pb/cb/lb/totalArea+kb*dt*(tb[i+1][-1]+tb[i-1][-1]-2*tb[i][-1])/dx/dx/pb/cb)

    #new temp values in the cold plate and water
    tk.append(tk[-1]+(qbk-qkt)*dt/(ck*pk*totalArea*lk))
    tt.append(tt[-1]+(qkt-qta)*dt/(ct*pt*totalArea*lt))
    ta.append(ta[-1]+(qta-qaw)*dt/(ca*pa*totalArea*la))
    twbat.append(twrad[-1]+qaw/waterHeatCapacityInBranch)
    twrad.append((radiatorEffectiveness*airHeatCapacity*airTemp+waterHeatCapacityTotal*twbat[-1])/(waterHeatCapacityTotal+radiatorEffectiveness*airHeatCapacity))
    #twrad.append(airTemp)


#GRAPHING RESULTS
timeVals=[]
for i in range(int(maxTime/dt)):
    timeVals.append(i*dt)
xvals = []
for i in range(len(tb)):
    xvals.append(i*dx)

#Adjust tb[i] to get temp vs time at certain battery node
plt.plot(timeVals, tb[0], color = "red", label ="Top of Battery")
plt.plot(timeVals, tb[int(len(tb)/2)], color = "orange", label = "Middle of Battery")
plt.plot(timeVals, tb[-1], color = "blue", label = "Bottom of Battery")
plt.xlabel("Time (s)")
plt.ylabel("Temp (C)")
plt.title("Battery Temperature over Time")
plt.legend()
plt.show()

#Adjust to get temp vs distance across battery
finalBatTemps = []
for i in range(len(tb)):
    finalBatTemps.append(tb[i][-1])
plt.plot(xvals, finalBatTemps, color = "red")
plt.xlabel("Distance (x)")
plt.ylabel("Temp (C)")
plt.title("Battery Temperature over Distance (0=top)")
plt.show()

plt.plot(timeVals, twbat, color = "purple", label ="Water after Battery")
plt.plot(timeVals, twrad, color = "blue", label ="Water after Radiator")
plt.plot(timeVals, tk, color = "yellow", label = "Kapton Tape")
plt.plot(timeVals, tt, color = "red", label = "TIM")
plt.plot(timeVals, ta, color = "grey", label = "Aluminum")
plt.xlabel("Time (s)")
plt.ylabel("Temp (C)")
plt.title("Water Temperature over Time after Battery")
plt.legend()
plt.show()

print("Final Temp at Top of Battery:", tb[0][-1])
print("Final Temp at Bottom of Battery", tb[-1][-1])
average = 0
for i in range(len(tb)):
    average+=tb[i][-1]
print("Average Battery Temp:", average/len(tb))