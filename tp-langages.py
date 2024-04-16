
#!/usr/bin/env python3
"""
Developpez votre projet de TP automates finis dans ce fichier.
"""

from contextfree import StackAutomaton, EPSILON, Grammar
from stack import Stack
import random


def is_deterministic(automaton):
  seen_transitions = set()
  for (source, letter, head, push, target) in automaton.get_transitions():
      if (source, letter, head) in seen_transitions:
          return False
      if (source, EPSILON, head) in seen_transitions:
          return False
      if letter == EPSILON:
          for (source2, letter2, head2) in seen_transitions:
              if source == source2 and head == head2:
                  return False
      seen_transitions.add((source, letter, head))
  return True


def execute(a: StackAutomaton, s: str):
  if not is_deterministic(a) : 
      return False
  stack = Stack()
  stack.push(a.initialstack)
  current_state = a.initialstate
  all_transitions = a.get_transitions()
  
  for char in s :
      transition = False
      for (source, letter, head, push, target) in all_transitions :
          if source == current_state and char == letter and head == stack.top() :
              current_state = target
              stack.pop()
              if push[0] != EPSILON :
                  for x in range(len(push)) :
                      stack.push(push[len(push)-x-1])
              transition = True
              break
      if transition == False :
          return False
  if current_state in a.get_final() :
          return True
      

def is_cnf(grammar):
  for symbol, replace in grammar.ruleList:
      if len(replace) > 2:
          return False
      if len(replace) == 1 and replace[0] not in grammar.get_symbolalphabet():
          return False
      for letter in replace:
          if letter == grammar.axiom or (
              len(replace) == 2 and letter in grammar.get_alphabet()
          ) or (symbol != grammar.axiom and letter == 'EPSILON'):
              return False
  return True

all = Grammar.get_alphabet() + Grammar.get_symbolalphabet()

def generate_symbol(symbol):
  generated_symbol = symbol
  i = 0
  while generated_symbol in all:
      generated_symbol = symbol + i
      i+=1
  return generated_symbol     

def step_1(grammar):
  for symbol, replace in grammar.ruleList:
      if grammar.axiom in replace:
          new_symbol = generate_symbol(grammar.axiom)
          grammar.add_rule(new_symbol, replace)
          grammar.set_axiom(new_symbol)


def step_2(grammar):
  for symbol, replace in grammar.ruleList:
      if len(replace) >= 2:
          list_replace = {}
          new_replace = []
          for  x in replace:
              new_str = ''
              for letter in x :
                   if letter in grammar.get_alphabet() and letter not in list_replace.keys():
                       new_symbol = generate_symbol(letter)
                       list_replace[letter] = new_symbol
                   new_str += list_replace.get(letter, letter)  # Use the replacement if it exists, else use the original letter
              new_replace.append(new_str)
          grammar.remove_rule(symbol, replace)
          grammar.add_rule(symbol, new_replace)
          
def eliminate_unit_productions(grammar):
    changes = True
    while changes:
        changes = False
        new_ruleList = []
        for symbol, replaces in grammar.get_rules():
            new_replaces = []
            for replace in replaces:
                if len(replace) == 1 and replace[0] in grammar.get_symbolalphabet() and replace[0] != symbol:
                    # Expand the unit production
                    for symbol2, replaces2 in grammar.get_rules():
                        if symbol2 == replace[0]:
                            for replace2 in replaces2:
                                if replace2 not in new_replaces:
                                    new_replaces.append(replace2)
                                    changes = True
                else:
                    new_replaces.append(replace)
            new_ruleList.append((symbol, new_replaces))
        grammar.ruleList = new_ruleList



def remove_useless_symbols(grammar):
    generating = set()

    # Find generating symbols
    changes = True
    while changes:
        changes = False
        for symbol, replaces in grammar.get_rules():
            for replace in replaces:
                if all(char in grammar.get_alphabet() or char in generating for char in replace):
                    if symbol not in generating:
                        generating.add(symbol)
                        changes = True

    # Remove non-generating symbols
    grammar.ruleList = [(symbol, replaces) for symbol, replaces in grammar.get_rules() if symbol in generating]

    # Find reachable symbols from the axiom
    reachable = set([grammar.axiom])
    stack = [grammar.axiom]
    while stack:
        current = stack.pop()
        for _, replaces in grammar.ruleList:
            for replace in replaces:
                for char in replace:
                    if char in grammar.get_symbolalphabet() and char not in reachable:
                        reachable.add(char)
                        stack.append(char)

    # Filter rules to keep only reachable symbols
    grammar.ruleList = [(symbol, replaces) for symbol, replaces in grammar.ruleList if symbol in reachable]




def remove_null_productions(grammar):
    nullable = set()
    # Identify nullable non-terminals
    changes = True
    while changes:
        changes = False
        for symbol, replaces in grammar.ruleList:
            for replace in replaces:
                if (not replace or all(sub_symbol in nullable for sub_symbol in replace)) and symbol not in nullable:
                    nullable.add(symbol)
                    changes = True
    
    # Modify productions to account for nullable non-terminals
    new_rules = []
    for symbol, replaces in grammar.ruleList:
        new_replaces = set(replaces)  # Use a set to avoid duplicate productions
        for replace in replaces:
            if replace:
                # Generate all combinations of replacements that exclude nullable symbols
                subsets = [replace[:i] + replace[i+1:] for i in range(len(replace)) if replace[i] in nullable]
                for subset in subsets:
                    if subset or symbol == grammar.axiom:
                        new_replaces.add(tuple(subset))
        new_rules.append((symbol, list(new_replaces)))

    grammar.ruleList = new_rules

    # Remove direct null productions unless it's for the axiom
    grammar.ruleList = [(symbol, [replace for replace in replaces if replace or symbol == grammar.axiom]) 
                        for symbol, replaces in grammar.ruleList]





          
if __name__ == "__main__": # If the module is run from command line, test it
  a=StackAutomaton("aut")
  a.from_txtfile("./tests/automaton1.pa")
  print(execute(a, "a"))
