"""Esempi eseguibili e identità booleane verificabili esaustivamente."""
BOOL=[
 ('~A',None),('A & B',None),('A | B',None),('A ^ B',None),('~(A ^ B)',None),('~(A & B)',None),('~(A | B)',None),
 ('~(A & B)','~A | ~B'),('~(A | B)','~A & ~B'),('A | A','A'),('A & A','A'),
 ('A | (A & B)','A'),('A & (A | B)','A'),('A & (B | C)','(A & B) | (A & C)'),
 ('A | (B & C)','(A | B) & (A | C)'),('A | ~A','1'),('~~A','A'),
 ('(A & B) | (~A & C) | (B & C)','(A & B) | (~A & C)'),
 ('A ^ B','(~A & B) | (A & ~B)'),('A ^ B','(~A & B) | (A & ~B)'),
 ('A ^ B','(A | B) & (~A | ~B)'),('A | 0','A'),
 ('(A & B) | (A & ~B)','A'),('~A | B',None)]
DIGITAL={1:('A ^ B',None),2:('A & B',None),3:('A ^ B ^ C',None),4:('(A & B) | (A & C) | (B & C)',None),6:('(~S & A) | (S & B)',None),12:('~(A ^ B) & (C ^ A)',None),17:('(J & ~Q) | (~K & Q)',None),18:('T ^ Q',None)}

def attach_logic(card):
    pair=BOOL[int(card['id'].split('-')[1])-1] if card['category']=='bool' else DIGITAL.get(int(card['id'].split('-')[1])) if card['category']=='digitale' else None
    if pair:
        card['logic']={'expression':pair[0],'equivalent_to':pair[1]}
        if card['category']=='bool' or card['id'] in ('digitale-001','digitale-002'):card['plot']=None
