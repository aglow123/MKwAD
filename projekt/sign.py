from api import *
from nearest_vector import *
from common import *
from ctypes import *
import struct

SEEDEXPANDER_MAX_LEN = 0xfffffffe       # 2^32-1

def read_lead_diff(lead_diff):
    lead_diff_file = open('lead_diff.pqsigrm', 'rb')
    lead_diff = lead_diff_file.read()
    lead_diff_file.close()
    return lead_diff

def syndromeForMsg(Sinv, syndromeMtx_p_T, m, mlen, sign_i):
    syndrome = []
    syndrome = hashMsg(syndrome, m, mlen, sign_i)

    syndromeMtx = newMatrix(1,CODE_N-CODE_K)
    syndromeMtx_T = newMatrix(CODE_N-CODE_K, 1)

    syndromeMtx = importMatrix(syndromeMtx, syndrome)
    del syndrome
    syndromeMtx_T = transpose(syndromeMtx_T, syndromeMtx)
    syndromeMtx_p_T = product(Sinv, syndromeMtx_T, syndromeMtx_p_T)
    deleteMatrix(syndromeMtx)
    deleteMatrix(syndromeMtx_T)
    return syndromeMtx_p_T

def crypto_sign(sm, smlen, m, mlen, sk):
    lead_diff = read_lead_diff([0]*(CODE_N-CODE_K))

    # read secret key(bit stream) into appropriate type.
    Sinv = newMatrix(CODE_N-CODE_K, CODE_N-CODE_K)
    R = newMatrix(NUMOFPUNCTURE, CODE_N-NUMOFPUNCTURE)
    Qinv = [0]*CODE_N

    # import secret keys
    Sinv = importMatrix(Sinv, sk[:SECRET_SINV_BYTES])
    R = importMatrix(R, sk[SECRET_SINV_BYTES:SECRET_R_BYTES])
    for i in range(CODE_N):
        Qinv[i] = int.from_bytes(sk[SECRET_SINV_BYTES+SECRET_R_BYTES+2*i:SECRET_SINV_BYTES+SECRET_R_BYTES+2*i+2], byteorder='little')


    # Do signing:
        # find e' such that wt(e') <= t
        # iterate for SIGN_ITER_N times.
    # Signing time is proportional to Proportional 
    # To increase security, reduce t and increase N. 
    # This is security trade-off
	
    sign_i = bytearray(0)
    sign = [0]*CODE_N
    syndromeMtx_p_T = newMatrix(CODE_N - CODE_K, 1)
    y = [0]*CODE_N
    not_decoded = [0]*CODE_N
    error = [0]*CODE_N

    seed = []
    for i in range(32):
        seed.append(i)
    
    div = []
    for i in range(8):
        div.append(i)

    ctx = AES_XOF_struct()
    ctx = seedexpander_init(ctx, seed, div, SEEDEXPANDER_MAX_LEN)

    while(True):
        ctx, sign_i = seedexpander(ctx, sign_i, struct.calcsize('Q')) # random number
        # Find syndrome
        syndromeMtx_p_T = syndromeForMsg(Sinv, syndromeMtx_p_T, m, mlen, sign_i)

        # decode and find e
        # In the recursive decoding procedure,
        # Y is 1 when the received codeword is 0, o.w, -1
        for i in range(CODE_N):
            not_decoded[i] =1
            y[i] = 1
        for i in range(CODE_N - CODE_K):
            not_decoded[lead_diff[i]] = 1 if (getElement(syndromeMtx_p_T, i, 0)==0) else -1
            y[lead_diff[i]] = not_decoded[lead_diff[i]]

        y = nearest_vector(y)

        # recover error for H_m
        for i in range(CODE_N):
            error[i] = (y[i] != not_decoded[i])

        # get e_p' using R
        for i in range(NUMOFPUNCTURE):
            err = getElement(syndromeMtx_p_T, (CODE_N -CODE_K - NUMOFPUNCTURE) + i, 0)
            for j in range(CODE_N - NUMOFPUNCTURE):
                err ^= (getElement(R, i, j) & error[j])
            error[(CODE_N - NUMOFPUNCTURE)+ i] = err

        # Check Hamming weight of e'
        if(hammingWgt(error, CODE_N) <= WEIGHT_PUB):
            break

    # compute Qinv*e'
    for i in range(CODE_N):
        sign[i] = Qinv[i]*error[i]

    # export message
    # sing is (mlen, M, e, sign_i)
    # M includes its length, i.e., mlen
    sm = list(m[:mlen])

    # export, write sign into bytes
    for i in range(CODE_N//8):
        byte = 0
        for j in range(8):
            byte ^= (sign[8*i+j] << ((8-1)-j))
        sm.append(byte)
	
    sm += sign_i
    smlen = len(sm)

    deleteMatrix(Sinv)
    deleteMatrix(R)
    deleteMatrix(syndromeMtx_p_T)
    del ctx

    return mlen, m, error, sign_i