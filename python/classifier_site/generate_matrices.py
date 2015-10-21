import pickle

a = pickle.load(open('id_to_index.pickle','r+'))
index_to_id = pickle.load(open('index_to_id.pickle','r+'))

S = [np.zeros(10000,1065) for _ in range(8)]

types = ['d_d_sim', 'd_d_w2vsim', 'd_t_sim', 'd_t_w2vsim', 't_d_sim', 't_d_w2vsim', 't_t_sim', 't_t_w2vsim']
for k,s in enumerate(S):
  for i,b in enumerate(biz):
    for j in range(1065):
      s[i,j] = b.features_dict[a[j]][types[k]]