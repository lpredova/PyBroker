# coding=utf-8
# !/usr/bin/env python
import json
import sys
import random

import spade
from spade.ACLMessage import ACLMessage
from spade.Agent import Agent
from spade.Behaviour import Behaviour, ACLTemplate


class StockExchange(Agent):
    class OpenStockExchange(Behaviour):

        ip = None
        name = None
        msg = None
        brokers = 0

        stock = None

        def initialize(self):
            self.ip = self.getName().split(" ")[0]
            self.name = self.getName().split(" ")[1]

            # generate stocks
            print "initialize"

        def _process(self):
            try:
                self.msg = self._receive(True)

                if self.msg:
                    request = json.loads(self.msg.content)

                    # Registering brokers to start stock exchange
                    if request['request_type'] == 'stock_sign_in':
                        self.brokers += 1

                        # All brokers are registrated
                        if self.brokers == 6:
                            msg_sign_in_to_stock_exchange = json.dumps(
                                {'request_type': 'stock_open',
                                 'data': None,
                                 'origin': self.ip
                                 }
                            )

                            self.broadcast_message(msg_sign_in_to_stock_exchange)

                    # Get stock report
                    if request['request_type'] == 'stock_report':

                        print "msg"

                    if request['request_type'] == 'request_two':
                        print "msg"

                    if request['request_type'] == 'request_three':
                        print "msg"

                    if request['request_type'] == 'request_four':
                        print "msg"

                    else:
                        pass

            except (KeyboardInterrupt, SystemExit):
                self.stop_agent()

        def stop_agent(self):
            self.kill()
            sys.exit()

        def broadcast_message(self, content):

            brokers = [1, 2, 3, 4, 5, 6]
            for broker in brokers:
                address = "broker%i@127.0.0.1" % broker
                agent = spade.AID.aid(name=address, addresses=["xmpp://%s" % address])

                self.msg = ACLMessage()
                self.msg.setPerformative("inform")
                self.msg.setOntology("stock")
                self.msg.setLanguage("eng")
                self.msg.addReceiver(agent)
                self.msg.setContent(content)
                self.myAgent.send(self.msg)
                print '\nMessage %s sent to %s' % (content, address)

        def send_message(self, message):
            client = "broker@127.0.0.1"
            address = "xmpp://" + client
            receiver = spade.AID.aid(name=client, addresses=[address])

            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("stock")
            self.msg.setLanguage("eng")
            self.msg.addReceiver(receiver)
            self.msg.setContent(message)

            self.myAgent.send(self.msg)
            # print "\nMessage sent to: %s !" % client


        def generate_stock(self):

            number_of_stocks = random.randint(10, 20)
            


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
