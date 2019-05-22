import io
from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair
from charm.toolbox.secretutil import SecretUtil
from charm.toolbox.ABEnc import ABEnc
from Crypto.Util.number import inverse
debug = False
class CPabe_sheme(ABEnc):
    def __init__(self, groupObj = False):
        ABEnc.__init__(self)
        global util, group        
        if groupObj == False:
            group = PairingGroup('SS512')
        else:
            group = groupObj
        util = SecretUtil(groupObj, debug)
                       
    def setup(self):
        g1, g2, u, v, d = group.random(G1), group.random(G2), group.random(G1), group.random(G1), group.random(G1)
        alpha, a = group.random(), group.random()        
        e_gg_alpha = pair(g1,g2) ** alpha
        g1_alpha = g1 ** alpha
        g2_alpha = g2 ** alpha
        g1_a = g1 ** a
        g2_a = g2 ** a
        msk = {'alpha':alpha}
        pk = {'g1':g1, 'g2':g2, 'e(gg)^alpha':e_gg_alpha, 'g1^a':g1_a, 'g2^a':g2_a, 'u':u, 'v':v, 'd':d}
        return (msk, pk)


    def keygen(self, pk, msk, attributes):        
        t = group.random()
        K = (pk['g2'] ** msk['alpha']) * (pk['g2^a'] ** t)
        K0 = (pk['g2'] ** t)
        k_x = [group.hash(s, G1) ** t for s in attributes]  
        K_x = {}
        for i in range(0, len(k_x)):
            K_x[ attributes[i] ] = k_x[i]    
        key = { 'K':K, 'K0':K0, 'K_x':K_x, 'attributes':attributes }
        return key  

    def encrypt(self, pk, M, M_, policy_str):
        # Extract the attributes as a list
        policy = util.createPolicy(policy_str)        
        p_list = util.getAttributeList(policy)
        # Generate ecoefficient for enc(M)
        s1 = group.random()
        C1 = (pk['e(gg)^alpha'] ** s1) * M
        C1_ = pk['g1'] ** s1
        C, D = {}, {}
        secret = s1
        shares = util.calculateSharesList(secret, policy)
        # ciphertext
        for i in range(len(p_list)):
            r1 = group.random()
            if shares[i][0] == p_list[i]:
               attr = shares[i][0].getAttribute() 
               C[ p_list[i] ] = ((pk['g1^a'] ** shares[i][1]) * (group.hash(attr, G1) ** -r1))
               D[ p_list[i] ] = (pk['g2'] ** r1)
        # Generate ecoefficient for enc(M')
        s2 = group.random()
        C2 = (pk['e(gg)^alpha'] ** s2) * M_
        C2_ = pk['g1'] ** s2
        C_, D_ = {}, {}
        secret = s2
        shares = util.calculateSharesList(secret, policy)
        # ciphertext
        for i in range(len(p_list)):
            r2 = group.random()
            if shares[i][0] == p_list[i]:
               attr = shares[i][0].getAttribute() 
               C_[ p_list[i] ] = ((pk['g1^a'] ** shares[i][1]) * (group.hash(attr, G1) ** -r2))
               D_[ p_list[i] ] = (pk['g2'] ** r2)
        C_h = (pk['u']**group.hash(str(M))) * (pk['v']**group.hash(str(M_))) * pk['d']
        CT = {'C_h':C_h, 'C1':C1, 'C1_':C1_, 'C':C, 'D':D , 'C2':C2, 'C2_':C2_, 'C_':C_, 'D_':D_,'policy':policy_str, 'attribute':p_list }
        
        if debug:
            print("cipher text:>>")
            for key, value in CT.items():
                print(key, '    <--->' ,value)
        return CT
  
    def decrypt(self, pk, sk, ct, mode='dir_dec'):
        policy = util.createPolicy(ct['policy'])
        pruned = util.prune(policy, sk['attributes'])
        if pruned == False:
            return False
        coeffs = util.getCoefficients(policy)
        numerator = pair(ct['C1_'], sk['K'])
        numerator_ = pair(ct['C2_'], sk['K'])      
        # create list for attributes in order...
        k_x, w_i = {}, {}
        for i in pruned:
            j = i.getAttributeAndIndex()
            k = i.getAttribute()
            k_x[ j ] = sk['K_x'][k]
            w_i[ j ] = coeffs[j]
            #print('Attribute %s: coeff=%s, k_x=%s' % (j, w_i[j], k_x[j]))
            # decrypt M
        C, D = ct['C'], ct['D']
        denominator = 1
        for i in pruned:
            j = i.getAttributeAndIndex()
            denominator *= ( pair(C[j] ** w_i[j], sk['K0']) * pair(k_x[j] ** w_i[j], D[j]) )           
        M = ct['C1'] * (denominator / numerator)
        # decrypt M'
        C_, D_ = ct['C_'], ct['D_']
        denominator_ = 1
        for i in pruned:
            j = i.getAttributeAndIndex()
            denominator_ *= ( pair(C_[j] ** w_i[j], sk['K0']) * pair(k_x[j] ** w_i[j], D_[j]) )          
        M_ = ct['C2'] * (denominator_ / numerator_)
     
        C_h = (pk['u']**group.hash(str(M))) * (pk['v']**group.hash(str(M_))) * pk['d']
       
        if C_h != ct['C_h']:
            if debug:
                print(M)
                print(M_)
                print('verification error!')
            return False
                   
        if debug:
            print('successful verificatin:>>', C_h)
        return M



    def gen_tk_out(self, pk, sk):
        #key = { 'K':K, 'K0':K0, 'K_x':K_x, 'attributes':attributes }
        z = group.random()
        tk = {}
        tk['attributes'] = sk['attributes']
        tk['K'] = sk['K']**(1/z)
        tk['K0'] = sk['K0']**(1/z)
        tk['K_x'] = {}
        K_x = sk['K_x']
        for each in K_x:
            tk['K_x'][each] = K_x[each]**(1/z)
        
        if debug:
            print('generating transform key...')
            print('transform key:>>', tk)
            print('retrieving key:>>', z)
        return tk, z
        
    def Transform(self, pk, tk, ct):
        policy = util.createPolicy(ct['policy'])
        pruned = util.prune(policy, tk['attributes'])
        if pruned == False:
            return False
        coeffs = util.getCoefficients(policy)
        numerator = pair(ct['C1_'], tk['K'])
        numerator_ = pair(ct['C2_'], tk['K'])      
        # create list for attributes in order...
        k_x, w_i = {}, {}
        for i in pruned:
            j = i.getAttributeAndIndex()
            k = i.getAttribute()
            k_x[ j ] = tk['K_x'][k]
            w_i[ j ] = coeffs[j]
            #print('Attribute %s: coeff=%s, k_x=%s' % (j, w_i[j], k_x[j]))
            # decrypt M
        C, D = ct['C'], ct['D']
        denominator = 1
        for i in pruned:
            j = i.getAttributeAndIndex()
            denominator *= ( pair(C[j] ** w_i[j], tk['K0']) * pair(k_x[j] ** w_i[j], D[j]) )           
        
        
        # decrypt M'
        C_, D_ = ct['C_'], ct['D_']
        denominator_ = 1
        for i in pruned:
            j = i.getAttributeAndIndex()
            denominator_ *= ( pair(C_[j] ** w_i[j], tk['K0']) * pair(k_x[j] ** w_i[j], D_[j]) )          
        
        
        T = (numerator / denominator)
        T_ = (numerator_ / denominator_)
           
           
        CT_ = {'T_h':ct['C_h'], 'T1':ct['C1'], 'T1_':T, 'T2':ct['C2'], 'T2_':T_}    
        return CT_
        
        

    def outsource(self, pk, ct, tk, rk):
        if debug:
            print('running outsourced algorithm...')
            
        CT_ = self.Transform(pk, tk, ct)
        
        if CT_['T_h'] != ct['C_h'] or CT_['T1'] != ct['C1'] or CT_['T2'] != ct['C2']:
            return false
        
        
        M = CT_['T1'] / (CT_['T1_']**rk)
        M_ = CT_['T2'] / (CT_['T2_']**rk)
        
        C_h = (pk['u']**group.hash(str(M))) * (pk['v']**group.hash(str(M_))) * pk['d']
        if C_h != ct['C_h']:
            if debug:
                print(M)
                print(M_)
                print('outsourced verification error!')
            return False
        if debug:
            print('successful outourced verificatin:>>', C_h)
        return M
        
def main():

    #Get the eliptic curve with the bilinear mapping feature needed.

    groupObj = PairingGroup('SS512')
    cpabe = CPabe_sheme(groupObj)
    (msk, pk) = cpabe.setup()
    pol = '(ONE or THREE) and (TWO or FOUR)'
    attr_list = ['THREE', 'ONE', 'TWO']
    if debug:
        print('Acces Policy: %s' % pol)
    if debug:
        print('User credential list: %s' % attr_list)
    m = groupObj.random(GT)
    m_ = groupObj.random(GT)
    if debug:
        print('message:>>', m)
        print('message for verification:>>', m_)
    cpkey = cpabe.keygen(pk, msk, attr_list)
    if debug:
        print("\nSecret key: %s" % attr_list)
    if debug:
        groupObj.debug(cpkey)
    cipher = cpabe.encrypt(pk, m, m_, pol)
    if debug:
        print("\nCiphertext...")
    if debug:
        groupObj.debug(cipher)
    orig_m = cpabe.decrypt(pk, cpkey, cipher)
    assert m == orig_m, 'FAILED Decryption!!!'

    if debug:
        print('Successful Decryption!')
        
    tk, rk = cpabe.gen_tk_out(pk, cpkey)

    orig_m = cpabe.outsource(pk, cipher, tk, rk)

    assert m == orig_m, 'FAILED Decryption!!!'



    del groupObj



if __name__ == '__main__':

    debug = True

    main()
