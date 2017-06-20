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

        msg = None
        budget = random.randint(10000, 50000)

        def _process(self):
            print "BROKER"
            self.msg = self._receive(True)
            if self.msg:
                request = json.loads(self.msg.content)
                if request['request_type'] == 'offer_response':
                    print "msg"

                if request['request_type'] == 'discount_response':
                    print "msg"

                if request['request_type'] == 'booking_confirmed':
                    print "msg"

        def stop_agent(self):
            self.kill()
            sys.exit()

        def broadcast_message(self, content):

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

        def send_message_to_broker(self, content, address):

            agent = spade.AID.aid(name=address, addresses=["xmpp://%s" % address])
            self.msg = ACLMessage()
            self.msg.setPerformative("inform")
            self.msg.setOntology("stock")
            self.msg.setLanguage("eng")
            self.msg.addReceiver(agent)
            self.msg.setContent(content)
            self.myAgent.send(self.msg)
            # print '\nMessage %s sent to %s' % (content, address)

    def _setup(self):
        print "\n Agent\t" + self.getAID().getName() + " is up"

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

    brokers = [1, 2, 3, 4, 5, 6]
    for broker in brokers:
        try:
            threading.Thread(target=start_broker(broker), args=None).start()
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            sys.exit()
        except Exception, e:
            print "\nError while starting broker!"
            print e.message
