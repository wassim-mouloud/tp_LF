#!/usr/bin/env python3
"""
Module to represent, build and manipulate finite state automata
"""

from typing import Dict, List, Union, Tuple, Optional
from collections import OrderedDict, Counter # remember order of insertion
import sys
import os.path

########################################################################
########################################################################

def warn(message, *, warntype="WARNING", pos="", **format_args):
  """Print warning message."""
  msg_list = message.format(**format_args).split("\n")
  beg, end = ('\x1b[33m', '\x1b[m') if sys.stderr.isatty() else ('', '')
  if pos: pos += ": "
  for i, msg in enumerate(msg_list):
    warn = warntype if i==0 else " "*len(warntype)
    print(beg, pos, warn, ": ", msg, end, sep="", file=sys.stderr)

##################

def error(message, **kwargs):
    """Print error message and quit."""
    warn(message, warntype="ERROR", **kwargs)
    sys.exit(1)
    
########################################################################
########################################################################

EPSILON = "%" # Constant to represent empty string

########################################################################
########################################################################

class StackAutomaton(object):
  """
  An stack automaton is a list of transitions. A transition is a quintuple (string,string,string,string list,string)
  """  
  name:str
  initialstate:str
  initialstack:str
  finalList:list
  transitionList:list

  
##################  
  
  def __init__(self,name:str)->None:
    self.reset(name)     

##################
    
  def reset(self,name:str=None):
    """
    Reinitialize the automaton with empty content
    """
    self.name = name
    self.initialstate = None
    self.initialstack = None
    self.finalList = []
    self.transitionList = []  

##################
    
  def set_name(self,name:str):
    """
    Change the name of an automaton
    """
    if name == self.name:
        warn("Automaton {aut} already has this name.",aut=self.name)
    else:
        self.name = name

##################
    
  def is_empty(self):
    """
    Checks if an automaton is empty
    """
    return ((self.get_transitions() == []) and (self.initialstate == None) and (self.initialstack == None) and (self.get_final() == []))

##################
      
  def add_transition(self, source:str, letter:chr, head:str, push:list, target:str):
    """
    Add a transition from `source` to `target` on `letter`, popping head of stack 'head' and pushing 'push' onto the stack
    """    
    if ( (source,letter,head,push,target) in self.get_transitions() ):
        warn("Transition: {s} -{a},{A}/{p}-> {t} is already present. Will not add to automaton {aut}.",s=source,a=letter,A=head,p='.'.join(push),t=target,aut=self.name)
    elif len(source)==0 or len(target)==0:
        warn("A state has to be a non-empty string")
    elif len(letter)!=1:
        warn("A terminal symbol has to be a single character")
    else:
      empty_symbol=False
      for symbol in push:
        if len(symbol)==0:
            empty_symbol=True
      if empty_symbol or len(head)==0:
        warn("A stack symbol has to be a non-empty string")

      else:
        self.transitionList.append((source,letter,head,push,target))
        
##################
        
  def remove_transition(self, source:str, letter:chr, head:chr, push:str, target:str):
    """
    Remove a transition from `source` to `target` on `letter`, popping head of stack 'head' and pushing 'push' onto the stack
    """    
    if ( (source,letter,head,push,target) not in self.get_transitions() ):
        warn("Transition: {s} -{a},{A}/{p}-> {t} is already absent. Will not modify automaton {aut}.",s=source,a=letter,A=head,p=push,t=target,aut=self.name)
    else:
        self.transitionList.remove((source,letter,head,push,target))
        
##################

  def make_final(self, state:str):
    """
    Transform a state of the automaton into a final state
    """
    if ( state in self.get_final() ):
        warn("State {s} is already final. Will not modify automaton {aut}.",s=state,aut=self.name)
    else:
        self.finalList.append(state) 
                
##################
        
  def unmake_final(self, state:str):
    """
    Transform a final state of the automaton into a not final state
    """
    if ( state not in self.get_final() ):
        warn("State {s} is already not final. Will not modify automaton {aut}.",s=state,aut=self.name)
    else:
        self.finalList.remove(state)  
                
##################

  def set_initialstate(self, state:str):
    """
    Sets the initial state of the automaton
    """
    if ( state == self.initialstate ):
        warn("State {s} is already initial. Will not modify automaton {aut}.",s=state,aut=self.name)
    else:
        self.initialstate=state

##################

  def set_initialstack(self, symbol: chr):
        """
        Sets the initial stack symbol of the automaton
        """
        if (symbol == self.initialstack):
            warn("Symbol {s} is already initial. Will not modify automaton {aut}.", s=symbol, aut=self.name)
        else:
            self.initialstack = symbol

  ##################

  def get_transitions(self) -> List[Tuple[str,chr,str]]:
    """
    Get the list of transitions of the automaton
    """
    return [x for x in self.transitionList]

##################
    
  def get_final(self) -> str:
    """
    Get a list of the final states of the automaton
    """
    return [x for x in self.finalList] 

##################
    
  def get_states(self) -> List[str]:
    """
    Get a list of states of the automaton
    """
    states=[]
    if (self.initialstate):
        states.append(self.initialstate)
    for (source,letter,head,push,target) in self.get_transitions():
        if source not in states:
            states.append(source)
        if target not in states:
            states.append(target)
    states+=[ x for x in self.get_final() if x not in states]
    return states
    
##################

  def get_alphabet(self,include_epsilon=False)->List[str]:
    """
    Get the letters used in the automaton, not including EPSILON by default
    """
    letters=[]
    epsilon_found=False
    for (source,letter,head,push,target) in self.transitionList:
        if (letter == EPSILON and not epsilon_found):
            epsilon_found=True
        if (letter not in letters and letter != EPSILON):
          letters.append(letter)
    if include_epsilon and epsilon_found:
        letters.append(EPSILON)
    return letters

##################


  def get_stackalphabet(self) -> List[str]:
        """
        Get the symbols used in the stack
        """
        symbols = []
        for (source, letter, head, push, target) in self.transitionList:
            if head not in symbols:
                symbols.append(head)
            for symbol in push:
                if symbol not in symbols:
                    symbols.append(symbol)
        return symbols

##################
    
  def make_copy(self, b):
    """
    Makes a copy of automaton b, but keeps the name
    """
    self.initialstate=b.initialstate
    self.initialstack=b.initialstack
    self.finalList=b.get_final()
    self.transitionList=b.get_transitions()

##################
    
  def transition_string(self)->str:
    """
    Return a string representing the transitions of the automaton
    """
    letters=self.get_alphabet(True)
    symbols=self.get_stackalphabet()
    states=self.get_states()
    res=""
    for state1 in states:
        for letter1 in letters:
            for symbol1 in symbols:
                for state2 in states:
                    for (source,letter,head,push,target) in self.get_transitions():
                        if source==state1 and letter==letter1 and head==symbol1 and target==state2:
                            letterout=letter
                            if letter1=='%':
                                letterout='ɛ'
                            if len(push)==0:
                                out='ɛ'
                            else:
                                out='.'.join(push)
                            res+= source+" -"+letterout+","+head+"/"+out+"-> "+target+"\n"
    
    return res
                	  
##################
    
  def __str__(self)->str:
    """
    Standard function to obtain a string representation of an automaton
    """
    alphabet_no_eps = [ x for x in self.get_alphabet() if x is not EPSILON ]
    tpl = "{A} = <Q={{{Q}}}, Σ={{{S}}}, Z={{{Z}}}, δ, q0={q0}, Z0={Z0}, F={{{F}}}>\nδ =\n{D}"
    return tpl.format(A=self.name, Q=str(",".join(self.get_states())), S=",".join(alphabet_no_eps),Z=",".join(self.get_stackalphabet()), q0=self.initialstate,Z0=self.initialstack, F=",".join(self.get_final()), D=self.transition_string())
    
##################
    
  def to_txtfile(self, outfilename:str=None) -> str:
    """
    Save automaton into txt file.
    """
    res = ""
    if self.initialstate:
        res += "I "+self.initialstate+"\n"
    else:
        res += "I"+"\n"
    res += "F "
    res += " ".join([s for s in self.get_final()])+"\n"
    if self.initialstack:
        res += "S "+self.initialstack
    else:
        res += "S"
    for (source,letter,head,push,target) in self.get_transitions():
        if len(push)==0:
            respush='%'
        else:
            respush='.'.join(push)
        res += "\n{} {} {} {} {}".format(source,letter,head,respush,target)
     
    if outfilename:
      if os.path.isfile(outfilename):
        warn("File {f} already exists, will be overwritten",f=outfilename)
      with open(outfilename,"w") as outfile:
        print(res,file=outfile)
    return res
    
##################

  def from_txt(self, text:str, name:str=None):
    """
    Reads from a txt source string and initializes automaton.
    """
    if not self.is_empty() :
      warn("Automaton {a} not empty: content will be lost",a=self.name)
    self.reset(name)
    rows = text.strip().split("\n")
    if len(rows) < 2:
      error("File must contain at least two lines")
    line1=rows[0].split(" ")
    if not line1[0] == "I":
      error("File must begin with \"I\" ")
    line2=rows[1].split(" ")
    if not line2[0] == "F":
      error("Second line must begin with \"F\" ")
    line3=rows[2].split(" ")
    if not line3[0] == "S":
      error("Third line must begin with \"S\" ")
    if len(line1) > 2:
        error("Only one state can be initial")
    if len(line1) == 2:
        self.initialstate=line1[1]
    if len(line3) > 2:
        error("Only one stack symbol can be initial")
    if len(line3)==2:
        self.initialstack = line3[1]
    line2=line2[1:]
    for state in line2:
        self.finalList.append(state)

    for (i,row) in enumerate(rows[3:]):
      try:
        (source,letter,head,push_dot,target) = row.strip().split(" ")
        if push_dot=='%':
            push=[]
        else:
            push=push_dot.strip().split('.')
        self.add_transition(source,letter,head,push,target)
      except ValueError:
        error("Malformed tuple {t}",pos=name+":"+str(i+1),t=row.strip())
    

##################
    
  def from_txtfile(self, infilename:str):
    """
    Reads from txt file and initializes automaton.
    """    
    try:
      with open(infilename) as infile:
        rows = infile.readlines()
    except FileNotFoundError:
      error("File not found: {f}",f=infilename)
    name = os.path.splitext(os.path.basename(infilename))[0]
    return self.from_txt("".join(rows), name)

########################################################################
########################################################################
class Grammar(object):
    """
    A grammar is a list of rules. A rule a pair (string,string list)
    """
    name: str
    axiom: str
    ruleList: list

    ##################

    def __init__(self, name: str) -> None:
        self.reset(name)

    ##################

    def reset(self, name: str = None):
        """
        Reinitialize the grammar with empty content
        """
        self.name = name
        self.axiom = None
        self.ruleList = []

    ##################

    def set_name(self, name: str):
        """
        Change the name of a grammar
        """
        if name == self.name:
            warn("Grammar {gr} already has this name.", gr=self.name)
        else:
            self.name = name

    ##################

    def is_empty(self):
        """
        Checks if a grammar is empty
        """
        return ((self.get_rules() == []) and (self.axiom == None))

    ##################

    def add_rule(self, symbol: str,  replace: list):
        """
        Add a rule replacing 'symbol' by 'replace'
        """
        if ((symbol,replace) in self.get_rules()):
            warn("Rule: {s} --> {r} is already present. Will not add to grammar {gr}.", s=symbol,
                 r=replace, gr=self.name)
        elif len(symbol) == 0:
            warn("A non-terminal has to be a non-empty string")
        else:
            empty_symbol = False
            for symbol1 in replace:
                if len(symbol1) == 0:
                    empty_symbol = True
            if empty_symbol:
                warn("A non-terminal has to be a non-empty string")

            else:
                self.ruleList.append((symbol,replace))

    ##################

    def remove_rule(self, symbol: str,  replace: list):
        """
        Remove a rule replacing 'symbol' by 'replace'
        """
        if ((symbol, replace) not in self.get_rules()):
            warn("Rule: {s} --> {r} is already absent. Will not modify grammar {gr}.", s=symbol,
                  r=replace, gr=self.name)
        else:
            self.ruleList.remove((symbol,replace))


    def set_axiom(self, symbol: str):
        """
        Sets the initial symbol of the grammar
        """
        if (symbol == self.axiom):
            warn("Symbol {s} is already initial. Will not modify grammar {gr}.", s=symbol, gr=self.name)
        else:
            self.axiom = symbol

    ##################

    def get_rules(self) -> List[Tuple[str, List]]:
        """
        Get the list of rules of the grammar
        """
        return [x for x in self.ruleList]

    ##################

    def get_alphabet(self) -> List[str]:
        """
        Get the letters used in the grammar
        """
        letters = []
        for (symbol, replace) in self.ruleList:
            for symbol1 in replace:
                if len(symbol1)==1 and symbol1.islower() and symbol1 not in letters:
                    letters.append(symbol1)
        return letters

    ##################

    def get_symbolalphabet(self) -> List[str]:
        """
        Get the non-terminal symbols used in the grammar
        """
        symbols = []
        for (symbol,replace) in self.ruleList:
            if symbol not in symbols:
                symbols.append(symbol)
            for symbol1 in replace:
                if (len(symbol1)>1 or not symbol1.islower()) and symbol1 not in symbols:
                    symbols.append(symbol1)
        return symbols

    ##################

    def make_copy(self, b):
        """
        Makes a copy of grammar b, but keeps the name
        """
        self.axiom = b.axiom
        self.ruleList = b.get_rules()

    ##################

    def rules_string(self) -> str:
        """
        Return a string representing the rules of the grammar
        """
        letters = self.get_alphabet()
        symbols = self.get_symbolalphabet()
        res = ""
        for symbol1 in symbols:
                found=False
                for (symbol, replace) in self.get_rules():
                    if symbol == symbol1:
                        if len(replace) == 0:
                            out = 'ɛ'
                        else:
                            out = '.'.join(replace)
                        if not found:
                            res += symbol + " --> " + out
                        else:
                            res += " | "+out
                        found=True
                res+= "\n"

        return res

    ##################

    def __str__(self) -> str:
        """
        Standard function to obtain a string representation of a grammar
        """
        alphabet= [x for x in self.get_alphabet()]
        tpl = "{G} = <Σ={{{S}}}, N={{{N}}}, S={S0}, P>\n P =\n{P}"
        return tpl.format(G=self.name, S=",".join(alphabet),
                          N=",".join(self.get_symbolalphabet()), S0=self.axiom,
                          P=self.rules_string())

    ##################

    def to_txtfile(self, outfilename: str = None) -> str:
        """
        Save grammar into txt file.
        """
        res = ""
        if self.axiom:
            res += "I " + self.axiom
        else:
            res += "I"
        for (symbol,replace) in self.get_rules():
            if len(replace) == 0:
                resreplace = '%'
            else:
                resreplace = '.'.join(replace)
            res += "\n{} {}".format(symbol, resreplace)

        if outfilename:
            if os.path.isfile(outfilename):
                warn("File {f} already exists, will be overwritten", f=outfilename)
            with open(outfilename, "w") as outfile:
                print(res, file=outfile)
        return res

    ##################

    def from_txt(self, text: str, name: str = None):
        """
        Reads from a txt source string and initializes grammar.
        """
        if not self.is_empty():
            warn("Grammar {g} not empty: content will be lost", g=self.name)
        self.reset(name)
        rows = text.strip().split("\n")
        if len(rows) < 1:
            error("File must contain at least one line")
        line1 = rows[0].split(" ")
        if not line1[0] == "I":
            error("File must begin with \"I\" ")

        if len(line1) > 2:
            error("Only one symbol can be initial")
        if len(line1) == 2:
            self.axiom = line1[1]
        for (i, row) in enumerate(rows[1:]):
            try:
                (symbol,replace_dot) = row.strip().split(" ")
                if replace_dot == '%':
                    replace = []
                else:
                    replace = replace_dot.strip().split('.')
                self.add_rule(symbol,replace)
            except ValueError:
                error("Malformed tuple {t}", pos=name + ":" + str(i + 1), t=row.strip())

    ##################

    def from_txtfile(self, infilename: str):
        """
        Reads from txt file and initializes grammar
        """
        try:
            with open(infilename) as infile:
                rows = infile.readlines()
        except FileNotFoundError:
            error("File not found: {f}", f=infilename)
        name = os.path.splitext(os.path.basename(infilename))[0]
        return self.from_txt("".join(rows), name)

########################################################################
########################################################################


if __name__ == "__main__": # If the module is run from command line, test it
    print("Ceci est la bibliothèque contextfree.py")