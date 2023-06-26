import hashlib
from matrix import *
from rng import *
from parm import *


def hashMsg(s, m, mlen, sign_i):
    # Assuming 64bit environment, say size_t is defined as unsigned long
	# Hash the given message
	# syndrome s = h(h(M)|i)|(h(h(M)|i)|i)
	for idx in range(1,8):
		s[HASHSIZEBYTES*idx:HASHSIZEBYTES*(idx+1)] = sign_i # concatenate i i.e. h(h(M)|i)

	# h(M)
	SHA512 = hashlib.sha512()
	SHA512.update(m[:mlen])
	s[:HASHSIZEBYTES] = SHA512.digest()
    
	# h(h(M)|i)
	SHA512 = hashlib.sha512()
	SHA512.update(bytearray(s[:HASHSIZEBYTES]) + sign_i)
	s[:HASHSIZEBYTES] = SHA512.digest()
    
	# (h(h(M)|i)|i)
	for idx in range(1, 8):
		SHA512 = hashlib.sha512()
		SHA512.update(bytearray(s[HASHSIZEBYTES*(idx-1):HASHSIZEBYTES*idx]) + sign_i)
		s[HASHSIZEBYTES*idx:HASHSIZEBYTES*(idx+1)] = SHA512.digest()

	return s

def hammingWgt(e, elen):
    w = 0
    for i in range(elen):
        w += e[i]
    return w


