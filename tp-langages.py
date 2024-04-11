#!/usr/bin/env python3
"""
Developpez votre projet de TP automates finis dans ce fichier.
"""

from contextfree import StackAutomaton, EPSILON, Grammar
from stack import Stack


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

def execute(a: StackAutomaton, s: str) -> bool:
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
                    for x in push :
                        stack.push(x)
                transition = True
                break
        if transition == False :
            return False
    if current_state in a.get_final() :
            return True
        




if __name__ == "__main__": # If the module is run from command line, test it
    a=StackAutomaton("aut")
    a.from_txtfile("./tests/automaton1.pa")
    print(execute(a, "a"))
