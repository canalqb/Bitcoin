"""secp256k1 - aritmetica de curva eliptica em Python puro (stdlib apenas).

Nenhuma dependencia externa: todas as operacoes usam inteiros grandes
nativos do Python, com coordenadas Jacobianas para evitar inversoes
modulares dentro do laco de multiplicacao escalar (uma unica inversao
no final). Isso mantem o consumo de CPU/RAM baixo e o codigo auditavel.

Inclui as constantes do endomorfismo GLV (beta, lambda) da secp256k1,
que permitem obter 3 chaves publicas relacionadas a partir de uma unica
multiplicacao escalar - a base da aceleracao 3x usada no modo endomorph.
"""

P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (GX, GY)

# Endomorfismo GLV (constantes publicas da secp256k1).
#   phi(x, y) = (BETA*x mod p, y)
#   phi(Q) = LAMBDA * Q  (multiplicacao escalar equivalente)
BETA = 0x7AE96A2B657C07106E64479EAC3434E99CF0497512F58995C1396C28719501EE
LAMBDA = 0x5363AD4CC05C30E0A5261C028812645A122E22EA20816678DF02967C1B23BD72

# Potencias quadraticas pre-computadas (validadas pelo selftest).
BETA2 = (BETA * BETA) % P
LAMBDA2 = (LAMBDA * LAMBDA) % N

# Ponto no infinito, representado como tupla vazia.
INF = ()


def inv(x, m=P):
    """Inverso modular pelo pequeno teorema de Fermat (p e n sao primos)."""
    return pow(x, m - 2, m)


def is_on_curve(pt):
    """Verifica se o ponto pertence a curva y^2 = x^3 + 7 (mod p)."""
    if not pt:
        return True
    x, y = pt
    return (y * y - (x * x * x + 7)) % P == 0


# ---------------------------------------------------------------------------
# Aritmetica em coordenadas Jacobianas (aceleracao: 1 inversao no final)
# ---------------------------------------------------------------------------

def _jac_double(pt):
    """Duplicacao em coordenadas Jacobianas."""
    X, Y, Z = pt
    if Y == 0:
        return (0, 0, 0)  # ponto no infinito
    YY = Y * Y % P
    S = 4 * X * YY % P
    M = 3 * X * X % P
    X3 = (M * M - 2 * S) % P
    Y3 = (M * (S - X3) - 8 * YY * YY) % P
    Z3 = 2 * Y * Z % P
    return (X3, Y3, Z3)


def _jac_add(pt1, pt2):
    """Adicao de dois pontos em coordenadas Jacobianas."""
    X1, Y1, Z1 = pt1
    X2, Y2, Z2 = pt2
    if Z1 == 0:
        return pt2
    if Z2 == 0:
        return pt1
    Z1Z1 = Z1 * Z1 % P
    Z2Z2 = Z2 * Z2 % P
    U1 = X1 * Z2Z2 % P
    U2 = X2 * Z1Z1 % P
    S1 = Y1 * Z2 * Z2Z2 % P
    S2 = Y2 * Z1 * Z1Z1 % P
    if U1 == U2:
        if S1 != S2:
            return (0, 0, 0)
        return _jac_double(pt1)
    H = (U2 - U1) % P
    R = (S2 - S1) % P
    HH = H * H % P
    HHH = H * HH % P
    V = U1 * HH % P
    X3 = (R * R - HHH - 2 * V) % P
    Y3 = (R * (V - X3) - S1 * HHH) % P
    Z3 = H * Z1 * Z2 % P
    return (X3, Y3, Z3)


def _jac_to_affine(pt):
    """Converte Jacobiana -> afim (1 inversao modular)."""
    X, Y, Z = pt
    if Z == 0:
        return INF
    invz = inv(Z)
    invz2 = invz * invz % P
    x = X * invz2 % P
    y = Y * invz2 % P * invz % P
    return (x, y)


def mul(k, pt=G):
    """Multiplicacao escalar k*pt (double-and-add, Jacobiano)."""
    k %= N
    if k == 0 or not pt:
        return INF
    x, y = pt
    R = (0, 0, 0)
    # caminho binario MSB -> LSB (menos duplicacoes desperdicadas)
    addend = (x, y, 1)
    for bit in bin(k)[2:]:
        R = _jac_double(R)
        if bit == "1":
            R = _jac_add(R, addend)
    return _jac_to_affine(R)


def endomorphism(pt):
    """Retorna (Q, phi(Q), phi^2(Q)) para um ponto Q = k*G.

    phi(x,y) = (BETA*x mod p, y). Os tres pontos correspondem aos
    escalares k, LAMBDA*k mod n e LAMBDA^2*k mod n. Com isso, uma unica
    multiplicacao escalar gera 3 enderecos candidatos.
    """
    if not pt:
        return (INF, INF, INF)
    x, y = pt
    return (pt, ((BETA * x) % P, y), ((BETA2 * x) % P, y))
