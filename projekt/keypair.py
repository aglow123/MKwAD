from api import *
from common import *

def readParityCheck(H):
    hbytestream = bytearray(H_BYTE_FILESIZE)
    
    with open('parity_check.pqsigrm', 'rb') as parity_binary:
        parity_binary.readinto(hbytestream)
        # if patity_binary == None:
        #     return ERROR_NO_FILE
    
    hbytestream = list(hbytestream)
    H = importMatrix(H, hbytestream)
    del hbytestream    
    return H

def getInsertedParityCheckMtx(H, R):
    for row in range(NUMOFPUNCTURE):
        for col in range(CODE_N - NUMOFPUNCTURE):
            setElement(H, (CODE_N - CODE_K - NUMOFPUNCTURE) + row, col, getElement(R, row, col))
    return H

def copy_columns(dest, src, lead):
    for row in range(dest.rows):
        for col in range(dest.cols):
            setElement(dest, row, col, getElement(src, row, lead[col]))
    return dest

def generateRandomInsertionMtx(R):
    randombytesstream = [0]*(SECRET_R_BYTES)
    randombytes(randombytesstream, SECRET_R_BYTES)
    importMatrix(R, randombytesstream)
    return R

def swap(Q, i, j):
    temp = Q[i]
    Q[i] = Q[j]
    Q[j] = temp

def generatePermutation(Q, Qinv):
    randomidxstream = [0]*(CODE_N)

    for i in range(CODE_N):
        Q[i] = i
        Qinv[i] = i

	# Generate Permutation by Knuth shuffles
    randomidxstream = randombytes(randomidxstream, CODE_N)
    for i in range(CODE_N):
        idx = randomidxstream[i]%CODE_N

    # Set Qinv
    for i in range(CODE_N):
        Qinv[Q[i]] = i
	
    del randomidxstream
    return Qinv

def permutation(H, Q, H_pub):
    for row in range(H.rows):
        for col in range(H.cols):
            setElement(H_pub, row, col, getElement(H, row, Q[col]))
    return H_pub

def crypto_sign_keypair(pk, sk):
    H = newMatrix(CODE_N-CODE_K, CODE_N)
    Sinv = newMatrix(CODE_N - CODE_K, CODE_N - CODE_K)
    R = newMatrix(NUMOFPUNCTURE, CODE_N-NUMOFPUNCTURE)

    Q = [0]*(CODE_N)
    Qinv =  [0]*(CODE_N)

    H_pub = newMatrix(CODE_N - CODE_K, CODE_N)
	
    H_lead = [0]*(CODE_N-CODE_K)
    H_lead_diff = [0]*(CODE_N)

    # Get parity check matrix of punctured RM code with random insertion,
    H = readParityCheck(H)

    # get random matrix R
    R = generateRandomInsertionMtx(R)
    H = getInsertedParityCheckMtx(H, R)

    # get Permutation
    Q = generatePermutation(Q, Qinv)
    H_pub = permutation(H, Q, H_pub)
    del Q

    H = matrixcpy(H, H_pub)     # copy of scrambled matrix, for Sinv

    H_pub = reducedEchelon(H_pub)

    H_lead_diff = getLeadingCoeff(H_pub, H_lead, H_lead_diff)

    # Generate a Scrambling matrix and its inverse.
    Sinv = copy_columns(Sinv, H, H_lead)
    deleteMatrix(H)

    # export public matrix and its H_leading set to pk
    H_info = newMatrix(CODE_N - CODE_K, CODE_K)
    H_info = copy_columns(H_info, H_pub, H_lead_diff)
    del H_lead_diff
    deleteMatrix(H_pub)

    pk = exportMatrix(pk, H_info)
    pk[PUBLIC_H_INFO_BYTES:PUBLIC_H_INFO_BYTES+PUBLIC_LEADING_SET_BYTES] = H_lead[:PUBLIC_LEADING_SET_BYTES]
    del H_lead
    deleteMatrix(H_info)

    # export private in order: Sinv, R, Qinv
    sk = exportMatrix(sk, Sinv)
    sk = sk + exportMatrix([], R)
    sk += Qinv[:SECTER_QINV_BYTES]

    deleteMatrix(Sinv)
    deleteMatrix(R)
    del Qinv

    return pk, sk