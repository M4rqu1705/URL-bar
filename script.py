import pprint

accents = 'á,Á,é,É,í,Í,ó,Ó,ú,Ú,ñ,Ñ,ü,Ü,¿,¡'.split(',')
normal = 'a,A,e,E,i,I,o,O,u,U,n,N,u,U,?,!'.split(',')
codes = '225,193,233,201,237,205,243,211,250,218,241,209,252,220,161,191'.split(',')

mapping = dict()
for i in range(len(accents)):
    mapping[accents[i]] = [normal[i], codes[i]]

for key in mapping:

        if char == 225:     # á
            string += 'á'
            return ord('a')
    string = f"""        elif char == {mapping[key][1]}:     # {key}
                string += '{key}'
                return ord('{mapping[key][0]}')"""
    print(string)
