from api import *
from common import *
import struct

def import_signed_msg(errorMtx, sign_i, sm):
    errorMtx = importMatrix(errorMtx, sm)
    sign_i = sm[ERRORSIZEBYTES]
    return errorMtx, sign_i

def build_public_mtx(H_pub, H_info, H_lead):
# 	size_t row, col, lidx = 0, infoidx = 0;
    lidx, infoidx = 0, 0
    for col in range(CODE_N):
        if(lidx < CODE_N - CODE_K):
            while(col < H_lead[lidx]):
                for row in range(CODE_N - CODE_K):
                    setElement(H_pub, row, col, getElement(H_info, row, infoidx))
                col += 1
                infoidx += 1
            setElement(H_pub, lidx, H_lead[lidx], 1);
            lidx += 1
        else:
            break

    while(col < CODE_N):
        for row in range(CODE_N - CODE_K):
            setElement(H_pub, row, col, getElement(H_info, row, infoidx))
        col += 1
        infoidx += 1
    return H_pub

def crypto_sign_open(m, mlen, sm, smlen, pk):
    errorMtx = newMatrix(1, CODE_N)
    errorMtx_T = newMatrix(CODE_N, 1)
    H_pub = newMatrix(CODE_N-CODE_K, CODE_N)
    syndrome_by_hash = newMatrix(1, CODE_N-CODE_K)
    syndrome_by_e = newMatrix(CODE_N-CODE_K, 1)
    H_info = newMatrix(CODE_N-CODE_K, CODE_K)

    sign_i = bytearray(0)
	
    mlen_rx = mlen
    m_rx = sm[:mlen_rx]

    errorMtx, sign_i = import_signed_msg(errorMtx, sign_i, list(sm[:struct.calcsize('Q') + mlen_rx]))
	
    w = 0
    for i in range(CODE_N):
        w += getElement(errorMtx, 0, i)

    if(w > WEIGHT_PUB):
        return VERIF_REJECT

    syndrome = []
    syndrome = hashMsg(syndrome, m_rx, mlen_rx, sign_i)
	
    # import public key
	
    H_info = importMatrix(H_info, pk)

    H_lead = pk[PUBLIC_H_INFO_BYTES]
    H_pub = build_public_mtx(H_pub, H_info, H_lead)

    errorMtx_T = transpose(errorMtx_T, errorMtx)
    syndrome_by_e = product(H_pub, errorMtx_T, syndrome_by_e)
	
    syndrome_by_hash = importMatrix(syndrome_by_hash, syndrome)

    for i in range(CODE_N - CODE_K):
        if(getElement(syndrome_by_hash, 0, i) != getElement(syndrome_by_e, i, 0)):
            return VERIF_REJECT

    m[:mlen_rx] = m_rx[:mlen_rx]
    mlen = mlen_rx


    deleteMatrix(errorMtx)
    deleteMatrix(errorMtx_T)
    deleteMatrix(H_pub)
    deleteMatrix(syndrome_by_hash)
    deleteMatrix(syndrome_by_e)
    deleteMatrix(H_info)
    del m_rx
    return 0
