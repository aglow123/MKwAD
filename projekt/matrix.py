MATRIX_NULL = 0
ELEMBLOCKSIZE = 8

class matrix:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.elem = [0]*(rows*cols)

def newMatrix(rows, cols):
    return matrix(rows, cols)

def deleteMatrix(A):
    del A.elem
    del A

def product(mtx1, mtx2, prod):
    for col in range(mtx2.cols):
        for row in range(mtx1.rows):
            val=0
            for k in range(mtx1.cols):
                val ^= getElement(mtx1, row, k) * getElement(mtx2, k, col)
            prod = setElement(prod, row, col, val)
    return prod

def rowInterchanging(A, row_idx1, row_idx2):
    for col_idx in range(A.cols):
        temp = A.elem[row_idx1 * A.cols + col_idx]
        A.elem[row_idx1 * A.cols + col_idx] = A.elem[row_idx2 * A.cols + col_idx]
        A.elem[row_idx2 * A.cols + col_idx] = temp
    return A

def rowAddition(A, dest_row_idx, adding_row_idx):
    for col_idx in range(A.cols):
        A.elem[dest_row_idx * A.cols + col_idx] = A.elem[dest_row_idx * A.cols + col_idx] ^ A.elem[adding_row_idx * A.cols + col_idx]
    return A

def reducedEchelon(A):
    row_idx, succ_row_idx = 0, 0
    for col_idx in range(A.cols):
        while row_idx < A.rows:
            if(getElement(A, row_idx, col_idx) == 1):
                break
            row_idx += 1
        if(row_idx == A.rows):
            row_idx = succ_row_idx
            continue
        if(row_idx != succ_row_idx):
            A = rowInterchanging(A, succ_row_idx, row_idx)
        for i in range(A.rows):
            if(i == succ_row_idx):
                continue
            if(getElement(A, i, col_idx) == 1):
                A = rowAddition(A, i, succ_row_idx)
        succ_row_idx += 1
        row_idx = succ_row_idx
    return A

def matrixcpy(dest, src):
    if(dest.rows != src.rows or dest.cols != src.cols):
        return MATRIX_NULL
    dest.elem = src.elem
    return dest

def transpose(dest, src):
    if((dest.rows != src.cols) or (dest.cols != src.rows)):
        return MATRIX_NULL
    for row in range(dest.rows):
        for col in range(dest.cols):
            dest = setElement(dest, row, col, getElement(src, col, row))
    return dest

def exportMatrix(dest, src_mtx):
    dest = src_mtx.elem
    return dest

def importMatrix(dest_mtx, src):
    len_rem = len(dest_mtx.elem) - len(src)
    dest_mtx.elem = src
    dest_mtx.elem += [0]*len_rem
    return dest_mtx

def getLeadingCoeff(mtx, lead, lead_diff):
    row, diff_idx, lead_idx = 0, 0, 0
    for col in range(mtx.cols):
        if(getElement(mtx, row, col) == 0):
            lead_diff[diff_idx] = col
            diff_idx += 1
        else:
            lead[lead_idx] == col
            lead_idx += 1
            row += 1
        if(row == mtx.rows):
            while(col<mtx.cols-1):
                col += 1
                lead_diff[diff_idx] = col
                diff_idx += 1
            return lead_diff
    return lead_diff

def getElement(A, i, j):
    return A.elem[i * A.cols + j]

def flipElement(A, i, j, val):
    A.elem[i * A.cols + j] = val
    return A

def setElement(A, i, j, val):
    if getElement(A, i, j) == val:
        return A
    else:
        return flipElement(A, i, j, val)