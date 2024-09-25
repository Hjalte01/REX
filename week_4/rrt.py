

numpy.np



r_r = 230 # 230 mm
b_r = 160 # 160 mm

r_sum = r_r + b_r

dist = [[1, 2, 3], [11, 22, 33]]

for i in range(len(dist[0])):
    print(np.sqrt(dist[0][i] - dist[1][i]), " : ")