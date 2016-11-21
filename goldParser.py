# read a sentence into a list of words, each being a list of items in CoNLL format rows
def readSentence(sFile):
   file = open(sFile) # the file object
   sent = [] # the return value
   for line in file:
      line = line.strip() # remove white characters
      if not line: # new line encountered
         yield sent # return the current sentence
         sent = [] # initialize the next sentence to return
      else:
         sent.append(line.split('\t')) # add word in
   if sent: # if there is still a last sentence without ending newline
      yield sent # return this sentence
   file.close() # close file object

# obtain a dict sid --> dWord and a mapping from did to sid
def sortDst(sent):
   ret = {} # sid --> word dict
   d2s = {} # d id --> sid
   col = {} # collapsed to host
   for row in sent:
      d = {'id':int(row[0]), # deep id
           'token':row[1],
           'pos':row[4],
           'head':int(row[8]), # deep id of the head word
           'label':row[10]}
      for s in row[6].split('|'): # for each feature
         k, v = s.split('=', 1)
         d[k]=v
      if ("pro" not in d['id0'] and "bis" not in d['id0']):
         d['id0']=int(d['id0'])-1 # sid
#      d['id1']=int(d['id1'])-1
      if 'id1' in d:
         d['id1'] = int(d['id1'])-1
         col[d['id1']] = d['id0']
      if 'id2' in d:
         d['id2'] = int(d['id2'])-1
         col[d['id2']] = d['id0']
      if 'id3' in d:
         d['id3'] = int(d['id3'])-1
         col[d['id3']] = d['id0']
      if 'id4' in d:
         d['id4'] = int(d['id4'])-1
         col[d['id4']] = d['id0']
      if 'id5' in d:
         d['id5'] = int(d['id5'])-1
         col[d['id5']] = d['id0']

      #assert not 'id5' in d
      ret[d['id0']]=d
      d2s[d['id']]=d['id0']
   return ret, d2s, col

# get the head, left modifiers, right modifiers of each word from shallow sentence tree
def sortSst(sent):
   heads = [] # heads of each word, index from zero
   left_mods = [] # left modifiers of each word
   right_mods = [] # right modifiers of each word
   words = []
   pos = []
   morphs = []
   deprels = []
   for i in range(len(sent)):
      heads.append(-1) 
      left_mods.append([])
      right_mods.append([])
      words.append([])
      pos.append([])
      morphs.append([])
      deprels.append([])
   for i in range(len(sent)):
      h = int(sent[i][8]) - 1 # head from zero
      w = str(sent[i][1]) # w
      p = str(sent[i][4]) # pos
      m = str(sent[i][6]) # morph
      d = str(sent[i][10]) # deprel
      heads[i] = h
      words[i] = w
      pos[i] = p
      morphs[i] = m
      deprels[i] = d
      if h != -1:
         if i<h:
            left_mods[h].append(i)
         else:
            assert i > h
            right_mods[h].append(i)
      else:
         root = i
   return root, heads, left_mods, right_mods, words, pos, morphs, deprels

# associate the modifiers of collapsed nodes to their heads
def reconSst(root, heads, left_mods, right_mods, dtree, d2s, col):
#   assert root in dtree
   ret_root = -1
   ret_heads = []
   ret_left_mods = []
   ret_right_mods = []
   for i in range(len(heads)):
      if i in dtree: # and not heads[i] in dtree:
#         assert heads[heads[i]] in dtree
         if dtree[i]['head'] == 0: # root of dtree
            ret_heads.append(-1) # make it root of shallow tree
         else: # otherwise find dhd
            ret_heads.append(d2s[dtree[i]['head']]) #(heads[heads[i]])
      else: # for non-existent words, root words and words that have a existent head, reduce to head
         if i in col:
            ret_heads.append(col[i])
         else:
            ret_heads.append(heads[i])
      ret_left_mods.append([])
      ret_right_mods.append([])
   for i in range(len(ret_heads)):
      h = ret_heads[i]
      if h != -1:
         if i<h:
            ret_left_mods[h].append(i)
         else:
            assert i>h
            ret_right_mods[h].append(i)
      else:
         assert ret_root == -1
         ret_root = i
#   assert ret_root == root
   return ret_root, ret_heads, ret_left_mods, ret_right_mods

# find action sequence by reading both the shallow syntactic structure and the deep
def getGoldActions(sSent, dSent):
   slen = len(sSent) # shallow word count
   dtree, d2s, col = sortDst(dSent) # deep tree, did-->sid
   root, heads, left_mods, right_mods, words, pos, morphs, deprels= sortSst(sSent) # shallow tree items
   root, heads, left_mods, right_mods = reconSst(root, heads, left_mods, right_mods, dtree, d2s, col) # modifiers of collapsed nodes
   actions = [] # return value actions
   actions.append("[][")
   k=0;
   for w in words:
      actions.append(w+"-"+deprels[k]+"#"+morphs[k])
      k=k+1
      if not k == len(pos):
         actions.append(", ")
   actions.append("]\n")
   def getActions(n, actions): #recursive
      stack = []
      for lm in  left_mods[n]: # for each left modifier of n in the shallow tree
         getActions(lm, actions) # print out all its actions
         stack.append(lm) # shifted onto stack
      #actions.append('SH-%s-%d' % (sSent[n][4], n)) # shift n pos
      actions.append("SH\n"+"[][]"+"\n") # shift n pos
      while stack: # now reduce left_mods
         lm = stack.pop(-1) # the S1 node
         if lm in dtree: # if this is also a node in dSynt
            assert d2s[dtree[lm]['head']] == n # assert that the head in dSyntt, when mapped into the shallow synax (d2s), is equal to n itself
            actions.append('LA(%s' % dtree[lm]['label']+")\n"+"[][]"+"\n") # do left arc
         else: # if the node is not in the dS
            actions.append('LC'+"\n"+"[][]"+"\n") # just collapse
      for rm in right_mods[n]: # for each right modifier
         getActions(rm, actions) # simply get it sorted out on the tree
         if rm in dtree: # and then decide whether to collapse or arc
            #print rm, d2s[dtree[rm]['head']], n
            assert d2s[dtree[rm]['head']] == n
            actions.append('RA(%s' % dtree[rm]['label']+")\n"+"[][]"+"\n")
         else:
            actions.append('RC'+"\n"+"[][]"+"\n")

   getActions(root, actions)
   return actions

# the main function
if __name__ == '__main__':
   import sys
   dfile = readSentence(sys.argv[1])
   sfile = readSentence(sys.argv[2])
   print "\n"
   try:
      while True:
         sSent = sfile.next()
         dSent = dfile.next()
         print ''.join(getGoldActions(sSent, dSent))
   except StopIteration:
      pass
