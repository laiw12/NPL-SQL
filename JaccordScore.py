#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 16:42:08 2018

@author: csking
"""


"""
calculate the jaccord similarity score

"""


class JaccordScore:
    
    def get_jaccordscore(word1, word2):
        word1_list = []
        word2_list = []
       
        for i in range(len(word1)):
            word1_list.append(word1[i])
        
        for i in range(len(word2)):
            word2_list.append(word2[i])
        
        word1_set = set(word1_list)
        word2_set = set(word2_list)
        
        
        intersect = word1_set.intersection(word2_set)
        union = word1_set.union(word2_set)
       
      
        score = len(intersect)/ len(union)
        
  
        
        return score*(0.5)
    
if __name__ == "__main__":
    word1 = 'author'
    word2 = 'jamse'
    print(JaccordScore.get_jaccordscore(word1,word2))
    
    
                
        
        
                    