#!/usr/bin/env python3.6

import hashlib
import requests
import json

from time import time
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain:

    def __init__(self):
        self.chain = []
        self.current_transaction = []
        self.nodes = set()        
        self.new_block(previous_hash=1, proof=100)


    def new_block(self, proof, previous_hash=None):
        '''Creates a new block and adds it to the chain'''
        
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transaction': self.current_transaction,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transaction = []
        self.chain.append(block)

        return block
        
        

    def new_transaction(self, sender, recipient, amount):
        '''Adds a new transaction to the list of transactions'''

        self.current_transaction.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1


    @property
    def last_block(self):
        '''Returns the last block in the chain'''
        return self.chain[-1]


    @staticmethod
    def hash(block):
        '''Hashes a block'''
        block_string = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()


    def proof_of_work(self, last_proof):
        '''Simple Proof of Work Algorithm'''

        proof = 0

        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof


    @staticmethod
    def valid_proof(last_proof, proof):
        '''Validates the Proof:  Does hash(last_proof, proof) contain 4 leading zeroes?'''

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:2] == "00"

    
    def register_node(self, address):
        '''Add a new node to the list of nodes'''

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    
    def valid_chain(self, chain):
        '''Determine if a given blockchain is valid'''
    
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n--------------\n")

            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True


    def resolve_conflicts(self):
        '''This is our Consensus Algorithm, it resolves conflicts by replacing our chain with the longest one in the network.'''

        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)
        
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

