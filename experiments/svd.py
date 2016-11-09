from sklearn.decomposition import TruncatedSVD
from sklearn.utils.extmath import randomized_svd
from scipy.spatial.distance import cosine
import numpy as np

A = [
		[1,0,1,0,0], # romeo
		[1,1,0,0,0], # juliet
		[0,1,0,0,0], # happy
		[0,1,1,0,0], # dagger
		[0,0,0,1,0], # live
		[0,0,1,1,0], # die
		[0,0,0,1,0], # free
		[0,0,0,1,1]  # new-hampshire
	]
X = np.array(A)

'''
SVD = TruncatedSVD(n_components=2) 
U = SVD.fit_transform(A)
Sigma = SVD.explained_variance_ratio_
VT = SVD.components_'''

U, Sigma, VT = randomized_svd(X, n_components=2, n_iter=5, random_state=42)
U = np.negative(U)
VT = np.negative(VT)
S = [[0 for x in Sigma] for x in Sigma]
for i in range(len(Sigma)):
	S[i][i] = Sigma[i]

# print(U)
# print(S)
# print(VT)

K_Terms = np.dot(U, S)
K_Docs = np.dot(S, VT)

#print(K_Terms)
# print(K_Docs)

# query: romeo die
Q = [[0], [0]]
for i in range(len(Q)):
	Q[i] = (K_Terms[0][i] + K_Terms[5][i]) / 2

print(Q)

for i in range(len(K_Docs[0])):
	d = [K_Docs[0][i], K_Docs[1][i]]
	sim = cosine(d, Q)
	print("doc" + str(i+1) + ": " + str(sim))

# print(K_Terms)