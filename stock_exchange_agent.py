# coding=utf-8
# !/usr/bin/env python
import json
import random
import string
import sys

import spade
from spade.ACLMessage import ACLMessage
from spade.Agent import Agent
from spade.Behaviour import Behaviour, ACLTemplate


class StockExchange(Agent):
    class OpenStockExchange(Behaviour):

        ip = None
        msg = None
        brokers = 0

        stock = []

        def initialize(self):
            self.ip = self.getName().split(" ")[0]
            self.stock = self.generate_stock()

        def open_stock_exchange(self):
            msg_sign_in_to_stock_exchange = json.dumps(
                {'request_type': 'stock_open',
                 'data': None,
                 'origin': self.ip
                 }
            )

            self.broadcast_message(msg_sign_in_to_stock_exchange)

        def send_stock_exchange_report(self, origin_ip):
            msg_sign_in_to_stock_exchange = json.dumps(
                {'request_type': 'stock_report_data',
                 'data': json.dumps(self.stock),
                 'origin': self.ip
                 }
            )

            self.send_message(msg_sign_in_to_stock_exchange, origin_ip)

        def _process(self):
            self.initialize()
            self.msg = self._receive(True)

            if self.msg:
                request = json.loads(self.msg.content)

                print request
                # Registering brokers to start stock exchange
                if request['request_type'] == 'stock_sign_in':
                    self.brokers += 1

                    # All brokers are registrated
                    if self.brokers == 2:
                        self.open_stock_exchange()

                # Get stock report
                if request['request_type'] == 'stock_report':
                    self.send_stock_exchange_report(request['origin'])

                if request['request_type'] == 'request_two':
                    print "msg"

                if request['request_type'] == 'request_three':
                    print "msg"

                if request['request_type'] == 'request_four':
                    print "msg"

                else:
                    pass

        def broadcast_message(self, message):

            brokers = [1, 3]
            for broker in brokers:
                address = "broker%i@127.0.0.1" % broker
                agent = spade.AID.aid(name=address, addresses=["xmpp://%s" % address])
                self.msg = ACLMessage()
                self.msg.setPerformative("inform")
                self.msg.setOntology("stock")
                self.msg.setLanguage("eng")
                self.msg.addReceiver(agent)
                self.msg.setContent(message)
                self.myAgent.send(self.msg)
                print '\nMessage %s sent to %s' % (message, address)

        def send_message(self, message, address):
            print address

            agent = spade.AID.aid(name=address, addresses=["xmpp://%s" % address])
            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("stock")
            self.msg.setLanguage("eng")
            self.msg.addReceiver(agent)
            self.msg.setContent(message)
            self.myAgent.send(self.msg)
            print '\nMessage %s sent to %s' % (message, address)

        def generate_stock(self):
            result = []
            number_of_stocks = random.randint(10, 20)
            for i in range(0, number_of_stocks):
                result.append(
                    {
                        'name': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3)),
                        'price': random.randint(10, 1000),
                        'numberOfStocks': 10000,
                        'tendency': random.choice(
                            [None, 'up', 'down', 'stale', 'up fast', 'up slow', 'down fast', 'down fast']),
                        'owners': []
                    }
                )

            return result

    def _setup(self):
        print "\nVAS Stock exchange\t%s\tis up" % self.getAID().getAddresses()

        template = ACLTemplate()
        template.setOntology('stock')

        behaviour = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(self.OpenStockExchange(), behaviour)


if __name__ == "__main__":
    try:
        StockExchange('stock@127.0.0.1', 'stock').start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
