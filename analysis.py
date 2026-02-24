# analysis.py

# 1. Map Names to Single Letters (The Scientific Standard)
aa_to_letter = {
    'Alanine': 'A', 'Arginine': 'R', 'Asparagine': 'N', 'Aspartic Acid': 'D',
    'Cysteine': 'C', 'Glutamine': 'Q', 'Glutamic Acid': 'E', 'Glycine': 'G',
    'Histidine': 'H', 'Isoleucine': 'I', 'Leucine': 'L', 'Lysine': 'K',
    'Methionine (START)': 'M', 'Phenylalanine': 'F', 'Proline': 'P',
    'Serine': 'S', 'Threonine': 'T', 'Tryptophan': 'W', 'Tyrosine': 'Y',
    'Valine': 'V', 'STOP': '*'
}

amino_acid_map = {
    'ATA':'Isoleucine', 'ATC':'Isoleucine', 'ATT':'Isoleucine', 'ATG':'Methionine (START)',
    'ACA':'Threonine', 'ACC':'Threonine', 'ACG':'Threonine', 'ACT':'Threonine',
    'AAC':'Asparagine', 'AAT':'Asparagine', 'AAA':'Lysine', 'AAG':'Lysine',
    'AGC':'Serine', 'AGT':'Serine', 'AGA':'Arginine', 'AGG':'Arginine',
    'CTA':'Leucine', 'CTC':'Leucine', 'CTG':'Leucine', 'CTT':'Leucine',
    'CCA':'Proline', 'CCC':'Proline', 'CCG':'Proline', 'CCT':'Proline',
    'CAC':'Histidine', 'CAT':'Histidine', 'CAA':'Glutamine', 'CAG':'Glutamine',
    'CGA':'Arginine', 'CGC':'Arginine', 'CGG':'Arginine', 'CGT':'Arginine',
    'GTA':'Valine', 'GTC':'Valine', 'GTG':'Valine', 'GTT':'Valine',
    'GCA':'Alanine', 'GCC':'Alanine', 'GCG':'Alanine', 'GCT':'Alanine',
    'GAC':'Aspartic Acid', 'GAT':'Aspartic Acid', 'GAA':'Glutamic Acid', 'GAG':'Glutamic Acid',
    'GGA':'Glycine', 'GGC':'Glycine', 'GGG':'Glycine', 'GGT':'Glycine',
    'TCA':'Serine', 'TCC':'Serine', 'TCG':'Serine', 'TCT':'Serine',
    'TTC':'Phenylalanine', 'TTT':'Phenylalanine', 'TTA':'Leucine', 'TTG':'Leucine',
    'TAC':'Tyrosine', 'TAT':'Tyrosine', 'TGC':'Cysteine', 'TGT':'Cysteine',
    'TGG':'Tryptophan', 'TAA':'STOP', 'TAG':'STOP', 'TGA':'STOP'
}

def clean_sequence(seq):
    return seq.strip().upper().replace(" ", "").replace("\n", "").replace("\r", "")

def is_valid_dna(seq):
    return all(base in "ATGC" for base in seq)

def sequence_length(seq):
    return len(seq)

def gc_content(seq):
    if not seq: return 0
    g = seq.count('G')
    c = seq.count('C')
    return round(((g + c) / len(seq)) * 100, 2)

def translate_dna(seq):
    protein_data = []
    
    # 1. Find Start Codon
    start_index = seq.find("ATG")
    if start_index == -1:
        return [] 

    # 2. Translate
    for i in range(start_index, len(seq) - 2, 3):
        codon = seq[i:i+3]
        name = amino_acid_map.get(codon, "Unknown")
        
        if name == "STOP":
            break 
            
        # Get the correct single letter code
        letter = aa_to_letter.get(name, "?")

        protein_data.append({
            "codon": codon,
            "name": name,
            "letter": letter # We now send the letter too!
        })
        
    return protein_data

def get_chem_profile(protein_data):
    profile = {"hydrophobic": 0, "polar": 0, "acidic": 0, "basic": 0, "charged": 0}
    cats = {
        'hydrophobic': ['Alanine', 'Valine', 'Leucine', 'Isoleucine', 'Phenylalanine', 'Tryptophan', 'Methionine (START)', 'Proline', 'Glycine'],
        'polar': ['Serine', 'Threonine', 'Cysteine', 'Tyrosine', 'Asparagine', 'Glutamine'],
        'acidic': ['Aspartic Acid', 'Glutamic Acid'],
        'basic': ['Lysine', 'Arginine', 'Histidine'],
        'charged': ['Arginine', 'Glutamic Acid', 'Lysine', 'Histidine']
    }
    for aa in protein_data:
        aa_name = aa['name']
        for category, members in cats.items():
            if aa_name in members:
                profile[category] += 1
    return profile

def reverse_complement(seq):
    complement_map = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    complement = "".join(complement_map.get(base, base) for base in seq)
    return complement[::-1]