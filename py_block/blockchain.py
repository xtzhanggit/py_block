import requests
import hashlib
import json
from time import time
from urllib.parse import urlparse

class Blockchain(object):
    """
    Blockchain类用于管理链条、储存交易、加入新块
    """
    def __init__(self):
        """
        区块list，当前交易list，创世区块
        """
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash = 1, proof = 100)
        self.nodes = set()

    def new_block(self, proof, previous_hash = None):
        """
        生成新块
        """ 
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amout):
        """
        方法向列表添加一个交易记录，并返回存储该记录的区块索引（下一个待挖掘出的区块）
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amout': amout
        })
        return self.last_block['index'] + 1  # 最后一个区块的索引+1，下一个区块

    @staticmethod
    def hash(block):
        """
        返回区块的SHA-256的hash值
        """
        block_string = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """
        返回最后一个区块
        """
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        工作量证明
        """    
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = (str(last_proof) + str(proof)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, address):
        """
        添加新节点至nodes集合
        """ 
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        确认参数中的链条是否合法，即：
        1、验证hash
        2、验证proof
        """
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print(last_block)
            print(block)
            print("\n---------------\n")
            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        """
        共识算法解决冲突，使用网络最长的链
        链被取代返回true，否则返回false
        遍历所有的邻居节点，检查其链的有效性，如果发现有效更长的链条，就替换掉自己的链
        """
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        for node in neighbours:
            url = "http://%s/chain" %node
            print(url)
            response = requests.get(url)
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
