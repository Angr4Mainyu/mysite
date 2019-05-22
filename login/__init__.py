# from cpabe import PairingGroup,CPabe_sheme
# from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair,serialize,deserialize

# groupObj = PairingGroup('SS512')
# cpabe = CPabe_sheme(groupObj)
# (msk, pk) = cpabe.setup()

# with open('msk.txt','w') as f:
#     for i in msk:
#         f.write(i+' '+str(groupObj.serialize(msk[i]),encoding='utf-8')+'\n')
# with open('pk.txt','w') as f:
#     for i in pk:
#         f.write(i+' '+str(groupObj.serialize(pk[i]),encoding='utf-8')+'\n')

# msk1=dict()
# with open('msk.txt','r') as f:
#     for line in f.readlines():
#         line=line.strip().split()
#         msk1[line[0]]=groupObj.deserialize(bytes(line[1],encoding='utf-8'))
# pk1=dict()
# with open('pk.txt','r') as f:
#     for line in f.readlines():
#         line=line.strip()
#         i=str.find(line,' ')
#         pk1[line[:i]]=groupObj.deserialize(bytes(line[i+1:],encoding='utf-8'))