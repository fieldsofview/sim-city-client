'''
Created on 22 Dec 2014

@author: Anatoli Danezi <anatoli.danezi@surfsara.nl>
@helpdesk: Grid Services <grid.support@surfsara.nl>
                                         
usage: python createTokens.py [picas_db_name] [picas_username] [picas_pwd]
description: create 5 tokens with basic fields and a random number for the input field
'''
import simcity_client
import argparse
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Remove all tokens in a view")
    parser.add_argument('view', choices=['todo', 'done', 'locked'], help="View to remove tokens from")
    args = parser.parse_args()
    
    _, db = simcity_client.init()

    is_deleted = db.delete_tokens_from_view('Monitor', args.view)
    print "Deleted", np.sum(is_deleted), "out of", len(is_deleted), "tokens from view", args.view