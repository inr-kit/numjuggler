import re
from numjuggler import numbering as mn
from numjuggler import parser as mp


#########################################
# define patterns to be found in string #
#########################################


# used in card_split
celmat=re.compile(r"(?P<cel>^ *\d+) +(?P<scnd>(\d+|like))",re.I)      # identify first two entries on cell card (cell name, material)
grlnumber=re.compile(r"[-+]?(\d+\.\d+|\.\d+|\d+\.?)(e[+-]\d+)?",re.I) # identify a general number form signed integer, float or exponential
param=re.compile(r"((^|\n {5})[\(\):\-\+\d+\.\# ]*)([\*a-z])",re.I)   # identity begining of the paramter part of the cell card
likebut=re.compile(r"but",re.I)                                       # identify likebut  card
trans=re.compile(r"trcl|fill= *\d+[ c\$\n]*\(,",re.I)                 # identify tranformed card

# user in get_stat function
reword=re.compile(r"(\d+|\(|\)|:|\#)")                    # word identification in cell line
compcell=re.compile(r"\#\d")                              # identify hashcell complement operator

# used in Complementary operator function
number=re.compile(r"(?P<number>[-+]?\d+)")                                     # signed (+-) (or not) numbers
# leftp=re.compile(r"^ *(?P<left>[-\d\(\#])",re.M)                               # identify first valid character
leftp=re.compile(r"(?P<left>[-+\d\(\#])",re.I)                                  # identify first valid character
rightp=re.compile(r"(?P<right>[ c\$\n]*$)",re.I)                               # identify last valid character
#interblk=re.compile(r"(?P<previous>\d)(?P<next>(( +| *(\$)?\n(C\n)* *)[-+]?\d))") # two numbers separated by blank (or newline or comments)
#intercls=re.compile(r"(?P<previous>\))(?P<next>(( *| *(\$)?\n(C\n)* *)[-+]?\d))") # closed parenthesis followed by number
#interopn=re.compile(r"(?P<previous>\d)(?P<next>(( *| *(\$)?\n(C\n)* *)\())")   # number followed by opened parenthesis
#intercop=re.compile(r"(?P<previous>\))(?P<next>(( *| *(\$)?\n(C\n)* *)\())")   # closed parenthesis followed by opened parenthesis
interblk=re.compile(r"(?P<previous>\d)(?P<next>(( +| *((\n *)?\$|\nC)*\n *)[-+]?\d))") # two numbers separated by blank (or newline or comments)
intercls=re.compile(r"(?P<previous>\))(?P<next>(( *| *((\n *)?\$|\nC)*\n *)[-+]?\d))") # closed parenthesis followed by number
interopn=re.compile(r"(?P<previous>\d)(?P<next>(( *| *((\n *)?\$|\nC)*\n *)\())")   # number followed by opened parenthesis
intercop=re.compile(r"(?P<previous>\))(?P<next>(( *| *((\n *)?\$|\nC)*\n *)\())")   # closed parenthesis followed by opened parenthesis
colonamp=re.compile(r"[:&]")                                                   # colon or amperserand

# used for remove redundant parenthesis function
mostinner=re.compile(r"\([^\(^\)]*\)")                                      # identify most inner parentheses
bracketsemi=re.compile(r"[\]\[;]")                                          # square bracket or semicolon
blnkline=re.compile(r"^ *\n",re.M)                                          # identify blank line
contline=re.compile(r"\n {0,4}(?P<start>[^c^ ])",re.I)                      # identify character other than 'C' in fisrt 5 columns
comdollar=re.compile(r"\n(?P<blnk> *)\$")                                   # identify dollar on 'blank line'
startgeom=re.compile(r"(?P<previous>^ *)(?P<start>[\-\+\d])")               # identify beginning of the geomtric part
endgeom=re.compile(r"(?P<last>\d)(?P<next> *((\n *)?\$|\nc)?(\n *)?$)",re.I)    # identify end of the geomtric part
#endgeom=re.compile(r"(?P<last>\d)(?P<next> *(\$|\nc)?(\n *)?$)",re.I)                      # identify end of the geomtric part

# other
rehash=re.compile(r"# *(\d+|\()")                                             # find beginning of complementary operator (both cell and surf)
parent=re.compile(r"[\(|\)]")                                               # position of open and close parenthesis (get_hashcell)
gline=re.compile(r"(^ ?[\(\):\-\+\d+\.\# ]+|\n {5}[\(\):\-\+\d+\.\# ]+)",re.I)  # valid geometric part of the line       (remove/restore_comments)
comments=re.compile(r"((\n *)?\$|\n *c)",re.I)                               # begining of comment part               (remove/restore_comments)
#comments=re.compile(r"\$|\n *c",re.I)                               # begining of comment part               (remove/restore_comments)


############################################################
# Auxiliary functions used in regular expresion functions  #
############################################################
def redundant(m,geom):
   """ check if the inner parentheses are redundant """
   term = m.group()

   # Find first valid character at the left of the  parenthese
   hashsmb = False
   leftOK= True
   left = m.start()-1
   while left > -1:
       if geom[left] in ('\n','C','$',' '):
          left -= 1
       else:
          if geom[left] not in ('(',':') : leftOK  = False
          if (geom[left] == '#') : hashsmb  = True
          break

  # if hash symbol found means parentheses delimits complementary
  # cell defined with surface. Theses parentheses are not redundants
   if hashsmb : return False

  # check if no ':' (or) are inside the parenthese
  # if not, parentheses are redundants
   if (term.find(':') == -1) : return True

  # Find first valid character at the right of the  parenthese
   rightOK= True
   right = m.end()
   while right < len(geom)  :
       if geom[right] in ('\n','C','$',' '):
          right += 1
       else:
          if geom[right] not in (')',':') : rightOK  = False
          break

  # if parentheses are like:
  # {( or : } ( ....... ) {) or :}
  # parentheses are redundants

   if leftOK and rightOK :
       return True
   else:
       return False

# function used in Regular expresion sub function
# function user in complementary function
# change the sign of the number
def chgsign(m):
    num=m.group(0)
    if num[0] == '-':
      return num[1:]
    if num[0] == '+':
      return '-'+num[1:]
    else:
      return '-'+num

# function used in Regular expersion sub function
# function user in complementary function
# change ':' in ')('  and
#        '&' in ':'
def repl_inter_union(m):
    if m.group(0) == ':' :
       return ')('
    else :
       return ':'

# function used in Regular expersion sub function
# function user in remove_redundant function
# restore curve parentheses and colon characters
def reverse_repl(m):
    symb=m.group(0)
    if symb == '[' :
      return '('
    elif symb == ']' :
      return ')'
    else :
      return ':'
############################################################

def complementary(ccell) :
    """ return the complementary cell """

    if (ccell.str[-1] == '\n') : ccell.str=ccell.str[:-1]

    # simplify comment in geometry string
    ccell.remove_comments()

    # insert external parenthesis
    ccell.str= re.sub(leftp,r"(\g<left>",ccell.str,count=1)
    ccell.str= re.sub(rightp,r")\g<right>",ccell.str,count=1)

    # insert '&' as intersection operator
    ccell.str=re.sub(interblk,r"\g<previous>&\g<next>",ccell.str)  # change intersection separate by blank space ie: "number number"
    ccell.str=re.sub(interblk,r"\g<previous>&\g<next>",ccell.str)  # 2nd pass intersection blank space (require 2 pass)
    ccell.str=re.sub(intercls,r"\g<previous>&\g<next>",ccell.str)  # change intersection close parenthesis ie: ") number"
    ccell.str=re.sub(interopn,r"\g<previous>&\g<next>",ccell.str)  # change intersection open  parenthesis ie: "number ("
    ccell.str=re.sub(intercop,r"\g<previous>&\g<next>",ccell.str)  # change intersection close-open  parenthesis ie: ") ("

    # invert operators
    # substitute colon by ')(' and  '&' by colon
    ccell.str=re.sub(colonamp,repl_inter_union,ccell.str)
    ccell.remove_redundant(remove_com=False)

    # Change signs
    ccell.str=re.sub(number,chgsign,ccell.str)

    # insert external parenthesis
    ccell.str= re.sub(leftp,r"(\g<left>",ccell.str,count=1)
    ccell.str= re.sub(rightp,r")\g<right>",ccell.str,count=1)

# restore original comments
    ccell.restore_comments()
    return ccell.str

############################################################
class cline():
   def __init__(self,line):
     self.str=line

   def remove_comments(self):
      """ Remove the text of the comment. The symbol 'C' or '$' is
kept in the line"""
      celltab = re.split(gline,self.str)
      cont=True
      while cont:
         try:
            celltab.remove('')
         except:
            cont=False

      self.__comtab__=[]
      for i,s in enumerate(celltab) :
         c = comments.match(s)
         if ( c ):
            self.__comtab__.append(s)
            celltab[i] = c.group()

      self.str=''.join(celltab)
      return

   def restore_comments(self):
      """ Restore the text of the comment."""
      celltab = re.split(gline,self.str)
      cont=True
      while cont:
         try:
            celltab.remove('')
         except:
            cont=False

      j = 0
      for i,s in enumerate(celltab) :
          c = comments.match(s)
          if ( c ):
             celltab[i] = self.__comtab__[j]
             j += 1

      self.str = ''.join(celltab)
      return


   def remove_redundant(self,remove_com=True,remopt='nochg'):
      """ return cell without redundant parenthesis """

      #simplify comment in geometry string
      if remove_com: self.remove_comments()
      geom = self.str

      if (remopt == 'nochg' and geom.find(')') == -1 ) :
          self.removedp = None
          return

      porg=self.countP()
      # Loop until no redundant parentheses are found
      cont = True
      while cont:
        # Loop over most inner parentheses
        pos = 0
        cont = False
        while True :
          m = mostinner.search(geom,pos)
          if not m : break
          cont = True
          if redundant(m,geom):
             # remove redundant parentheses
             geom = geom[:m.start()]+ ' ' + geom[m.start()+1:m.end()-1]+ ' ' + geom[m.end():]
          else:
             # replace no redundant parentheses by [] and : by ;
             term = geom[m.start()+1:m.end()-1].replace(':',';')
             geom = geom[:m.start()] + '[' + term + ']' + geom[m.end():]
          pos = m.end()

      # restore curved parenthesis and colon
      geom=re.sub(bracketsemi,reverse_repl,geom)

      # remove possible blank line
      geom=re.sub(blnkline,'',geom)

      # ensure 5 blanks continous line
      geom=re.sub(contline, r'\n     \g<start>',geom)

      if remopt != 'all' :
        # add parenthesis to set geom as MCNP complex cell
        if geom.find(':') == -1 and geom.find('#') == -1 :
           geom=re.sub(startgeom,r'\g<previous>(\g<start>',geom)
           geom=re.sub(endgeom,r'\g<last>)\g<next>',geom)

      # restore original comments
      self.str = geom
      pmod=self.countP()
      if remove_com: self.restore_comments()

      # subtitute comment $ with  blank line
      self.str=re.sub(comdollar,r'\nC\g<blnk>',self.str)
      pdiff = [x-y for x,y in zip(pmod,porg)]
      self.removedp=pdiff
      return


   def get_hashcell(self,start=0):
      """ get the complementary cell defined with surfaces combination """
      count=0
      for p in  parent.finditer(self.str,start):
         if (p.group() == '(') :
           count += 1
         else:
           count -= 1
         if (count == 0 ):
           end=p.end()
           cell=cline(self.str[start+1:end])
           break
      return cell,end

   def countP(self):
      lp=self.str.count('(')
      rp=self.str.count(')')
      return (lp,rp)
############################################################
class cell_card_string():

   def __init__(self,card):
      self.stat={ 'word'     : None  ,\
                  'hashcell' : None  ,\
                  'hashsurf' : None  ,\
                  'hash'     : None   }

      self.__card_split__(card)
      return

   def __card_split__(self,cardin):
      """ Split the card string in three parts :
              - headstr : string containing the cell name, mat number and density (if mat != 0) of the cell
              - geom    : cline class containing the part of the geometric definition of the cell
              - geom    : cline class containing the cell parameters part
           hproc is true if the complementary operator of the cell can be substituted"""

      m=celmat.match(cardin)
      self.hproc=True
      if m.group('scnd').lower() == 'like':
         self.headstr    =       cardin[:m.start('scnd')]
         s = likebut.search(cardin,m.end('scnd'))
         self.geom = cline(cardin[m.start('scnd'):s.end()])
         self.parm = cline(cardin[s.end():])
         self.hproc=False
      elif m.group('scnd') == '0':
         cstart=m.end('scnd')
      else :
         p=grlnumber.search(cardin,m.end('scnd'))
         cstart=p.end()

      if self.hproc:
         self.headstr = cardin[:cstart]
         cellcard=cline(cardin[cstart:])
         cellcard.remove_comments()
         m = param.search(cellcard.str)
         if m:
            linecut = cellcard.str[:m.end(1)].count('\n')
         else:
            linecut = cellcard.str.count('\n')

         cellcard.restore_comments()

         # look for the last line geometry string
         if linecut != 0 :
            pos=0
            c=0
            while c != linecut :
               pos=cellcard.str.find('\n',pos)
               c += 1
            m = param.search(cellcard.str,pos)

         if m:
            start = m.end(1)
            self.geom = cline(cellcard.str[:start])
            self.parm = cline(cellcard.str[start:])

            # look for transformation in cell parameters
            self.parm.remove_comments()
            m = trans.search(self.parm.str)
            if m : self.hproc = False
            self.parm.restore_comments()
         else :
            self.geom = cline(cellcard.str)
            self.parm = cline('')

      return

   def get_stat(self,remove_com=True):
      """ Count and return the number of words and hashes on the line."""

      if remove_com : self.geom.remove_comments()

      words    = len(reword.findall(self.geom.str))
      hashcell = len(compcell.findall(self.geom.str))
      hashtot  = self.geom.str.count('#')

      self.stat={ 'words'   : words,
                  'hash'    : hashtot,
                  'hascell' : hashcell,
                  'hashsur' : hashtot-hashcell }
      if remove_com : self.geom.restore_comments()
      return [words, hashtot, hashcell, hashtot-hashcell]

   def get_lines(self):
      """ split string card in the format Cards.lines of Cards object"""
      card=self.headstr + self.geom.str + self.parm.str

      # remove blank line introduced during the process
      card=re.sub(blnkline,'',card)

      # subtitute comment $ with  blank line
      card=re.sub(comdollar, r'\nC\g<blnk>',card)

      # ensure 5 blanks continous line
      card=re.sub(contline, r'\n     \g<start>',card)

      if (card[-1] == '\n') : card=card[:-1]
      return  list(map(lambda x: x+'\n' ,card.split('\n')))


############################################################
# function called by main.py
############################################################

def remove_hash(cards,logfile=''):

#########################################################################
    def remove(card,cname):
       """ remove complementary operator and subtitute by complementary cell """
       celline=''.join(card.lines)
       cardstr = cell_card_string(celline)
       cardstr.get_stat()
       if (not cardstr.hproc) or (cardstr.stat['hash'] == 0) :return   # no complementary operator or cannot be # cannot be removed

       cell=cardstr.geom

       # find all operators in the cell and
       # substitute all complementary operators
       # locate object in list to reverse iteration
       hashgroup=[]
       start = 0
       hlist = []

       lencel = len(cell.str)
       while True:
          ic   = cell.str.lower().find('c',start)
          idol = cell.str.find('$',start)
          if idol < 0 : idol = lencel
          if ic   < 0 : ic   = lencel
          end = min(idol, ic)
          for m in (rehash.finditer(cell.str,start,end)):
             hashgroup.append(m)
          start = cell.str.find('\n',end)
          if (end  == lencel) : break

       for m in reversed(hashgroup):
          start=m.start()
          if m.group(1) == '(':                       # complementary cell defined as surface intersections
             hcell,end=cell.get_hashcell(start)
             hlist.append(('surf',hcell.str))
             cellmod=cell.str[0:start] + complementary(hcell) + cell.str[end:]
          else:
             hcname=int(m.group(1))                  # complementary cell defined with other cell index
             remove(cards[dcel[hcname]],hcname)      # remove complementary operator in new cell if necessary
             hlist.append(('cell',hcname))
             end=m.end()
             celline=''.join(cards[dcel[hcname]].lines)
             hcell=cell_card_string(celline).geom
             cellmod=cell.str[0:start]+                                  \
                 '\nC  Complementary cell %i start\n' %hcname  \
                 + '      '+complementary(hcell) +                          \
                 '\nC  Complementary cell %i end  \n' %hcname  \
                 + cell.str[end:]

          # complementary cell inserted  at the operator location
          cardstr.geom.str = cellmod

          cards[dcel[cname]].cstrg = True
          cards[dcel[cname]].lines = cardstr.get_lines()
       if wrtlog:
          logtab.append((int(cname),hlist))
       return
#########################################################################

    dcel={}
    wrtlog = False
    if logfile != '' :
      wrtlog = True
      logtab = []
    for i,c in enumerate(cards):
         if c.ctype == mp.CID.cell:
              c.get_values()
              dcel[c.name]=i
    for c in cards:
         if c.ctype == mp.CID.cell:
              remove(c,c.name)

    if wrtlog :
       logtab.sort
       flog = open(logfile,'w')
       for cell in logtab:
          flog.write(' Cell {:>9} :\n'.format(cell[0]))
          cc = False
          for h in cell[1]:
             if (h[0] == 'surf'):
                cc = True
                flog.write('\n      Complementary cell definition :\n')
                break
          if cc:
             for i,h in enumerate(cell[1]):
                if (h[0] == 'surf'):
                    flog.write(' {:>2}:   {}\n'.format(i+1,h[1]) )
          cc = False
          for h in cell[1]:
             if (h[0] == 'cell'):
                cc = True
                flog.write('\n      Complementary cell number :\n')
                break
          if cc:
             for i,h in enumerate(cell[1]):
                if (h[0] == 'cell'):
                    flog.write(' {:>2}:  {:>9}\n'.format(i+1,h[1]) )
          flog.write('\n---------------------------------------------------\n')
       flog.close()

    return cards

if __name__ == '__main__':
    pass

