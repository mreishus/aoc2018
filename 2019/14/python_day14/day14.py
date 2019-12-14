#!/usr/bin/env python
from collections import Counter
from itertools import groupby
import collections


def parse(filename):
    with open(filename) as f:
        return [parse_line(line.strip()) for line in f.readlines()]


Element = collections.namedtuple("Element", "thing quantity")
Rule = collections.namedtuple("Rule", "materials result")


def parse_line(line):
    left, right = line.split(" => ")
    left = parse_elements(left)
    right = parse_elements(right)[0]
    return Rule(left, right)


def parse_elements(string):
    elements = string.split(", ")
    output = []
    for element in elements:
        quantity, thing = element.split(" ")
        output.append(Element(thing, int(quantity)))
    return output


def approx_match(d, elm):
    # We need ELM "28 A"
    # But there is no direct key in d corresponding to "28 A"
    # Find another one like "10 A"
    keys = [k for k, v in d.items() if k.thing == elm.thing]
    # print(f"Found [{keys}]")
    if len(keys) == 0:
        return None

    smaller = [k for k in keys if k.quantity <= elm.quantity]
    larger = [k for k in keys if k.quantity > elm.quantity]
    if len(smaller) > 0:
        return max(smaller, key=lambda x: x.quantity)
    if len(larger) > 0:
        return max(larger, key=lambda x: x.quantity)
    print(
        f"WHAT?? keys[{keys}] smaller[{smaller}] larger[{larger}] elmQ[{elm.quantity}]"
    )


def index_of_first(lst, pred):
    for i, v in enumerate(lst):
        if pred(v):
            return i
    return None


def part2(rules):
    # Manual Binary Search
    try_me = [1_993_284]
    for v in try_me:
        a = part1(rules, v)
        print(f"fuel {v} answer {a} answer {a / 1_000_000_000}")


def part1(rules, initial_fuel=1):
    d = {}
    for rule in rules:
        if rule.result in d:
            raise ValueError("didn't expect to see duplicate rules")
        d[rule.result] = rule.materials

    what_i_need = [Element(thing="FUEL", quantity=initial_fuel)]
    negatives = []
    while True:
        additions = []
        delete_indexes = []

        for i, elm in enumerate(what_i_need):
            # Is there a negative thing (EXTRA)?
            negative_i = index_of_first(negatives, lambda v: v.thing == elm.thing)
            # print(f"neg #{negative_i} #{negatives}  <==> {elm}")

            # Look for exact replacement
            if elm in d:
                # print(f"Using direct replacement.")
                delete_indexes.append(i)
                additions += d[elm]
            elif negative_i != None:
                # Pos: 2 Neg: -3  Result = -1

                # Mark both for deletion
                neg = negatives.pop(negative_i)
                delete_indexes.append(i)

                # Find new amount
                new_amount = neg.quantity + elm.quantity
                new_elm = Element(elm.thing, new_amount)
                if new_amount > 0:
                    additions += [new_elm]
                elif new_amount < 0:
                    negatives.append(new_elm)
            elif approx_match(d, elm):
                # We have an approx match; use_this = 10 A, produces = 10 ORE, but
                # we have say, 14 A (or 8 A!)
                use_this = approx_match(d, elm)
                produces = d[use_this]

                # print(f"Maybe continue? Got this rule:")
                # print(f"  --USE THIS --> [{use_this}] ")
                # print(f"   <--- GET THIS [{produces}]")

                if elm.quantity >= use_this.quantity:
                    # print(f"     ++ This one is safe. Doing it!")
                    # This one is always safe; invoking a rule to transform 10A when we have 14.
                    # times = 1
                    # if elm.quantity % use_this.quantity == 0:
                    times = elm.quantity // use_this.quantity

                    delete_indexes.append(i)
                    new_elm = Element(
                        elm.thing, elm.quantity - (use_this.quantity * times)
                    )
                    if new_elm.quantity > 0:
                        additions += [new_elm]
                    for this_elm in produces:
                        additions += [
                            Element(this_elm.thing, this_elm.quantity * times)
                        ]
                    break
                else:
                    # Actually, not safe/possible, we need to get more, but we will waste some
                    # We only need 8 A but the rule is 10 ORE => 10 A
                    delete_indexes.append(i)
                    additions += produces
                    negatives.append(
                        Element(elm.thing, elm.quantity - use_this.quantity)
                    )
                    # print("")
                    # print(what_i_need)
                    # print(f"  --USE THIS --> [{use_this}] ")
                    # print(f"   <--- GET THIS [{produces}]")
                    # print(f"     -- Hmm.. producing waste.")
                    break
                # else:
                # print(f"     ?? Decided to skip for now.")

        # Process Marked Deletes/Adds
        for i in sorted(delete_indexes, reverse=True):
            what_i_need.pop(i)
        what_i_need += additions

        # Merge Same Types
        merged = []
        for thing, elements in groupby(sorted(what_i_need), key=lambda x: x.thing):
            q = sum(x.quantity for x in elements)
            merged.append(Element(thing=thing, quantity=q))
        what_i_need = merged

        # print("")
        # print("What I need:")
        # print(what_i_need)
        # print("")

        if len(what_i_need) == 1 and what_i_need[0].thing == "ORE":
            break

        # j += 1
        # if j > 10000000:
        #     break
    # print("What I need:")
    # print(what_i_need)
    # print("Negatives:")
    # print(negatives)
    return what_i_need[0].quantity


if __name__ == "__main__":
    rules = parse("../input.txt")
    print("Part1: ")
    print(part1(rules))

    print("Part2: ")
    print(part2(rules))
