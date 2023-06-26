from api import *
from common import *
from keypair import *
from matrix import *
from nearest_vector import *
from open import *
from parm import *
from sign import *
from rng import *


with open('param/seed.txt', 'r') as f:
    seed = str.encode(f.readline())
    
with open('param/mlen.txt', 'r') as f:
    mlen = int(f.readline())

with open('param/msg.txt', 'r') as f:
    msg = str.encode(f.readline())

with open('param/pk.txt', 'r') as f:
    pk = str.encode(f.readline())

with open('param/sk.txt', 'r') as f:
    sk = list(map(int, str.encode(f.readline())))

with open('param/smlen.txt', 'r') as f:
    smlen = int(f.readline())

with open('param/sm.txt', 'r') as f:
    sm = str.encode(f.readline())

pk, sk = crypto_sign_keypair(pk, sk)
mlen, msg, error, sign_i = crypto_sign(sm, smlen, msg, mlen, sk)
result = crypto_sign_open(msg, mlen, sm, smlen, pk)

print(result)
if result==0:
    print('Sign verified correctly')
else:
    print('Sign failed')