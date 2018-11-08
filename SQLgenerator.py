#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 22:47:22 2018

@author: csking
"""

from NodeMapper import NodeMapper
import math
import itertools

### class that generates SQL statements from the mapping verified by the user. 




class SQLgenerator:
  
    """
    Start from evaluating the format NN_ON_VN
    
    input: map results after user edit
    output: possible NN_ON_VN format where NN is the attribute node, ON is the operator node and VN is the value node
    
    """
    
    
    
 
    def group_NN_ON_VN(map_result):
        
        ## Rule  NN ON VN 
        perm_NN_ON_VN =[]
        NN_ON_VN = [ x[2] for x in map_result if x[1] == "VN" or x[1] =="NN" or x[1] =="ON" ]
        perm = itertools.permutations(NN_ON_VN ,3)
        for item in list(perm):
            if SQLgenerator.check_node_type(item[0],map_result) == "NN" and SQLgenerator.check_node_type(item[1],map_result) == "ON" and SQLgenerator.check_node_type(item[2],map_result) =="VN":
                perm_NN_ON_VN.append(item)       
        return perm_NN_ON_VN
            
    
    
    """
    Based on the input of possible NN_ON_VN format, choose the valid ones based on mapping results and the operators.
    
    input possible NN_ON_VN formats, the map result
    
    output valid NN_ON_VN results that can be used to connect by operator
    
    """
            
    
    def select_valid_LN(perm_NN_ON_VN,map_result):
        valid = []
        key_words = [ x[2] for x in map_result ]
        n = len([x for x in map_result if x[1] == "LN"])
        print(n)
        selection_c = 2*n
        perm = list(itertools.permutations(perm_NN_ON_VN,selection_c))
        for item in perm:
            key_words_c = key_words.copy()
            boolean = True
            for j in range(len(item)):
                
                if item[j][0] not in key_words_c:
                    boolean = False
                if item[j][1] not in key_words_c:
                    boolean = False
                if item[j][2] not in key_words_c:
                    boolean = False
                if item[j][0] in key_words_c:
                    key_words_c.remove(item[j][0])
                if item[j][1] in key_words_c:
                    key_words_c.remove(item[j][1])
                if item[j][2] in key_words_c:
                    key_words_c.remove(item[j][2])
            if boolean == True:
                valid.append(item)
        return valid
                
    
    """
    connect the NN_ON_VN format based on the operators
    
    input valid NN_ON_VN format
    
    output:  the sql strings in the format  (NN ON VN) LN (NN ON VN)
    
    """
    
    
    
    def connect_LN(valid_LN,map_result):
        sql = []    
        logic = [x[2] for x in map_result if x[1] == "LN"]

        for i in range(len(valid_LN)):
            n = len([x for x in map_result if x[1] == "LN"])
            sql_string = ""
            for j in range(len(valid_LN[0])):
                for m in range(len(valid_LN[0][0])):
                    sql_string +=  valid_LN[i][j][m] + " "
                while n > 0:
                    sql_string += logic[n-1] + " "
                    n = n - 1
            sql.append(sql_string)
        return sql
        
    
    
    """
    Hepler function that returns the type of the node
    
    """
                    
        
    def check_node_type(sql_word,map_result):
        for i in range(len(map_result)):
            if map_result[i][2] == sql_word:
                return map_result[i][1]
            
        
        
    
    """
    evaluate the LN connection based on the score
    
    returns a list of scores of each (NN ON VN) LN (NN ON VN) node 
    

    """
    
    def assign_connect_ln_score(valid_ln_string, map_result, sentence):
        sql_scores = []
        
        for i in range(len(valid_ln_string)):
            score = SQLgenerator.calculate_single_score(valid_ln_string[i],map_result,sentence)
            sql_scores.append([valid_ln_string[i],score])
        
        return sql_scores
            
            
        
         
    """
    
    healper fucntion that checks if word1 is before word2 in the orginal sentence
    return true if word1 is before word2

    """       
    def is_before(sentence,word1,word2):
        sentence_split = sentence.split(" ")
        for i in range(len(sentence_split)):
            if sentence_split.index(word1) < sentence_split.index(word2):
                return True
        
        return False
    
    
    
    
    
    """
    Score function: evaluating an SQL statements by comparing the matching order between the orginal sentence
    and the generated ln_sql results. 

    """        
    
    def calculate_single_score(ln_sql,map_results,sentence):
        dic = {}
        score = 0 
        for i in range(len(map_results)):
            dic[map_results[i][2]] = map_results[i][0]
         
        ln_sql_split = ln_sql.split(' ')
        ln_sql_split =ln_sql_split[:-1]
        for i in range(len(ln_sql_split)):
            for j in range(i,len(ln_sql_split)):
                if i == j:
                    continue
                if SQLgenerator.is_before(sentence,dic[ln_sql_split[i]], dic[ln_sql_split[j]]):
                    score += 1
        return score
                    
    
    
    
    
    """
    1. Generation of the final sql once we decide the (NN ON VN) LN (NN ON VN) in WHERE CLAUSE 
    2. Decide the NN attributes after select by finding a nearest NN node in the orginal sentence
    
    """
    
    def generate_final_sql(sentence,map_results):
        
        selection_NN = SQLgenerator.get_selection_NN(sentence,map_results)
        new_map_results = selection_NN[1]
        NN_ON_VN = SQLgenerator.group_NN_ON_VN(new_map_results)
        LN = SQLgenerator.select_valid_LN(NN_ON_VN , new_map_results)
        connect_ln = SQLgenerator.connect_LN(LN, new_map_results)
        score_list = SQLgenerator.assign_connect_ln_score(connect_ln, new_map_results,sentence)
        where = SQLgenerator.get_highest_score(score_list)
        
        sql = "SELECT " + selection_NN[0][2] + " FROM " + NodeMapper.DB_Name + " WHERE " + where 
        
        return sql
        
        
    """
    helper function to Decide the NN attributes after select by finding a nearest NN node in the orginal sentence
    
    """
    
            
    def get_selection_NN(sentence,map_results):
      
        sentence_split = sentence.split(" ")
        
        NN_Node = [x for x in map_results if x[1] == "NN"]
        
        node = []
        min_index = math.inf
        for i in range(len(NN_Node)):
            index = sentence_split.index(NN_Node[i][0])
            if index < min_index:
                 node = NN_Node[i]
                 min_index = index
        
        map_results.remove(node)
        return (node,map_results) 
                 
                
    """
    helper function to Decide the highest score for a score list of NN ON VN) LN (NN ON VN)
    
    """
                
            
    def get_highest_score(score_list):
        score = 0
        node = []
        for i in range(len(score_list)):
            if score_list[i][1] > score:
                score = score_list[i][1]
                node = score_list[i][0]
        
        return node
                
            


if __name__ == "__main__":
    sentence = "get the authors whose name equal to BOB and age is greater than 38"
    sentence2 ="get the authors whose name equal to BOB"
   
    map_result = NodeMapper.get_final_map(sentence)
    map_result2 = NodeMapper.get_final_map(sentence2)
    print(map_result2)
  #  print(map_result)
   
    
    map_result_after_user_edit = [('authors', 'NN', 'author'),('BOB', 'VN', 'BOB'), ('age', 'NN', 'age'), ('get', 'SN', 'SELECT'), ('and', 'LN', 'AND'), ('greater', 'ON', '>'), ('38', 'VN', '38'),('equal', 'ON', '=') ,('name', 'NN', 'author')]
    
   # a = SQLgenerator.group_NN_ON_VN(map_result_after_user_edit)
  ##  print("group NN ON VN: ",a)
    
    #b = SQLgenerator.select_valid_LN(a, map_result_after_user_edit)
    
    
    #c = SQLgenerator.connect_LN(b,map_result_after_user_edit)
    #print(c)
    #sql = 'age > BOB AND author = 38 '
    #sq2 = 'author = BOB AND age > 38 '
    #d = SQLgenerator.calculate_single_score(sq2,map_result_after_user_edit,sentence)
    #print(d)
    
    #perm = permutations(map_result_after_user_edit)
    
    
   # g = SQLgenerator.assign_connect_ln_score(c,map_result_after_user_edit,sentence)
    #print(g)
    
    
    print(SQLgenerator.generate_final_sql(sentence,map_result_after_user_edit))
 
  #  print(SQLgenerator.get_selection_NN(sentence, map_result_after_user_edit))
    
    
    
    
  #  a = SQLgenerator.check_node_type('BOB', map_result_after_user_edit)
 #   print(a)
  
    
    
    
    
    
    
    
    
    