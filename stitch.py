filenames = ['json/SUM22CIS.json', 'json/SUM22EEC.json', 'json/SUM22ESC.json']
with open('sum22pack.json', 'w') as outfile:
    outfile.write('[')
    for fname in filenames:
        with open(fname) as infile:
            for line in infile:
                outfile.write(line)
            outfile.write(',')
    outfile.write(']')