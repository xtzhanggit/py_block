from blockchain import Blockchain
from flask import Flask, jsonify, request
#from testwrap import dedent
from uuid import uuid1
import sys

# 实例化此节点
app = Flask(__name__)

# 生成此节点的全局唯一地址
node_identifier = str(uuid1()).replace('-', '')

# 实例化一个区块链
blockchain = Blockchain()

@app.route('/mine', methods = ['GET'])
def mine():
    """
    创建/mine GET接口
    """
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    blockchain.new_transaction(
        sender = "0",  # 发送者为"0"，表示是新挖出的币
        recipient = node_identifier,
        amout = 1
    )
    # 添加新区块到链
    block = blockchain.new_block(proof)
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'proof': block['proof'],
        'transactions': block['transactions'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200
    
    return "We'll mine a new block"

@app.route('/transaction/new', methods = ['POST'])
def new_transaction():
    """
    创建/transaction/new POST接口，可以给接口方发送交易数据
    """
    values = request.get_json()
    required = ['sender', 'recipient', 'amout']
    if not all(k in values for k in required):
        return "Missing values", 400
    # 创建新的交易
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amout'])
    response = {'message': 'Transaction will be added to Block {%d}' % index}
    return jsonify(response), 201

@app.route('/chain', methods = ['GET'])
def full_chain():
    """
    创建/chain 接口，返回整个区块链
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods = ['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)
    response = {
        'message': "New nodes have been added",
        'the_node': nodes,
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods = ['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': "Our chain was replaced",
            'new_chain': blockchain.chain
        }
    else:
        response = { 
            'message': "Our chain is authoritative",
            'new_chain': blockchain.chain
        }
    return jsonify(response), 200

if __name__ == "__main__":
    """
    服务运行在5000端口上
    """
    app.run(host = '0.0.0.0', port = int(sys.argv[1]))
