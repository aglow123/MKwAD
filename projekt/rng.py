from ctypes import CDLL
from ctypes.util import find_library
import sys
from OpenSSL import crypto

RNG_SUCCESS = 0
RNG_BAD_MAXLEN = -1
RNG_BAD_OUTBUF = -2
RNG_BAD_REQ_LEN = -3

libcrypto = CDLL(find_library('libcrypto'))

class AES_XOF_struct:
    def __init__(self):
        self.buffer = []
        self.buffer_pos = 0
        self.length_remaining = 0
        self.key = [0]*(32)
        self.ctr = [0]*(16)

class AES256_CTR_DRBG_struct:
    def __init__(self):
        self.Key = [0]*(32)
        self.V = [0]*(16)
        self.reseed_counter = 0

def AES256_CTR_DRBG_Update(provided_data, Key, V):
    temp = [0]*(48)

    for i in range(3):
        # increment V
        for j in range(15, -1, -1):
            if V[j] == 0xff:
                V[j] = 0x00
            else:
                V[j] += 1
                break
        AES256_ECB(Key, V, temp[16*i:16*(i+1)])

    if provided_data is not None:
        for i in range(48):
            temp[i] ^= provided_data[i]
    
    Key[:32] = temp[:32]
    V[:] = temp[32:]

DRBG_ctx = AES256_CTR_DRBG_struct()

def seedexpander_init(ctx, seed, diversifier, maxlen):
    if ( maxlen >= 0x100000000 ):
        raise ValueError(f'RNG_BAD_MAXLEN {RNG_BAD_MAXLEN}')
    
    ctx.length_remaining = maxlen

    ctx.key = seed[:32]

    ctx.ctr[:8] = diversifier[:8]
    ctx.ctr[11] = maxlen % 256
    maxlen >>= 8
    ctx.ctr[10] = maxlen % 256
    maxlen >>= 8
    ctx.ctr[9] = maxlen % 256
    maxlen >>= 8
    ctx.ctr[8] = maxlen % 256
    ctx.ctr[12:] = [0]*(4)

    ctx.buffer_pos = 16
    ctx.buffer = [0]*(16)

    return ctx

def seedexpander(ctx, x, xlen):
    if x is None:
        raise ValueError(f'RNG_BAD_OUTBUF {RNG_BAD_OUTBUF}')
    if xlen >= ctx.length_remaining:
        raise ValueError(f'RNG_BAD_REQ_LEN {RNG_BAD_REQ_LEN}')
    
    ctx.length_remaining -= xlen
    offset = 0

    while ( xlen > 0 ):
        if ( xlen <= (16-ctx.buffer_pos) ):         # buffer has what we need
            x[offset:offset + xlen] = ctx.buffer[ctx.buffer_pos:ctx.buffer_pos + xlen]
            ctx.buffer_pos += xlen
            return ctx, x
        
        # take what's in the buffer
        x[offset:offset + 16 - ctx.buffer_pos] = ctx.buffer[ctx.buffer_pos:16]
        xlen -= 16-ctx.buffer_pos
        offset += 16-ctx.buffer_pos
        
        AES256_ECB(bytes(ctx.key), bytes(ctx.ctr), ctx.buffer)
        ctx.buffer_pos = 0
        
        # increment the counter
        for i in range(15, 11, -1):
            if ( ctx.ctr[i] == 0xff ):
                ctx.ctr[i] = 0x00
            else:
                ctx.ctr[i] += 1
                break
    return ctx, x

def handleErrors():
    # Get the last error and print it to stderr
    error = crypto._ffi.string(
        crypto._lib.ERR_error_string(crypto._lib.ERR_get_error(), None)
    )
    sys.stderr.write(error + '\n')
    
    # Abort the program
    sys.exit(1)

def AES256_ECB(key, ctr, buffer):
    ctx = None
    ctx = libcrypto.EVP_CIPHER_CTX_new()
    if not ctx:
        handleErrors()

def randombytes_init(entropy_input, personalization_string, security_strength):
    seed_material = [0]*(48)
    seed_material[:48] = entropy_input
    if personalization_string:
        for i in range(48):
            seed_material[i] ^= personalization_string[i]
    DRBG_ctx.Key[:32] = [0]*(32)
    DRBG_ctx.V[:16] = [0]*(16)
    AES256_CTR_DRBG_Update(seed_material, DRBG_ctx.Key, DRBG_ctx.V)
    DRBG_ctx.reseed_counter = 1

def randombytes(x, xlen):
    block = [0]*(16)
    i = 0
    
    while ( xlen > 0 ):
        # increment V
        for j in range(15, -1, -1):
            if ( DRBG_ctx.V[j] == 0xff ):
                DRBG_ctx.V[j] = 0x00
            else:
                DRBG_ctx.V[j] += 1
                break

        AES256_ECB(DRBG_ctx.Key, DRBG_ctx.V, block)
        if ( xlen > 15 ):
            x[i:i+16] = block[:16]
            i += 16
            xlen -= 16
        else:
            x[i:i+xlen] = block[:xlen]
            xlen = 0

    AES256_CTR_DRBG_Update(None, DRBG_ctx.Key, DRBG_ctx.V)
    DRBG_ctx.reseed_counter += 1
    
    return x