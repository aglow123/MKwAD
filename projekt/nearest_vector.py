from parm import *


def reculsive_decoding(y, r1, m1, f, l):
    if (r1==0):
        # Calculate Euclidean distance
        a1 = 0
        a2 = 0

        for i in range(f, l+1):
            a1 += pow(y[i] - 1, 2)
            a2 += pow(y[i] + 1, 2)

        if(a1 <= a2):
            for i in range(f, l+1):
                y[i] = 1
        elif(a1 > a2):
            for i in range(f, l+1):
                y[i] = -1

    elif(r1 == m1):
        for i in range(f, l+1):
            if(y[i] >= 0):
                y[i] = 1
            elif(y[i] < 0):
                y[i] = -1

    else:
        temp = y[(l + f + 1) // 2: l+1]

        for i in range((l-f+1)//2):
            y[i + (l + f + 1) // 2] = y[i + (l + f + 1) // 2] * y[i + f]

        y = reculsive_decoding(y, r1 - 1, m1 - 1, (l + f + 1) // 2, l)

        for i in range((l-f+1)//2):
            y[f + i] = (y[f + i] + y[i + (l + f + 1) // 2] * temp[i]) / 2

        y = reculsive_decoding(y, r1, m1 - 1, f, (l + f - 1) // 2)

        for i in range((l-f+1)//2):
            y[i + (l + f + 1) // 2] = y[i + (l + f + 1) // 2] * y[i + f]

        del temp
    return y

def nearest_vector(y):
    return reculsive_decoding(y, RM_R, RM_M, 0, CODE_N -1)