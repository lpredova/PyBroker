# coding=utf-8
# !/usr/bin/env python
import json
import sys
import threading
import time

import spade
from spade.ACLMessage import ACLMessage
from spade.Agent import Agent, random
from spade.Behaviour import ACLTemplate, MessageTemplate, Behaviour


class BrokerAgent(Agent):
    class Speculate(Behaviour):

        ip = None
        name = None
        behaviour = None

        msg = None
        budget = None

        myStocks = []

        def initialize(self):
            self.ip = self.getName().split(" ")[0]
            self.budget = random.randint(10000, 50000)
            self.behaviour = random.choice(['risky', 'passive', 'cautious'])

            print 'Agent %s\nBudget: %d' % (self.ip, self.budget)

        def sign_in(self):
            msg_sign_in_to_stock_exchange = json.dumps(
                {'request_type': 'stock_sign_in',
                 'data': None,
                 'origin': self.ip
                 }
            )

            self.send_message_to_stock(msg_sign_in_to_stock_exchange)

        def ask_for_report(self):
            msg_stock_exchange_report = json.dumps(
                {'request_type': 'stock_report',
                 'data': None,
                 'origin': self.ip
                 }
            )
            self.send_message_to_stock(msg_stock_exchange_report)

        def delcate_win(self):
            msg_stock_win = json.dumps(
                {'request_type': 'stock_win',
                 'data': None,
                 'origin': self.ip
                 }
            )

            self.send_message_to_stock(msg_stock_win)

        def _process(self):
            self.initialize()
            self.sign_in()

            self.msg = self._receive(True)
            if self.msg:
                request = json.loads(self.msg.content)

                if request['request_type'] == 'stock_open':
                    self.ask_for_report()

                if request['request_type'] == 'stock_report_data':
                    self.evaluate_stock_state(request['data'])

                if request['request_type'] == 'stock_close':
                    print 'Agent %s stopped trading, Won %d$' % (self.ip, self.budget)
                    self.kill()

        def evaluate_stock_state(self, stock_data):
            print "evaluation stock exchange state"
            print stock_data
            self.delcate_win()

        def send_message_to_agent(self, content):

            # for agency_id in agencies_ids:
            address = "broker%i@127.0.0.1" % 1
            agent = spade.AID.aid(name=address, addresses=["xmpp://%s" % address])

            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("stock")
            self.msg.setLanguage("eng")
            self.msg.addReceiver(agent)
            self.msg.setContent(content)
            self.myAgent.send(self.msg)
            # print '\nMessage %s sent to %s' % (content, address)

        def send_message_to_stock(self, content):
            stock_address = 'stock@127.0.0.1'
            agent = spade.AID.aid(name=stock_address, addresses=["xmpp://%s" % stock_address])
            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("stock")
            self.msg.setLanguage("eng")
            self.msg.addReceiver(agent)
            self.msg.setContent(content)
            self.myAgent.send(self.msg)

    def _setup(self):
        stock_template = ACLTemplate()
        stock_template.setOntology('stock')

        mt = MessageTemplate(stock_template)
        settings = self.Speculate()
        self.addBehaviour(settings, mt)


def start_broker(broker_id):
    try:
        ip = "broker%i@127.0.0.1" % broker_id
        agency_name = "broker%i" % broker_id

        agent = BrokerAgent(ip, agency_name)
        agent.start()

    except Exception, e:
        print e


if __name__ == '__main__':

    brokers = [1]
    for broker in brokers:
        try:
            threading.Thread(target=start_broker(broker), args=None).start()
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            sys.exit()
        except Exception, e:
            print "\nError while starting broker!"
            print e.message
