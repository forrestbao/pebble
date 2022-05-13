#%%
import stanza

#%%
def print_parsing(bracket_string:str, indent=2):
    indent_level = 0
    prompt = ""
    for c in bracket_string:
        if c == "(":
            # prompt = " "*indent_level*indent
            print (f'\n{indent_level}{prompt}_{c}', end="")
            prompt += " |"
            indent_level += 1
        elif c == ")":
            print (c, end="")
            indent_level -= 1
            prompt = prompt[:-2]
        else: 
            print (c, end="")


#%%
def process_parsing_tree(bracket_string):
    """Return BFS-flattened tree in two dictionaries, for child and parent relations respectively

    The tree: 
        0
    /\
    1  2
    /\  /\
    3 4  5 6

    returns 

    [ # the child relation
        {0:[]},
        {1:[3,4], 2:[5,6]},
        {3:[], 4:[], 5:[], 6:[]},
    ], 

    [ # the parent relation 
        {0:[]},
        {1:0, 2:0},
        {3:1, 4:1, 5:2, 6:2},
    ]
    
    """
    # print (bracket_string)
    level = 0
    child_tree = [{}]
    parent_tree = [{}]
    previous_char = None 
    tag = ""
    path = [] # e.g., [0, 1, 3]
    node_counter = 0 
    node_to_tag = {}

    for c in bracket_string:
        if c == " ":
            continue # TODO: why bug if this is pass? 
        elif c == "(":
            if tag != "":
                node_name = f'{node_counter}_{tag}'
                node_to_tag[node_name] = tag 

                child_tree[level][node_name] = [] 

                if level>0:
                    child_tree[level-1][path[-1]].append(node_name)
                    parent_tree[level][node_name] = path[-1]

                # print (f'Adding {tag} at level {level}, due to (')

                child_tree.append(dict()) # prepare for next level
                parent_tree.append(dict()) # prepare for next level

                tag = ""
                node_counter += 1
                level += 1
                path.append(node_name)

        elif c == ")":
            if previous_char != ")": # this is a token
                node_name = f'{node_counter}_{tag}'
                child_tree[level][node_name] = [] # add the token to dict at tree[level]
                child_tree[level-1][path[-1]].append(node_name)
                parent_tree[level][node_name] = path[-1]

                # print (f'Adding {tag} at level {level} due to )')
                tag = ""
                node_counter += 1
            else:
                level -= 1
                path = path[:-1]
        else: 
            tag += c 

        previous_char = c 

        # print (level, tag, c)


    return child_tree, parent_tree 

# Test case 1 
# bracket_string = "(A (B (D) (E) ) (C (F) (G)))"
# bracket_string = "(A (B (D) (E) ) (C (D) (G)))"
# # bracket_string = "(A(B(D((X)))(E)(H) (C(F)(G(Y(Z(P)))))))"
# print_parsing(bracket_string)
# print ("")
# process_parsing_tree(bracket_string)

# Test case 2

# #%%
# sentence = "通过主控计算机接通开关。"
# stanza_nlp = stanza.Pipeline(lang='zh-hans', processors='tokenize,pos,constituency')
# doc = stanza_nlp(sentence)
# for sent in doc.sentences:
#     bracket_sent = str(sent.constituency)

# print_parsing(str(sent.constituency))
# print (" ")
# child_tree, parent_tree = process_parsing_tree(str(sent.constituency))

# %%

def search_tree(child_tree, parent_tree):
    """Find the true VV based on the BFS travesal of the parsing tree

    Heuristics: 
    A true VV must be under a sequence of VPs, the last VP closer to the root the better  
    """

    # 1. enumerate all paths from a VV back to root
    paths = [] # a tuple of level and nodes 
    for level_counter, level in enumerate(parent_tree): 
        for node, parent in level.items(): 
            if "VV" in node: 
                paths.append([(level_counter, node)])
                level_counter_tmp = int(level_counter) # make a deepcopy
                while parent != "0_ROOT":
                    paths[-1].append( (level_counter_tmp, parent))
                    level_counter_tmp -= 1
                    parent = parent_tree[level_counter_tmp][parent]

    if len(paths) == 0:
        return []

    # Filter 1: At least one VP is needed on the path 
    new_paths = []
    for path in paths: 
        for (level, node) in path: 
            if "VP" in node:
                new_paths.append(path)
                break 
    paths = new_paths

    # Filter 2: Rank paths based on Proximity from VV to VP, keep only the shortest one(s)
    distance_to_VP = {} # first try to rank paths based on distance from VV to closest VP 

    for path_ID, path in enumerate(paths): 
        distance_counter = 1
        (_, VV) = path[0]
        for (VP_level, node) in path[1:]: 
            if "VP" in node: 
                distance_to_VP[(path_ID, VP_level, VV)] = distance_counter # FIXME: should I store VP level or VV level here? 
                break 
            distance_counter += 1 

    # only keep the VV closest to a VP
    if distance_to_VP != {}: 
        # Example exception: there is no VP but not ADVP. So earlier we need to check the tag exactly. # FIXME
        # [{'0_ROOT': ['1_IP']}, {'1_IP': ['2_ADVP', '4_NP', '18_.。']}, {'2_ADVP': ['3_RB然后'], '4_NP': ['5_DNP', '12_``“', '13_NP', "15_''”", '16_NP'], '18_.。': []}, {'3_RB然后': [], '5_DNP': ['6_NP', '11_DEC的'], '12_``“': [], '13_NP': ['14_FWBB'], "15_''”": [], '16_NP': ['17_NN项目']}, {'6_NP': ['7_VV运行', '8_VV主控', '9_VV计算', '10_NN机上'], '11_DEC的': [], '14_FWBB': [], '17_NN项目': []}, {'7_VV运行': [], '8_VV主控': [], '9_VV计算': [], '10_NN机上': []}, {}, {}, {}] 
        minimal_distance_to_VP = min(distance_to_VP.values()) 
    else:
        return None 
    
    paths = [paths[i] for (i, VP_level, VV), distance in distance_to_VP.items() if distance == minimal_distance_to_VP]      

    # print (paths)
    # print (distance_to_VP)

    # Filter 3: distance to root or path length 
    minimal_path_length = min( [len(path) for path in paths])

    # only keep the shortest path     
    paths = [path for path in paths if len(path) == minimal_path_length]
    # for path in paths:
    #     print (path)

    # Filter 4: percentage of VP on the path
    # NOT IN USE NOW 

    # Filter 5 : node ID of VV 
    number_to_token = {}
    for path in paths:
        (VV_level, VV_id_and_tag) = path[0]
        [node_number, tag_and_token] = VV_id_and_tag.split("_")
        token = tag_and_token[2:] # drop VV
        number_to_token[int(node_number)] =  token
    
    final_token =  number_to_token[  list(sorted(number_to_token.keys()))[0]  ]

    # print (final_token)

    return final_token

# %% 
# Test 
# search_tree(child_tree, parent_tree)

# %%
# Feature engineering or running
stanza_nlp = stanza.Pipeline(lang='zh-hans', processors='tokenize,pos,constituency')
lines = open("Chinese_sentences.txt", "r", encoding="utf-8").readlines()

parsing_trees = []
for line in lines: 
    doc = stanza_nlp(line)
    for sent in doc.sentences:
        # # print (sent.text, end=">>>")
        # print_parsing(str(sent.constituency))
        # parsing_trees.append(str(sent.constituency))
        parsing_bracket = str(sent.constituency)
        child_tree, parent_tree = process_parsing_tree(parsing_bracket)
        final_token = search_tree(child_tree, parent_tree)
        print (sent.text, "-->", final_token)


# %%
