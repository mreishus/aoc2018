#!/usr/bin/env python
from collections import defaultdict
from os import system
import networkx as nx
import string
import copy
from functools import lru_cache

path_lens_cache = {}


@lru_cache(262_144)
def get_maze(filename, keys_unlocked):
    if len(keys_unlocked) == 0:
        return Maze(filename)

    keys = list(keys_unlocked)
    this_key = keys.pop()

    m_in = get_maze(filename, tuple(keys))
    m = copy.deepcopy(m_in)
    # print(f"{keys} --> {this_key}")
    m.collect_key(this_key)

    return m

# @lru_cache(262_144)
# def get_maze2(filename, keys_unlocked):
#     all_but_last, last = get_maze_args(keys_unlocked)
#     if last == None:
#         return Maze(filename)

#     m_in = get_maze2(filename, tuple(all_but_last))
#     m = copy.deepcopy(m_in)
#     m.collect_key(last)
#     return m

# def get_maze_args(keys_unlocked):
#     all_but_last = None
#     last = None
#     if len(keys_unlocked) == 0:
#         all_but_last = frozenset()
#         last = None
#     elif len(keys_unlocked) == 1:
#         all_but_last = frozenset()
#         last = keys_unlocked[0]
#     else:
#         all_but_last = frozenset(keys_unlocked[:-1])
#         last = keys_unlocked[-1]

#     return all_but_last, last

#     #     maze_cache_key = (frozenset(keys_unlocked[:-1]), keys_unlocked[-1])


class Finder:
    def __init__(self, filename):
        self.filename = filename
        self.cache = {}
        self.maze_cache = {}

    def solve(self):
        # m = Maze(self.filename)
        return self.do_solve([], [])

    def do_solve(self, keys_unlocked, unlock_these):
        # print(f"Do SOLVE [{keys_unlocked}]")

        ######
        m = get_maze(self.filename, tuple(keys_unlocked))
        # print(get_maze.cache_info())
        #######
        # maze_cache_key = ""
        # if len(keys_unlocked) > 1:
        #     maze_cache_key = (frozenset(keys_unlocked[:-1]), keys_unlocked[-1])
        # elif len(unlock_these) == 1:
        #     maze_cache_key = unlock_these[0]

        # if maze_cache_key in self.maze_cache:
        #     # print(f"Cache hit {maze_cache_key}")
        #     m = self.maze_cache[maze_cache_key]
        # else:
        #     m = copy.deepcopy(m_in)
        #     for this_key in unlock_these:
        #         # print(f"Keys unlocked [{keys_unlocked}] Unlocking [{this_key}]")
        #         # print(f"Ask M its unlocked doors {m.unlocked_doors}")
        #         m.collect_key(this_key)
        #     self.maze_cache[maze_cache_key] = m

        # if len(self.maze_cache) > 1000:
        #     # print("Clearing Maze Cache")
        #     self.maze_cache.clear()
        # print(len(self.maze_cache))
        ####

        # print("Accessible keys")
        # print(m.accessible_keys)

        possible_keys = list(m.accessible_keys.keys())
        cache_key = frozenset(possible_keys + [m.hero_loc])
        possible_path_lens = [x for x in list(m.accessible_keys.values())]
        # print(possible_keys)

        if len(possible_keys) == 0:
            return 0
        if cache_key in self.cache:
            return self.cache[cache_key]

        smallest = min(possible_path_lens)
        # print("")
        # print(list(zip(possible_keys, possible_path_lens)))
        # print(smallest)

        candidates = {}
        for next_key, next_steps in zip(possible_keys, possible_path_lens):
            # # Don't know if this skip is valid or not
            # if next_steps > smallest * 7 and len(possible_path_lens) > 5:
            #     print(list(zip(possible_keys, possible_path_lens)))
            #     print("Skipped")
            #     continue
            candidates[next_key] = next_steps + self.do_solve(
                keys_unlocked + [next_key], [next_key]
            )

        answer = min(candidates.values())
        if cache_key in self.cache and self.cache[cache_key] != answer:
            print(f"Cached answer {self.cache[cache_key]} computed {answer}")
        self.cache[cache_key] = answer
        return answer

path_lens_cache = {}
@lru_cache(262_144)
def cache_spl(graph, loc1, loc2, filename):
    cache_key = (loc1, loc2, filename)
    if False and cache_key in path_lens_cache:
        return path_lens_cache[cache_key]

    try:
        result = nx.shortest_path_length(graph, loc1, loc2)
        path_lens_cache[cache_key] = result
        return result
    except nx.NetworkXNoPath:
        if cache_key in path_lens_cache:
            del path_lens_cache[cache_key]
        raise

class Maze:
    """Main module for solving Day01."""

    def __init__(self, filename):
        self.grid = None  # defaultdict(lambda: "?")
        self.filename = filename
        self.unlocked_doors = []
        self.loc_of_door = {}
        self.loc_of_key = {}
        self.hero_loc = complex(-99, -99)
        self.accessible_keys = {}
        self.graph = None
        self.path_lens_cache = {}
        # print("Init")
        self.compute()


    def compute(self):
        # print("Compute")
        if self.grid is None:
            grid, loc_of_door, loc_of_key = self.parse(self.filename)
            self.grid = grid
            self.loc_of_door = loc_of_door
            self.loc_of_key = loc_of_key
        self.graph = self.build_graph()
        self.accessible_keys = self.find_accessible_keys()

    def reset(self):
        self.grid = None
        self.compute()

    def parse(self, filename):
        grid = defaultdict(lambda: "?")
        loc_of_door = {}
        loc_of_key = {}
        location = complex(0, 0)

        with open(filename) as f:
            for line in f:
                for char in line.strip():
                    # print(char)
                    grid[location] = char

                    if char in string.ascii_uppercase:
                        loc_of_door[char] = location
                    if char in string.ascii_lowercase:
                        loc_of_key[char] = location
                    if char == "@":
                        self.hero_loc = location
                    location += complex(1, 0)
                location += complex(0, 1)
                location = complex(0, location.imag)
        return grid, loc_of_door, loc_of_key

    def display(self):
        reals = [c.real for c in self.grid.keys() if self.grid[c] != "?"]
        imags = [c.imag for c in self.grid.keys() if self.grid[c] != "?"]
        # system("clear")
        for y in range(int(min(imags)) - 1, int(max(imags)) + 2):
            for x in range(int(min(reals)) - 1, int(max(reals)) + 2):
                char = self.grid[complex(x, y)]
                print(char, end="")
            print("")

    def valid_char(self, char):
        if char == "?" or char == "#":
            return False
        if char in string.ascii_uppercase and char not in self.unlocked_doors:
            return False
        return True

    def find_accessible_keys(self):
        G = self.graph
        accessible_keys = {}
        for key_name in self.loc_of_key.keys():
            # if key_name == "b":
            #     continue
            # print(f"Hero {self.hero_loc} -> {key_name} {self.loc_of_key[key_name]}")
            try:
                # path = nx.dijkstra_path(G, self.hero_loc, self.loc_of_key[key_name])
                steps_taken = cache_spl(
                    G, self.hero_loc, self.loc_of_key[key_name], self.filename
                )
                # steps_taken = nx.shortest_path_length(
                #     G, self.hero_loc, self.loc_of_key[key_name]
                # )
                accessible_keys[key_name] = steps_taken
            except nx.NetworkXNoPath:
                # print(f"Exception #{key_name}")
                a = 0

        return accessible_keys

    def move_hero(self, location):
        self.grid[self.hero_loc] = "."
        self.grid[location] = "@"
        self.hero_loc = location

    def collect_key(self, key_name):
        if key_name not in string.ascii_lowercase:
            raise ValueError("Expected an uppercase door name")

        # Where is the key and how to get there?
        loc = self.loc_of_key[key_name]
        # path = nx.dijkstra_path(self.graph, self.hero_loc, loc)
        # path = nx.shortest_path(self.graph, self.hero_loc, loc)
        # steps_taken = nx.shortest_path_length(self.graph, self.hero_loc, loc)
        # steps_taken = self.cache_spl(self.graph, self.hero_loc, loc, self.filename)
        steps_taken = self.accessible_keys[key_name]

        # print(f"path {path}")
        # print(f"path2 {path2}")

        # Move hero
        self.move_hero(loc)

        # steps_taken = len(path) - 1

        # Delete key (move_hero took care of the grid)
        del self.loc_of_key[key_name]

        # Unlock door
        door_name = key_name.upper()
        if door_name in self.loc_of_door:
            self.unlock_door(key_name.upper())
        else:
            # print("Unlocking a door that doesn't exist")
            # print(door_name)
            # print(self.loc_of_door)
            self.accessible_keys = self.find_accessible_keys()
            # self.compute()
        return steps_taken

    def unlock_door(self, door_name):
        if door_name not in string.ascii_uppercase:
            raise ValueError("Expected an uppercase door name")

        self.unlocked_doors.append(door_name)
        loc = self.loc_of_door[door_name]
        self.grid[loc] = "."
        del self.loc_of_door[door_name]

        # Rebuild Grid
        location = loc
        self.graph.add_node(location)
        up = location + complex(0, -1)
        down = location + complex(0, 1)
        left = location + complex(-1, 0)
        right = location + complex(1, 0)

        for neighbor in [up, down, left, right]:
            neighbor_char = self.grid[neighbor]
            if self.valid_char(neighbor_char):
                self.graph.add_edge(location, neighbor)
        self.accessible_keys = self.find_accessible_keys()
        # self.compute()

    def build_graph(self):
        G = nx.Graph()

        reals = [c.real for c in self.grid.keys() if self.grid[c] != "?"]
        imags = [c.imag for c in self.grid.keys() if self.grid[c] != "?"]
        for y in range(int(min(imags)) - 1, int(max(imags)) + 2):
            for x in range(int(min(reals)) - 1, int(max(reals)) + 2):
                location = complex(x, y)
                char = self.grid[location]
                if not self.valid_char(char):
                    continue

                G.add_node(location)

                up = location + complex(0, -1)
                down = location + complex(0, 1)
                left = location + complex(-1, 0)
                right = location + complex(1, 0)

                for neighbor in [up, down, left, right]:
                    neighbor_char = self.grid[neighbor]
                    if self.valid_char(neighbor_char):
                        G.add_edge(location, neighbor)

        return G


if __name__ == "__main__":
    # f = Finder("../input.txt")
    # print("Real Part 1")
    # print(f.solve())

    f = Finder("../input_small.txt")
    print("Small: Expect 8")
    print(f.solve())

    f = Finder("../input_86.txt")
    print("Expect 86")
    print(f.solve())

    f = Finder("../input_81.txt")
    print("Expect 81")
    print(f.solve())

    f = Finder("../input_132.txt")
    print("Expect 132")
    print(f.solve())

    f = Finder("../input_136.txt")
    print("Expect 136")
    print(f.solve())

    #############

    # m = Maze("../input_small.txt")
    # m.display()
    # m.build_graph()
    # print(m.loc_of_key)
    # print(m.graph)

    # print("Accessible keys")
    # print(m.accessible_keys)

    # steps = m.collect_key("a")
    # print(f"Steps = {steps}")
    # m.display()

    # steps = m.collect_key("b")
    # print(f"Steps = {steps}")
    # m.display()

    # print("\nAccessible keys")
    # print(m.accessible_keys)

    # m.reset()

    # grid = parse("../input_small.txt")
    # display(grid)
    # print("Part1: ")
    # print(grid)
    # print("Part2: ")

